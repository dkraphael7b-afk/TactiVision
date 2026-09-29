# Validação do MVP TactiVision

Data da revisão: 29/09/2026

## Passada 1 — análise estática

- Todos os arquivos Python foram compilados com `compileall` sem erros de sintaxe.
- Os scripts JavaScript foram verificados com `node --check` sem erros de sintaxe.
- As rotas foram inspecionadas para evitar conflito entre `/atletas/filtro` e `/atletas/{id}`.
- As rotas foram inspecionadas para garantir `/metricas` antes de `/metricas/{atleta_id}`.
- A raiz `/` foi configurada para redirecionar para o login.
- O dashboard HTML passou a exigir sessão antes de ser servido.
- Os arquivos de vídeo deixaram de ser expostos por uma pasta estática pública.
- A leitura do arquivo de vídeo passou a usar uma rota autenticada.
- O upload possui limite de 2 GB, validação de extensão, nome de arquivo sanitizado e gravação em blocos.
- A sessão usa segredo por variável de ambiente quando disponível.
- SQLite ativa chaves estrangeiras.
- `processos_videos.status` possui restrição de valores válidos.
- `metricas_consolidadas` possui `UNIQUE(atleta_id, partida_id)`.

## Passada 2 — integração HTTP e banco

Foi executado um teste integrado usando `FastAPI TestClient` com um adaptador temporário de hash apenas para este ambiente de validação, porque o ambiente de execução da revisão não possuía o pacote `bcrypt` instalado e não havia acesso à internet para instalá-lo.

Foram verificados:

- redirecionamento da raiz;
- carregamento da tela de login;
- bloqueio do dashboard sem autenticação;
- login;
- cadastro de usuário;
- rejeição de e-mail duplicado;
- cadastro de campeonato;
- cadastro de partida;
- cadastro de atleta;
- filtro de atleta;
- erro para partida inexistente;
- upload de vídeo;
- rejeição de extensão incompatível;
- acesso autenticado ao arquivo de vídeo;
- início de processamento;
- tratamento de erro de processamento;
- nova tentativa após erro;
- dashboard autenticado;
- logout;
- bloqueio do dashboard após logout.

Resultado: `FULL_INTEGRATION_OK`.

## Passada 3 — pipeline de tracking

Foi criado um vídeo local de teste e utilizado um adaptador temporário que reproduz a estrutura de objetos retornada pelo Ultralytics para testar a integração do pipeline sem fingir que esse adaptador é a IA real.

Foram verificadas:

- leitura das dimensões e FPS do vídeo;
- amostragem de frames;
- criação de identidades técnicas;
- registro de posição X/Y;
- timestamp em segundos;
- cálculo de velocidade;
- geração de logs;
- regra de dispersão;
- geração de alertas;
- cálculo de distância;
- cálculo de velocidade máxima;
- gravação de métricas consolidadas;
- consulta de resultados.

Resultado: `TRACKING_PIPELINE_MOCK_OK`.

## Verificação do esquema

Foi criado um banco SQLite limpo e confirmada a existência das sete tabelas exigidas:

- `usuarios`
- `campeonatos`
- `partidas`
- `atletas`
- `processos_videos`
- `logs_ia_tracking`
- `metricas_consolidadas`

Também foi confirmada a ativação de `PRAGMA foreign_keys=ON` pela conexão SQLAlchemy.

Resultado: `SCHEMA_OK`.

## Limitação da validação local

O ambiente desta revisão não possuía `bcrypt` nem `ultralytics` instalados e não tinha acesso à internet para instalar as dependências. Por isso, a execução com YOLO/ByteTrack oficiais não foi realizada neste ambiente.

O código de produção continua configurado para usar exatamente `bcrypt`, `Ultralytics YOLO` e `ByteTrack` conforme o `requirements.txt`. O teste de pipeline acima valida a lógica de integração, mas não substitui um teste com o pacote Ultralytics instalado e um vídeo real de partida.

Para a demonstração real, depois de instalar `requirements.txt`, deve ser feito pelo menos um processamento de vídeo real e conferidos `CONCLUIDO`, logs, métricas, alertas e mapa de calor.
