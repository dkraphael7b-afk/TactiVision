PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(120) NOT NULL,
    cargo VARCHAR(100) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS campeonatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(150) NOT NULL,
    temporada VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campeonato_id INTEGER NOT NULL,
    data_partida DATE NOT NULL,
    adversario VARCHAR(150) NOT NULL,
    FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id)
);

CREATE TABLE IF NOT EXISTS atletas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(150) NOT NULL,
    data_nascimento DATE NOT NULL,
    posicao VARCHAR(50) NOT NULL,
    clube_atual VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS processos_videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    partida_id INTEGER NOT NULL,
    video_nome VARCHAR(255) NOT NULL,
    video_url VARCHAR(500) NOT NULL,
    data_upload DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL CHECK(status IN ('PENDENTE','PROCESSANDO','CONCLUIDO','ERRO')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (partida_id) REFERENCES partidas(id)
);

CREATE TABLE IF NOT EXISTS logs_ia_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processo_id INTEGER NOT NULL,
    atleta_id INTEGER NOT NULL,
    timestamp_video FLOAT NOT NULL,
    pos_x FLOAT NOT NULL,
    pos_y FLOAT NOT NULL,
    velocidade_estimada FLOAT NOT NULL,
    alerta_desorganizacao BOOLEAN NOT NULL,
    FOREIGN KEY (processo_id) REFERENCES processos_videos(id),
    FOREIGN KEY (atleta_id) REFERENCES atletas(id)
);

CREATE TABLE IF NOT EXISTS metricas_consolidadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    atleta_id INTEGER NOT NULL,
    partida_id INTEGER NOT NULL,
    distancia_total FLOAT NOT NULL,
    velocidade_maxima FLOAT NOT NULL,
    UNIQUE(atleta_id, partida_id),
    FOREIGN KEY (atleta_id) REFERENCES atletas(id),
    FOREIGN KEY (partida_id) REFERENCES partidas(id)
);
