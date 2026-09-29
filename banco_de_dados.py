from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
BANCO_DIR = BASE_DIR / "dados"
BANCO_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{BANCO_DIR / 'tactivision.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def ativar_chaves_estrangeiras(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessaoBanco = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def obter_banco():
    banco = SessaoBanco()
    try:
        yield banco
    finally:
        banco.close()

def criar_banco():
    from modelos import (
        Usuario, Campeonato, Partida, Atleta, ProcessoVideo,
        LogIaTracking, MetricaConsolidada
    )
    Base.metadata.create_all(bind=engine)
