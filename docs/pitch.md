# 5. Pitch Final — 3 a 5 minutos

## 0:00 — Problema

Imagine uma comissão técnica com horas de vídeos de partidas para analisar.

Hoje, encontrar movimentações específicas, medir deslocamentos e localizar momentos de possível desorganização pode exigir muito trabalho manual.

Além disso, no scouting, pequenos detalhes podem ser perdidos quando a análise depende somente da observação.

## 0:35 — Solução

Esse é o TactiVision.

Uma plataforma de inteligência esportiva que transforma vídeos de partidas em dados de movimentação.

O fluxo é simples:

vídeo → visão computacional → tracking → métricas → regras → alertas.

A proposta não é substituir o profissional.

É entregar informação organizada para que ele consiga analisar melhor.

## 1:10 — Demonstração

Primeiro, fazemos login.

Depois, no dashboard, temos uma visão geral de campeonatos, partidas, atletas, vídeos e alertas.

Criamos um campeonato e uma partida.

Na área de vídeos, enviamos a gravação da partida.

O processo começa como PENDENTE e pode ser iniciado pelo operador.

## 1:50 — IA

Agora entra a parte central.

Usamos Ultralytics YOLO para detectar pessoas.

Depois utilizamos ByteTrack para acompanhar as identidades técnicas ao longo dos frames.

Cada registro guarda:

- posição X;
- posição Y;
- timestamp em segundos;
- velocidade estimada;
- referência ao atleta técnico.

É importante destacar que o tracker não sabe automaticamente o nome do jogador.

Por isso, o MVP trabalha com identificadores técnicos até que exista uma associação manual.

## 2:30 — Regra de desorganização

Não queremos uma IA criando alertas sem explicação.

O TactiVision possui uma regra programada.

A cada instante, calculamos a dispersão espacial dos jogadores rastreados.

Se a dispersão ultrapassar um limite configurado, o sistema registra um possível alerta de desorganização.

Assim, a comissão consegue entender de onde veio o alerta.

Essa regra é demonstrativa e não representa uma conclusão tática definitiva.

## 3:00 — Banco e histórico

Todos os dados importantes ficam em um banco relacional.

Temos usuários, campeonatos, partidas, atletas, processos de vídeo, logs de tracking e métricas consolidadas.

Também podemos filtrar atletas por campeonato, idade, posição, clube e partida.

A idade não fica gravada como um número fixo. Ela é calculada usando a data de nascimento e a data da partida ou referência.

## 3:30 — Mapa e negócio

No resultado, o mapa de posições é construído com os dados reais coletados durante o processamento.

Isso permite visualizar onde os objetos rastreados estiveram.

O modelo de negócio pode seguir SaaS B2B, atendendo clubes, escolas, centros de treinamento e empresas de scouting.

A principal proposta de valor é reduzir trabalho operacional e organizar informação para decisões profissionais.

## 4:10 — Encerramento

O TactiVision transforma uma tarefa manual e dispersa em um fluxo estruturado de análise.

A visão computacional encontra os objetos.

O tracking acompanha a movimentação.

O banco preserva o histórico.

As regras tornam os alertas explicáveis.

E a comissão técnica continua responsável pela interpretação.

Esse é o TactiVision.
