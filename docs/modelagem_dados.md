# 3. Modelagem de Dados

## Entidades

### USUARIOS
- id PK
- nome
- cargo
- email UNIQUE
- senha

### CAMPEONATOS
- id PK
- nome
- temporada

### PARTIDAS
- id PK
- campeonato_id FK -> CAMPEONATOS.id
- data_partida
- adversario

### ATLETAS
- id PK
- nome
- data_nascimento
- posicao
- clube_atual

### PROCESSOS_VIDEOS
- id PK
- usuario_id FK -> USUARIOS.id
- partida_id FK -> PARTIDAS.id
- video_nome
- video_url
- data_upload
- status

### LOGS_IA_TRACKING
- id PK
- processo_id FK -> PROCESSOS_VIDEOS.id
- atleta_id FK -> ATLETAS.id
- timestamp_video
- pos_x
- pos_y
- velocidade_estimada
- alerta_desorganizacao

### METRICAS_CONSOLIDADAS
- id PK
- atleta_id FK -> ATLETAS.id
- partida_id FK -> PARTIDAS.id
- distancia_total
- velocidade_maxima
- UNIQUE(atleta_id, partida_id)

## Cardinalidades

```text
USUARIOS 1 ───── N PROCESSOS_VIDEOS

CAMPEONATOS 1 ───── N PARTIDAS

PARTIDAS 1 ───── N PROCESSOS_VIDEOS

PROCESSOS_VIDEOS 1 ───── N LOGS_IA_TRACKING

ATLETAS 1 ───── N LOGS_IA_TRACKING

ATLETAS 1 ───── N METRICAS_CONSOLIDADAS

PARTIDAS 1 ───── N METRICAS_CONSOLIDADAS
```

## DER textual

```text
┌─────────────────────┐
│      USUARIOS       │
├─────────────────────┤
│ PK id               │
│ nome                │
│ cargo               │
│ email UNIQUE        │
│ senha               │
└──────────┬──────────┘
           │ 1:N
           ▼
┌─────────────────────────────┐
│      PROCESSOS_VIDEOS       │
├─────────────────────────────┤
│ PK id                       │
│ FK usuario_id               │
│ FK partida_id               │
│ video_nome                  │
│ video_url                   │
│ data_upload                 │
│ status                      │
└──────────┬──────────────────┘
           │ 1:N
           ▼
┌─────────────────────────────┐
│      LOGS_IA_TRACKING       │
├─────────────────────────────┤
│ PK id                       │
│ FK processo_id              │
│ FK atleta_id                │
│ timestamp_video             │
│ pos_x                       │
│ pos_y                       │
│ velocidade_estimada         │
│ alerta_desorganizacao       │
└──────────▲──────────────────┘
           │ N:1
           │
┌──────────┴──────────┐
│       ATLETAS       │
├─────────────────────┤
│ PK id               │
│ nome                │
│ data_nascimento     │
│ posicao             │
│ clube_atual         │
└──────────┬──────────┘
           │ 1:N
           ▼
┌─────────────────────────────┐
│  METRICAS_CONSOLIDADAS      │
├─────────────────────────────┤
│ PK id                       │
│ FK atleta_id                │
│ FK partida_id               │
│ distancia_total             │
│ velocidade_maxima           │
│ UNIQUE(atleta_id, partida)  │
└─────────────────────────────┘

┌─────────────────────┐
│    CAMPEONATOS      │
├─────────────────────┤
│ PK id               │
│ nome                │
│ temporada           │
└──────────┬──────────┘
           │ 1:N
           ▼
┌─────────────────────┐
│      PARTIDAS       │
├─────────────────────┤
│ PK id               │
│ FK campeonato_id    │
│ data_partida        │
│ adversario          │
└──────────┬──────────┘
           │ 1:N
           ├───────────────────────> PROCESSOS_VIDEOS
           │
           └───────────────────────> METRICAS_CONSOLIDADAS
```

## Observação sobre idade

`idade` não é armazenada em ATLETAS. Ela é calculada a partir de `data_nascimento` e da data de referência da consulta. Isso evita idade desatualizada.

## Observação sobre identidade

Um ID técnico do ByteTrack não é um nome de jogador. O MVP cria um registro `Atleta Técnico #X` quando necessário. A associação com o atleta real é uma evolução posterior.
