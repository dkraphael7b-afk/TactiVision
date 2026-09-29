from datetime import date
import cv2
from sqlalchemy.orm import Session
from modelos import Atleta, LogIaTracking, MetricaConsolidada
from regras import avaliar_desorganizacao, calcular_metricas_por_atleta

MODELO_YOLO = "yolo11n.pt"
FPS_AMOSTRAGEM = 5


def processar_video(caminho_video: str, processo, banco: Session):
    try:
        from ultralytics import YOLO
    except ImportError as erro:
        raise RuntimeError("Ultralytics não está instalado") from erro

    modelo = YOLO(MODELO_YOLO)
    video = cv2.VideoCapture(caminho_video)
    if not video.isOpened():
        raise RuntimeError("Não foi possível abrir o vídeo")
    fps_video = video.get(cv2.CAP_PROP_FPS) or 30.0
    largura = video.get(cv2.CAP_PROP_FRAME_WIDTH) or 1.0
    altura = video.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1.0
    video.release()
    intervalo = max(1, int(round(fps_video / FPS_AMOSTRAGEM)))
    ultimo_ponto = {}
    atletas_tecnicos = {}
    frame_index = 0

    resultados = modelo.track(
        source=caminho_video,
        stream=True,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[0],
        verbose=False
    )

    try:
        for resultado in resultados:
            if frame_index % intervalo != 0:
                frame_index += 1
                continue
            timestamp = frame_index / fps_video
            ids = resultado.boxes.id
            if ids is None:
                frame_index += 1
                continue
            caixas = resultado.boxes.xyxy.cpu().tolist()
            ids_lista = ids.int().cpu().tolist()
            posicoes_frame = []
            dados_frame = []
            for caixa, track_id in zip(caixas, ids_lista):
                x1, y1, x2, y2 = caixa
                x_centro = max(0.0, min(1.0, ((x1 + x2) / 2) / largura))
                y_centro = max(0.0, min(1.0, ((y1 + y2) / 2) / altura))
                posicoes_frame.append((x_centro, y_centro))
                if track_id not in atletas_tecnicos:
                    atleta = Atleta(
                        nome=f"Atleta Técnico #{track_id}",
                        data_nascimento=date(2000, 1, 1),
                        posicao="NÃO ASSOCIADO",
                        clube_atual="Não informado"
                    )
                    banco.add(atleta)
                    banco.flush()
                    atletas_tecnicos[track_id] = atleta.id
                atleta_id = atletas_tecnicos[track_id]
                velocidade = 0.0
                if track_id in ultimo_ponto:
                    ponto_anterior, tempo_anterior = ultimo_ponto[track_id]
                    delta_tempo = max(timestamp - tempo_anterior, 0.001)
                    velocidade = calcular_velocidade(ponto_anterior, (x_centro, y_centro), delta_tempo)
                ultimo_ponto[track_id] = ((x_centro, y_centro), timestamp)
                dados_frame.append((atleta_id, x_centro, y_centro, velocidade))
            alerta = avaliar_desorganizacao(posicoes_frame)
            for atleta_id, x_centro, y_centro, velocidade in dados_frame:
                banco.add(LogIaTracking(
                    processo_id=processo.id,
                    atleta_id=atleta_id,
                    timestamp_video=timestamp,
                    pos_x=x_centro,
                    pos_y=y_centro,
                    velocidade_estimada=velocidade,
                    alerta_desorganizacao=alerta
                ))
            if frame_index % (intervalo * 20) == 0:
                banco.commit()
            frame_index += 1

        banco.commit()
        registros = banco.query(LogIaTracking).filter(LogIaTracking.processo_id == processo.id).all()
        metricas = calcular_metricas_por_atleta(registros)
        for atleta_id, valores in metricas.items():
            existente = banco.query(MetricaConsolidada).filter(
                MetricaConsolidada.atleta_id == atleta_id,
                MetricaConsolidada.partida_id == processo.partida_id
            ).first()
            if existente:
                existente.distancia_total = valores["distancia_total"]
                existente.velocidade_maxima = valores["velocidade_maxima"]
            else:
                banco.add(MetricaConsolidada(
                    atleta_id=atleta_id,
                    partida_id=processo.partida_id,
                    distancia_total=valores["distancia_total"],
                    velocidade_maxima=valores["velocidade_maxima"]
                ))
        banco.commit()
    finally:
        try:
            resultados.close()
        except Exception:
            pass


def calcular_velocidade(ponto_anterior, ponto_atual, delta_tempo):
    distancia = ((ponto_atual[0] - ponto_anterior[0]) ** 2 + (ponto_atual[1] - ponto_anterior[1]) ** 2) ** 0.5
    return distancia / delta_tempo
