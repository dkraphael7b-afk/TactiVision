# 1. Documento de Entendimento do Contexto

## Projeto

TactiVision — Inteligência Artificial para Análise Tática Esportiva.

## Problema

O departamento de análise de desempenho de um clube tradicional enfrenta dois problemas principais. O primeiro é a sobrecarga operacional causada pela análise manual de dezenas de horas de vídeos. O segundo é a dificuldade de scouting baseada apenas em observação e intuição, o que pode fazer com que detalhes de movimentação sejam ignorados.

## Persona

O usuário principal é o gestor ou operador da comissão técnica, especialmente profissionais de análise de desempenho.

Esse usuário precisa organizar campeonatos, partidas, atletas e vídeos, acompanhar o processamento e consultar métricas e alertas.

## Solução

O TactiVision recebe vídeos de partidas e transforma parte do conteúdo visual em dados estruturados.

O fluxo é:

1. Login.
2. Cadastro de campeonato.
3. Cadastro de partida.
4. Upload do vídeo.
5. Processamento por YOLO e ByteTrack.
6. Registro de posições e timestamps.
7. Estimativa de velocidade.
8. Consolidação de métricas.
9. Aplicação de regra programada de dispersão.
10. Consulta de resultados, alertas e mapa de posições.

## Papel da IA

A IA é utilizada para detectar pessoas no vídeo e manter IDs técnicos de rastreamento. O ByteTrack acompanha a identidade técnica do objeto ao longo dos frames.

O sistema não afirma que o tracker conhece o nome do jogador. Quando não existe associação manual, o MVP usa identificadores técnicos como `Atleta Técnico #3`.

A IA auxilia a comissão técnica. A interpretação final permanece com o profissional.

## Regra de análise

O MVP possui uma regra explícita de dispersão espacial.

Para cada instante amostrado:

- as posições são normalizadas;
- calcula-se a distância média das posições em relação ao centro;
- a dispersão é comparada com `LIMITE_DISPERSAO`;
- acima do limite, o registro recebe alerta.

A regra é propositalmente simples e explicável. Ela não pretende representar uma definição profissional completa de desorganização tática.

## Banco de dados

O banco relacional mantém:

- usuários;
- campeonatos;
- partidas;
- atletas;
- processos de vídeo;
- logs de tracking;
- métricas consolidadas.

O relacionamento entre atleta e partida nas métricas possui restrição única, evitando duas métricas consolidadas para o mesmo atleta na mesma partida.

## Resultado esperado

O TactiVision reduz o trabalho manual de localizar informações básicas de movimentação e organiza os dados em uma estrutura que pode ser consultada pela comissão técnica.

O MVP é uma base técnica para evoluções como calibração do campo, associação de jogadores por camisa, reconhecimento de equipes, modelos táticos mais sofisticados e processamento distribuído.
