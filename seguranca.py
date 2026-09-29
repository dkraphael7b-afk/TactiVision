import bcrypt
from fastapi import HTTPException, Request

def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False

def exigir_usuario(request: Request) -> int:
    usuario_id = request.session.get("usuario_id")
    if not isinstance(usuario_id, int) or usuario_id <= 0:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    return usuario_id
