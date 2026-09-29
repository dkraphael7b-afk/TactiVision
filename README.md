# TactiVision

## Inteligência Artificial para Análise Tática Esportiva

O TactiVision é um MVP funcional de uma plataforma de rastreamento tático por visão computacional. O sistema recebe vídeos de partidas, detecta pessoas com Ultralytics YOLO, rastreia os objetos com ByteTrack, registra posições, estima velocidade, consolida distância e aplica uma regra programada de dispersão espacial para sinalizar possíveis momentos de desorganização.

A IA auxilia a comissão técnica. O sistema não atribui nomes reais aos jogadores automaticamente e não substitui a interpretação profissional.

## Problema

Comissões técnicas gastam muitas horas analisando vídeos manualmente e podem perder detalhes de movimentação durante scouting e análise de adversários.

## Solução

O TactiVision transforma frames de vídeo em registros estruturados de posicionamento e movimentação, permitindo consultar histórico, métricas e alertas explicáveis.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- OpenCV
- Ultralytics YOLO
- ByteTrack
- HTML
- CSS
- JavaScript

A arquitetura usa SQLAlchemy e uma URL de banco configurada em um único módulo, facilitando a futura migração para PostgreSQL.

## Arquitetura

Frontend estático servido pelo FastAPI -> API REST -> serviços e regras -> SQLAlchemy -> SQLite.

O processamento de vídeo ocorre em uma thread de fundo do processo local. O arquivo não é carregado inteiro na memória durante o upload: o backend grava blocos de 1 MB.

## Estrutura

```text
TactiVision/
├── venv/
├── main.py
├── banco_de_dados.py
├── modelos.py
├── schemas.py
├── seguranca.py
├── rastreamento.py
├── regras.py
├── servicos.py
├── rotas.py
├── requirements.txt
├── README.md
├── banco.sql
├── docs/
│   ├── entendimento_contexto.md
│   ├── plano_negocio.md
│   ├── modelagem_dados.md
│   └── pitch.md
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── cadastro.html
│   ├── dashboard.html
│   ├── estilo.css
│   └── script.js
├── videos/
├── resultados/
└── dados/
    └── tactivision.db
```

A `venv` não faz parte do código-fonte e deve permanecer separada dos arquivos do projeto.

## Instalação

Python 3.11 ou 3.12 é recomendado.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No primeiro processamento, o Ultralytics poderá baixar o peso `yolo11n.pt` se ele ainda não estiver disponível localmente. Isso exige internet na primeira execução do modelo.

## Execução

```powershell
python -m uvicorn main:app --reload
```

Sistema:

http://127.0.0.1:8000

A raiz redireciona automaticamente para a tela de login. O caminho direto também funciona:

http://127.0.0.1:8000/frontend/login.html

Documentação:

http://127.0.0.1:8000/docs

## Usuário inicial

O sistema cria automaticamente um usuário local de demonstração:

- E-mail: demo@tactivision.com
- Senha: TactiVision123
- Cargo: Analista de Desempenho

A senha é armazenada como hash bcrypt.

## Como usar

1. Acesse a tela de login.
2. Entre com o usuário de demonstração ou crie uma conta.
3. Cadastre um campeonato.
4. Cadastre uma partida vinculada ao campeonato.
5. Cadastre atletas reais, se desejar manter um cadastro de referência.
6. Na seção Vídeos, selecione a partida e envie MP4, AVI, MOV, MKV ou WEBM.
7. O processo será criado como `PENDENTE`.
8. Clique em `Processar`.
9. O sistema usa YOLO para detectar pessoas e ByteTrack para rastrear IDs técnicos.
10. Os registros são gravados em `logs_ia_tracking`.
11. Métricas consolidadas são gravadas em `metricas_consolidadas`.
12. A seção de alertas mostra registros gerados pela regra de dispersão.
13. O botão `Resultado` desenha um mapa de calor usando os dados reais armazenados.
14. O arquivo de vídeo não é exposto por uma pasta pública: a rota `/videos/{id}/arquivo` exige autenticação.

## Regra de desorganização

O arquivo `regras.py` possui a constante:

```python
LIMITE_DISPERSAO = 0.32
```

Para cada frame amostrado, as posições normalizadas dos objetos rastreados são reunidas. Calcula-se a dispersão espacial em relação ao centro médio. Quando a dispersão ultrapassa o limite, os registros daquele instante recebem `alerta_desorganizacao = true`.

Essa regra é demonstrativa. Ela não representa uma definição tática profissional definitiva.

## Identidade dos jogadores

YOLO e ByteTrack identificam objetos tecnicamente dentro do vídeo. O tracker não sabe automaticamente o nome real de cada jogador. Por isso, quando uma nova identidade técnica aparece, o MVP cria um registro como `Atleta Técnico #X`, com posição `NÃO ASSOCIADO`.

Esse registro pode posteriormente ser associado manualmente a um atleta real em uma evolução do produto.

## Métricas

O MVP registra:

- posição X e Y normalizadas;
- timestamp em segundos;
- velocidade estimada em unidades normalizadas por segundo;
- distância acumulada em unidades normalizadas;
- velocidade máxima;
- quantidade de registros;
- quantidade de alertas.

Como não há calibração automática do campo em metros, distância e velocidade são relativas à imagem. Não devem ser interpretadas como km/h ou metros percorridos sem uma etapa futura de calibração.

## Filtros

A API permite filtrar atletas por:

- campeonato;
- idade;
- posição;
- clube;
- partida.

A idade é calculada com a data de nascimento e a data de referência atual. Não existe campo fixo `idade` na tabela.

## Tratamento de erros

Erros de autenticação, IDs inexistentes, duplicidade de e-mail, formatos de arquivo incompatíveis e falhas de processamento retornam respostas HTTP apropriadas.

Se o processamento falhar, o processo recebe status `ERRO` e o restante da aplicação continua disponível.

## Limitações do MVP

- O processamento é local e consome CPU/GPU conforme a instalação do OpenCV/Ultralytics.
- O modelo não identifica jogadores reais por nome. ByteTrack fornece apenas uma identidade técnica dentro do vídeo.
- A distância e a velocidade são relativas à imagem enquanto não houver homografia/calibração.
- A regra de dispersão é demonstrativa e considera as pessoas detectadas no vídeo, sem separar automaticamente equipes.
- O processamento em thread local não é indicado para produção distribuída.
- A sessão usa `TACTIVISION_SESSION_SECRET` quando definida; o valor padrão existe apenas para facilitar a demonstração local e deve ser substituído em produção.
- O armazenamento de vídeos é local; produção deveria usar armazenamento de objetos.
- O banco padrão é SQLite; PostgreSQL é recomendado para produção.
- O MVP não possui RBAC avançado, fila distribuída, multi-clube ou auditoria completa.

## Teste manual

### Autenticação
- Abrir login.
- Criar usuário.
- Fazer login.
- Recarregar dashboard.
- Sair.
- Tentar acessar `/usuario` sem sessão.

### Dados
- Criar campeonato.
- Criar partida.
- Criar atleta.
- Conferir os itens nas respectivas seções.

### Vídeo
- Enviar um vídeo compatível.
- Conferir status PENDENTE.
- Iniciar processamento.
- Conferir PROCESSANDO e depois CONCLUIDO ou ERRO.
- Abrir Resultado.

### IA
- Conferir quantidade de jogadores técnicos.
- Conferir logs via `/videos/{id}`.
- Conferir métricas.
- Conferir alertas.
- Conferir mapa de posições.

## Git

Exemplo de fluxo:

```powershell
git init
git add .
git commit -m "feat: cria MVP do TactiVision"
git branch -M main
git remote add origin URL_DO_REPOSITORIO
git push -u origin main
```

Não versionar `venv/`, `dados/tactivision.db`, vídeos de demonstração, pesos grandes do modelo e arquivos temporários.
