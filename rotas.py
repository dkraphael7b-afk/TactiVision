from datetime import datetime
from pathlib import Path
from threading import Lock, Thread
import re
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import Integer, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from banco_de_dados import obter_banco, SessaoBanco
from modelos import Usuario, Campeonato, Partida, Atleta, ProcessoVideo, LogIaTracking, MetricaConsolidada
from rastreamento import processar_video
from schemas import UsuarioCriacao, LoginDados, CampeonatoCriacao, PartidaCriacao, AtletaCriacao
from seguranca import exigir_usuario, gerar_hash, verificar_senha
from servicos import idade_na_data

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
VIDEOS_DIR = BASE_DIR / "videos"
EXTENSOES_PERMITIDAS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
TAMANHO_MAXIMO_VIDEO = 2 * 1024 * 1024 * 1024
PROCESSAMENTOS_ATIVOS = set()
PROCESSAMENTOS_LOCK = Lock()


def limpar_nome_arquivo(nome):
    nome = Path(nome or "video").name
    nome = re.sub(r"[^A-Za-z0-9._-]", "_", nome)
    return nome[:180] or "video"


def limpar_resultado_anterior(processo_id, banco):
    processo = banco.query(ProcessoVideo).filter(ProcessoVideo.id == processo_id).first()
    if not processo:
        return
    atleta_ids = [x[0] for x in banco.query(LogIaTracking.atleta_id).filter(LogIaTracking.processo_id == processo_id).distinct().all()]
    banco.query(LogIaTracking).filter(LogIaTracking.processo_id == processo_id).delete(synchronize_session=False)
    for atleta_id in atleta_ids:
        atleta = banco.query(Atleta).filter(Atleta.id == atleta_id).first()
        if atleta and atleta.nome.startswith("Atleta Técnico #"):
            if not banco.query(LogIaTracking).filter(LogIaTracking.atleta_id == atleta_id).first():
                banco.query(MetricaConsolidada).filter(MetricaConsolidada.atleta_id == atleta_id).delete(synchronize_session=False)
                banco.delete(atleta)
    banco.commit()


def rodar_processamento(processo_id):
    banco = SessaoBanco()
    try:
        processo = banco.query(ProcessoVideo).filter(ProcessoVideo.id == processo_id).first()
        if not processo:
            return
        processo.status = "PROCESSANDO"
        banco.commit()
        caminho = VIDEOS_DIR / Path(processo.video_url).name
        try:
            processar_video(str(caminho), processo, banco)
            processo = banco.query(ProcessoVideo).filter(ProcessoVideo.id == processo_id).first()
            if processo:
                processo.status = "CONCLUIDO"
                banco.commit()
        except Exception:
            banco.rollback()
            try:
                limpar_resultado_anterior(processo_id, banco)
            except Exception:
                banco.rollback()
            processo = banco.query(ProcessoVideo).filter(ProcessoVideo.id == processo_id).first()
            if processo:
                processo.status = "ERRO"
                banco.commit()
    finally:
        banco.close()
        with PROCESSAMENTOS_LOCK:
            PROCESSAMENTOS_ATIVOS.discard(processo_id)


@router.get("/frontend/dashboard.html", include_in_schema=False)
def pagina_dashboard(request: Request):
    exigir_usuario(request)
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@router.get("/", include_in_schema=False)
def pagina_inicial():
    return RedirectResponse(url="/frontend/login.html", status_code=307)


@router.get("/saude", include_in_schema=False)
def saude():
    return {"sistema": "TactiVision", "status": "ok"}


@router.post("/usuarios")
def criar_usuario(dados: UsuarioCriacao, banco: Session = Depends(obter_banco)):
    email = str(dados.email).lower()
    if banco.query(Usuario).filter(func.lower(Usuario.email) == email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    usuario = Usuario(nome=dados.nome, cargo=dados.cargo, email=email, senha=gerar_hash(dados.senha))
    banco.add(usuario)
    try:
        banco.commit()
        banco.refresh(usuario)
    except IntegrityError:
        banco.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    return {"id": usuario.id, "mensagem": "Usuário criado com sucesso"}


@router.post("/login")
def login(dados: LoginDados, request: Request, banco: Session = Depends(obter_banco)):
    usuario = banco.query(Usuario).filter(func.lower(Usuario.email) == str(dados.email).lower()).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    request.session.clear()
    request.session["usuario_id"] = usuario.id
    return {"mensagem": "Login realizado", "usuario": {"id": usuario.id, "nome": usuario.nome, "cargo": usuario.cargo}}


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"mensagem": "Logout realizado"}


@router.get("/usuario")
def usuario_atual(request: Request, banco: Session = Depends(obter_banco)):
    usuario_id = exigir_usuario(request)
    usuario = banco.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return {"id": usuario.id, "nome": usuario.nome, "cargo": usuario.cargo, "email": usuario.email}


@router.post("/campeonatos")
def criar_campeonato(dados: CampeonatoCriacao, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    campeonato = Campeonato(nome=dados.nome, temporada=dados.temporada)
    banco.add(campeonato)
    banco.commit()
    banco.refresh(campeonato)
    return {"id": campeonato.id, "nome": campeonato.nome, "temporada": campeonato.temporada}


@router.get("/campeonatos")
def listar_campeonatos(request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    campeonatos = banco.query(Campeonato).options(joinedload(Campeonato.partidas)).order_by(Campeonato.id.desc()).all()
    return [{"id": c.id, "nome": c.nome, "temporada": c.temporada, "partidas": len(c.partidas)} for c in campeonatos]


@router.post("/partidas")
def criar_partida(dados: PartidaCriacao, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    if not banco.query(Campeonato).filter(Campeonato.id == dados.campeonato_id).first():
        raise HTTPException(status_code=404, detail="Campeonato não encontrado")
    partida = Partida(campeonato_id=dados.campeonato_id, data_partida=dados.data_partida, adversario=dados.adversario)
    banco.add(partida)
    banco.commit()
    banco.refresh(partida)
    return {"id": partida.id, "data_partida": partida.data_partida, "adversario": partida.adversario}


@router.get("/partidas")
def listar_partidas(request: Request, campeonato_id: int | None = None, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    consulta = banco.query(Partida).options(joinedload(Partida.campeonato), joinedload(Partida.processos_videos), joinedload(Partida.metricas))
    if campeonato_id is not None:
        consulta = consulta.filter(Partida.campeonato_id == campeonato_id)
    return [{
        "id": p.id,
        "campeonato_id": p.campeonato_id,
        "campeonato": p.campeonato.nome,
        "data_partida": p.data_partida,
        "adversario": p.adversario,
        "videos": len(p.processos_videos),
        "metricas": len(p.metricas)
    } for p in consulta.order_by(Partida.data_partida.desc()).all()]


@router.get("/partidas/{id}")
def obter_partida(id: int, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    partida = banco.query(Partida).options(joinedload(Partida.campeonato), joinedload(Partida.processos_videos), joinedload(Partida.metricas)).filter(Partida.id == id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return {
        "id": partida.id,
        "campeonato_id": partida.campeonato_id,
        "campeonato": partida.campeonato.nome,
        "data_partida": partida.data_partida,
        "adversario": partida.adversario,
        "videos": [{"id": v.id, "nome": v.video_nome, "status": v.status} for v in partida.processos_videos],
        "metricas": [{"atleta_id": m.atleta_id, "distancia_total": m.distancia_total, "velocidade_maxima": m.velocidade_maxima} for m in partida.metricas]
    }


@router.post("/atletas")
def criar_atleta(dados: AtletaCriacao, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    atleta = Atleta(**dados.model_dump())
    banco.add(atleta)
    banco.commit()
    banco.refresh(atleta)
    return {"id": atleta.id, "nome": atleta.nome}


@router.get("/atletas")
def listar_atletas(request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    atletas = banco.query(Atleta).order_by(Atleta.nome).all()
    return [serializar_atleta(a, banco) for a in atletas]


@router.get("/atletas/filtro")
def filtrar_atletas(
    request: Request,
    campeonato_id: int | None = None,
    idade: int | None = None,
    posicao: str | None = None,
    clube: str | None = None,
    partida_id: int | None = None,
    banco: Session = Depends(obter_banco)
):
    exigir_usuario(request)
    if idade is not None and not 0 <= idade <= 120:
        raise HTTPException(status_code=400, detail="Idade inválida")
    if partida_id is not None and not banco.query(Partida).filter(Partida.id == partida_id).first():
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    if campeonato_id is not None and not banco.query(Campeonato).filter(Campeonato.id == campeonato_id).first():
        raise HTTPException(status_code=404, detail="Campeonato não encontrado")
    data_referencia = datetime.now().date()
    if partida_id:
        data_referencia = banco.query(Partida.data_partida).filter(Partida.id == partida_id).scalar()
    atletas = banco.query(Atleta).order_by(Atleta.nome).all()
    resultado = []
    for atleta in atletas:
        metricas = banco.query(MetricaConsolidada).filter(MetricaConsolidada.atleta_id == atleta.id)
        if partida_id:
            metricas = metricas.filter(MetricaConsolidada.partida_id == partida_id)
        if campeonato_id:
            metricas = metricas.join(Partida).filter(Partida.campeonato_id == campeonato_id)
        if (partida_id or campeonato_id) and not metricas.first():
            continue
        idade_calculada = idade_na_data(atleta.data_nascimento, data_referencia)
        if idade is not None and idade_calculada != idade:
            continue
        if posicao and atleta.posicao.casefold() != posicao.strip().casefold():
            continue
        if clube and atleta.clube_atual.casefold() != clube.strip().casefold():
            continue
        resultado.append(serializar_atleta(atleta, banco, data_referencia))
    return resultado


@router.get("/atletas/{id}")
def obter_atleta(id: int, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    atleta = banco.query(Atleta).filter(Atleta.id == id).first()
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    return serializar_atleta(atleta, banco)


@router.post("/videos")
async def enviar_video(
    request: Request,
    partida_id: int = Form(...),
    arquivo: UploadFile = File(...),
    banco: Session = Depends(obter_banco)
):
    usuario_id = exigir_usuario(request)
    partida = banco.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    extensao = Path(arquivo.filename or "").suffix.lower()
    if extensao not in EXTENSOES_PERMITIDAS:
        raise HTTPException(status_code=400, detail="Formato de vídeo incompatível")
    nome_original = limpar_nome_arquivo(arquivo.filename)
    nome_seguro = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{nome_original}"
    destino = VIDEOS_DIR / nome_seguro
    tamanho = 0
    try:
        with destino.open("wb") as saida:
            while bloco := await arquivo.read(1024 * 1024):
                tamanho += len(bloco)
                if tamanho > TAMANHO_MAXIMO_VIDEO:
                    raise HTTPException(status_code=413, detail="Vídeo excede o limite de 2 GB")
                saida.write(bloco)
    except HTTPException:
        destino.unlink(missing_ok=True)
        raise
    except OSError as erro:
        destino.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Não foi possível salvar o vídeo") from erro
    finally:
        await arquivo.close()
    processo = ProcessoVideo(
        usuario_id=usuario_id,
        partida_id=partida_id,
        video_nome=arquivo.filename or nome_original,
        video_url=f"videos/{nome_seguro}",
        status="PENDENTE"
    )
    banco.add(processo)
    try:
        banco.commit()
        banco.refresh(processo)
    except Exception:
        banco.rollback()
        destino.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Não foi possível registrar o vídeo")
    return {"id": processo.id, "status": processo.status, "video_nome": processo.video_nome}


@router.get("/videos")
def listar_videos(request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    videos = banco.query(ProcessoVideo).options(joinedload(ProcessoVideo.partida), joinedload(ProcessoVideo.usuario)).order_by(ProcessoVideo.id.desc()).all()
    return [{
        "id": v.id,
        "nome": v.video_nome,
        "partida": f"{v.partida.data_partida} x {v.partida.adversario}",
        "usuario": v.usuario.nome,
        "data_upload": v.data_upload,
        "status": v.status
    } for v in videos]


@router.get("/videos/{id}/arquivo")
def obter_arquivo_video(id: int, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    processo = banco.query(ProcessoVideo).filter(ProcessoVideo.id == id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    caminho = VIDEOS_DIR / Path(processo.video_url).name
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado")
    extensao = caminho.suffix.lower()
    tipos = {".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime", ".avi": "video/x-msvideo", ".mkv": "video/x-matroska"}
    return FileResponse(caminho, media_type=tipos.get(extensao, "application/octet-stream"), filename=limpar_nome_arquivo(processo.video_nome))


@router.get("/videos/{id}")
def obter_video(id: int, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    processo = banco.query(ProcessoVideo).options(joinedload(ProcessoVideo.partida)).filter(ProcessoVideo.id == id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    resumo = banco.query(
        LogIaTracking.atleta_id,
        func.count(LogIaTracking.id),
        func.sum(func.cast(LogIaTracking.alerta_desorganizacao, Integer))
    ).filter(LogIaTracking.processo_id == id).group_by(LogIaTracking.atleta_id).all()
    atletas = {
        atleta_id: {"atleta_id": atleta_id, "registros": registros, "alertas": alertas or 0}
        for atleta_id, registros, alertas in resumo
    }
    logs = banco.query(LogIaTracking).filter(LogIaTracking.processo_id == id).order_by(desc(LogIaTracking.timestamp_video), desc(LogIaTracking.id)).limit(2000).all()
    logs.reverse()
    return {
        "id": processo.id,
        "nome": processo.video_nome,
        "status": processo.status,
        "partida_id": processo.partida_id,
        "partida": f"{processo.partida.data_partida} x {processo.partida.adversario}",
        "video_url": f"/videos/{processo.id}/arquivo",
        "jogadores_rastreados": list(atletas.values()),
        "logs": [{
            "atleta_id": l.atleta_id,
            "timestamp_video": l.timestamp_video,
            "pos_x": l.pos_x,
            "pos_y": l.pos_y,
            "velocidade_estimada": l.velocidade_estimada,
            "alerta_desorganizacao": l.alerta_desorganizacao
        } for l in logs[-2000:]]
    }


@router.post("/videos/{id}/processar")
def iniciar_processamento(id: int, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    processo = banco.query(ProcessoVideo).filter(ProcessoVideo.id == id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    with PROCESSAMENTOS_LOCK:
        if id in PROCESSAMENTOS_ATIVOS or processo.status == "PROCESSANDO":
            raise HTTPException(status_code=409, detail="Vídeo já está sendo processado")
        if processo.status == "CONCLUIDO":
            raise HTTPException(status_code=409, detail="Vídeo já foi processado")
        if processo.status not in {"PENDENTE", "ERRO"}:
            raise HTTPException(status_code=409, detail="Status de processamento inválido")
        if processo.status == "ERRO":
            limpar_resultado_anterior(id, banco)
        PROCESSAMENTOS_ATIVOS.add(id)
    try:
        processo.status = "PROCESSANDO"
        banco.commit()
    except Exception:
        banco.rollback()
        with PROCESSAMENTOS_LOCK:
            PROCESSAMENTOS_ATIVOS.discard(id)
        raise HTTPException(status_code=500, detail="Não foi possível iniciar o processamento")
    Thread(target=rodar_processamento, args=(id,), daemon=True).start()
    return {"mensagem": "Processamento iniciado", "status": "PROCESSANDO"}


@router.get("/metricas")
def listar_metricas(request: Request, partida_id: int | None = None, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    consulta = banco.query(MetricaConsolidada).options(joinedload(MetricaConsolidada.atleta), joinedload(MetricaConsolidada.partida))
    if partida_id is not None:
        consulta = consulta.filter(MetricaConsolidada.partida_id == partida_id)
    return [{
        "id": m.id,
        "atleta_id": m.atleta_id,
        "atleta": m.atleta.nome,
        "partida_id": m.partida_id,
        "partida": f"{m.partida.data_partida} x {m.partida.adversario}",
        "distancia_total": m.distancia_total,
        "velocidade_maxima": m.velocidade_maxima
    } for m in consulta.order_by(MetricaConsolidada.id.desc()).all()]


@router.get("/metricas/{atleta_id}")
def metricas_atleta(atleta_id: int, request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    if not banco.query(Atleta).filter(Atleta.id == atleta_id).first():
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    return [{
        "partida_id": m.partida_id,
        "distancia_total": m.distancia_total,
        "velocidade_maxima": m.velocidade_maxima
    } for m in banco.query(MetricaConsolidada).filter(MetricaConsolidada.atleta_id == atleta_id).all()]


@router.get("/alertas")
def listar_alertas(request: Request, processo_id: int | None = None, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    consulta = banco.query(LogIaTracking).options(joinedload(LogIaTracking.atleta), joinedload(LogIaTracking.processo)).filter(LogIaTracking.alerta_desorganizacao.is_(True))
    if processo_id is not None:
        consulta = consulta.filter(LogIaTracking.processo_id == processo_id)
    return [{
        "id": a.id,
        "atleta": a.atleta.nome,
        "video_id": a.processo_id,
        "video": a.processo.video_nome,
        "timestamp_video": a.timestamp_video,
        "mensagem": "Dispersão espacial acima do limite configurado"
    } for a in consulta.order_by(LogIaTracking.timestamp_video, LogIaTracking.id).all()]


@router.get("/dashboard")
def dashboard(request: Request, banco: Session = Depends(obter_banco)):
    exigir_usuario(request)
    return {
        "campeonatos": banco.query(func.count(Campeonato.id)).scalar() or 0,
        "partidas": banco.query(func.count(Partida.id)).scalar() or 0,
        "atletas": banco.query(func.count(Atleta.id)).scalar() or 0,
        "videos": banco.query(func.count(ProcessoVideo.id)).scalar() or 0,
        "videos_processados": banco.query(func.count(ProcessoVideo.id)).filter(ProcessoVideo.status == "CONCLUIDO").scalar() or 0,
        "videos_pendentes": banco.query(func.count(ProcessoVideo.id)).filter(ProcessoVideo.status.in_(["PENDENTE", "PROCESSANDO"])).scalar() or 0,
        "alertas": banco.query(func.count(LogIaTracking.id)).filter(LogIaTracking.alerta_desorganizacao.is_(True)).scalar() or 0
    }


def serializar_atleta(atleta, banco, data_referencia=None):
    data_referencia = data_referencia or datetime.now().date()
    idade = idade_na_data(atleta.data_nascimento, data_referencia)
    metricas = banco.query(MetricaConsolidada).filter(MetricaConsolidada.atleta_id == atleta.id).all()
    return {
        "id": atleta.id,
        "nome": atleta.nome,
        "data_nascimento": atleta.data_nascimento,
        "idade": idade,
        "posicao": atleta.posicao,
        "clube_atual": atleta.clube_atual,
        "metricas": [{
            "partida_id": m.partida_id,
            "distancia_total": m.distancia_total,
            "velocidade_maxima": m.velocidade_maxima
        } for m in metricas]
    }
