import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from banco_de_dados import criar_banco
from servicos import criar_dados_iniciais

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
VIDEOS_DIR = BASE_DIR / "videos"
RESULTADOS_DIR = BASE_DIR / "resultados"
CHAVE_SESSAO = os.getenv("TACTIVISION_SESSION_SECRET", "tactivision-chave-local-mvp-2026")

@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    VIDEOS_DIR.mkdir(exist_ok=True)
    RESULTADOS_DIR.mkdir(exist_ok=True)
    criar_banco()
    criar_dados_iniciais()
    yield

app = FastAPI(
    title="TactiVision",
    description="Inteligência Artificial para Análise Tática Esportiva",
    version="1.1.0",
    lifespan=ciclo_vida
)

app.add_middleware(
    SessionMiddleware,
    secret_key=CHAVE_SESSAO,
    max_age=60 * 60 * 12,
    same_site="lax",
    https_only=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)

from rotas import router
app.include_router(router)
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
