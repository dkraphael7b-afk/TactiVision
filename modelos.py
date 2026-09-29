from datetime import date, datetime
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from banco_de_dados import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    processos_videos: Mapped[list["ProcessoVideo"]] = relationship(back_populates="usuario")

class Campeonato(Base):
    __tablename__ = "campeonatos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    temporada: Mapped[str] = mapped_column(String(30), nullable=False)
    partidas: Mapped[list["Partida"]] = relationship(back_populates="campeonato", cascade="all, delete-orphan")

class Partida(Base):
    __tablename__ = "partidas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campeonato_id: Mapped[int] = mapped_column(ForeignKey("campeonatos.id"), nullable=False)
    data_partida: Mapped[date] = mapped_column(Date, nullable=False)
    adversario: Mapped[str] = mapped_column(String(150), nullable=False)
    campeonato: Mapped["Campeonato"] = relationship(back_populates="partidas")
    processos_videos: Mapped[list["ProcessoVideo"]] = relationship(back_populates="partida", cascade="all, delete-orphan")
    metricas: Mapped[list["MetricaConsolidada"]] = relationship(back_populates="partida", cascade="all, delete-orphan")

class Atleta(Base):
    __tablename__ = "atletas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    posicao: Mapped[str] = mapped_column(String(50), nullable=False)
    clube_atual: Mapped[str] = mapped_column(String(150), nullable=False)
    logs_tracking: Mapped[list["LogIaTracking"]] = relationship(back_populates="atleta")
    metricas: Mapped[list["MetricaConsolidada"]] = relationship(back_populates="atleta")

class ProcessoVideo(Base):
    __tablename__ = "processos_videos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"), nullable=False)
    video_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    data_upload: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDENTE")
    usuario: Mapped["Usuario"] = relationship(back_populates="processos_videos")
    partida: Mapped["Partida"] = relationship(back_populates="processos_videos")
    logs_tracking: Mapped[list["LogIaTracking"]] = relationship(back_populates="processo", cascade="all, delete-orphan")
    __table_args__ = (CheckConstraint("status IN ('PENDENTE','PROCESSANDO','CONCLUIDO','ERRO')", name="ck_status_processo"),)

class LogIaTracking(Base):
    __tablename__ = "logs_ia_tracking"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processo_id: Mapped[int] = mapped_column(ForeignKey("processos_videos.id"), nullable=False)
    atleta_id: Mapped[int] = mapped_column(ForeignKey("atletas.id"), nullable=False)
    timestamp_video: Mapped[float] = mapped_column(Float, nullable=False)
    pos_x: Mapped[float] = mapped_column(Float, nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, nullable=False)
    velocidade_estimada: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    alerta_desorganizacao: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    processo: Mapped["ProcessoVideo"] = relationship(back_populates="logs_tracking")
    atleta: Mapped["Atleta"] = relationship(back_populates="logs_tracking")

class MetricaConsolidada(Base):
    __tablename__ = "metricas_consolidadas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    atleta_id: Mapped[int] = mapped_column(ForeignKey("atletas.id"), nullable=False)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"), nullable=False)
    distancia_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    velocidade_maxima: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    atleta: Mapped["Atleta"] = relationship(back_populates="metricas")
    partida: Mapped["Partida"] = relationship(back_populates="metricas")
    __table_args__ = (UniqueConstraint("atleta_id", "partida_id", name="uq_atleta_partida"),)
