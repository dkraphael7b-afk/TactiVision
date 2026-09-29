# 2. Plano de Negócio — Canvas

## Proposta de valor

Transformar vídeos de partidas em dados estruturados de movimentação para reduzir trabalho manual e apoiar análises técnicas com métricas e alertas explicáveis.

## Segmentos de clientes

- Clubes profissionais.
- Clubes de base.
- Escolas de futebol.
- Centros de treinamento.
- Empresas de scouting.
- Consultorias de análise de desempenho.

## Canais

- Demonstrações presenciais.
- Campeonatos e eventos esportivos.
- Parcerias com clubes.
- LinkedIn e redes profissionais.
- Indicação entre profissionais de análise.
- Prospecção B2B.

## Relacionamento

- Onboarding assistido.
- Suporte técnico.
- Demonstração dos resultados.
- Treinamento da comissão técnica.
- Evolução contínua das regras e modelos.

## Fontes de receita

Uma estratégia possível é SaaS B2B:

- Plano inicial para clubes menores.
- Plano profissional para clubes com maior volume.
- Contrato corporativo personalizado.
- Serviços adicionais de implantação e integração.

Os valores não fazem parte do MVP e devem ser validados com entrevistas e testes de mercado.

## Recursos-chave

- Software TactiVision.
- Modelos de visão computacional.
- Infraestrutura de processamento.
- Equipe de desenvolvimento.
- Conhecimento de análise esportiva.
- Banco de dados e armazenamento de vídeos.

## Atividades-chave

- Desenvolvimento da plataforma.
- Evolução dos modelos de visão.
- Criação e validação de regras táticas.
- Suporte aos clientes.
- Segurança e proteção de dados.
- Processamento e armazenamento.

## Parceiros-chave

- Clubes e escolas de futebol.
- Profissionais de análise de desempenho.
- Fornecedores de GPU/cloud.
- Instituições de ensino.
- Empresas de tecnologia esportiva.

## Estrutura de custos

- Desenvolvimento.
- Infraestrutura de nuvem.
- GPUs para processamento.
- Armazenamento de vídeos.
- Domínio e serviços.
- Suporte.
- Pesquisa e desenvolvimento.

## Viabilidade técnica

O MVP já demonstra a cadeia principal com FastAPI, SQLite, OpenCV, YOLO e ByteTrack. A arquitetura permite migrar o banco para PostgreSQL e substituir o processamento local por workers distribuídos.

## Estimativa de ROI

A avaliação inicial deve comparar:

`horas economizadas por partida × custo/hora da equipe`

contra:

`custo mensal da plataforma + processamento`

Exemplo hipotético, apenas para demonstrar o método:

Se uma equipe gastar 10 horas para encontrar e organizar determinados eventos de uma partida e o sistema reduzir esse esforço para 4 horas, são 6 horas potencialmente economizadas por partida.

Com 8 partidas no mês:

`6 × 8 = 48 horas/mês`

Se o custo interno considerado for R$50/hora:

`48 × R$50 = R$2.400/mês`

Esse valor não é uma promessa comercial nem uma medição real do MVP. Deve ser substituído por dados obtidos com clientes piloto.

## Indicadores para validar o negócio

- Horas economizadas por partida.
- Tempo médio de processamento.
- Número de vídeos processados.
- Número de usuários ativos.
- Retenção mensal.
- Custo por hora de vídeo processado.
- Frequência de uso das métricas.
- Quantidade de análises complementares geradas pela comissão.

## Riscos

- Necessidade de GPU para alto volume.
- Variações de câmera e iluminação.
- Oclusão dos jogadores.
- Necessidade de calibração para métricas físicas.
- Aceitação das regras pela comissão técnica.
- Privacidade e governança dos vídeos.

## Próximos passos

1. Piloto com partidas reais.
2. Calibração do campo.
3. Associação manual e automática de jogadores.
4. Separação por equipes.
5. Métricas físicas em metros e km/h.
6. Regras táticas validadas por analistas.
7. Processamento em nuvem.
