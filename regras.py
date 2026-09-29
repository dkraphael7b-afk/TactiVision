import math
from collections import defaultdict

LIMITE_DISPERSAO = 0.32

def calcular_distancia(ponto_a, ponto_b):
    return math.sqrt((ponto_b[0] - ponto_a[0]) ** 2 + (ponto_b[1] - ponto_a[1]) ** 2)

def calcular_dispersao(posicoes):
    if not posicoes:
        return 0.0
    media_x = sum(p[0] for p in posicoes) / len(posicoes)
    media_y = sum(p[1] for p in posicoes) / len(posicoes)
    return math.sqrt(sum((p[0] - media_x) ** 2 + (p[1] - media_y) ** 2 for p in posicoes) / len(posicoes))

def avaliar_desorganizacao(posicoes):
    return calcular_dispersao(posicoes) > LIMITE_DISPERSAO

def calcular_metricas_por_atleta(registros):
    agrupado = defaultdict(list)
    for registro in registros:
        agrupado[registro.atleta_id].append(registro)
    resultado = {}
    for atleta_id, itens in agrupado.items():
        itens.sort(key=lambda x: x.timestamp_video)
        distancia = 0.0
        velocidade_maxima = 0.0
        for anterior, atual in zip(itens, itens[1:]):
            distancia += calcular_distancia((anterior.pos_x, anterior.pos_y), (atual.pos_x, atual.pos_y))
            velocidade_maxima = max(velocidade_maxima, atual.velocidade_estimada)
        if itens:
            velocidade_maxima = max(velocidade_maxima, max(x.velocidade_estimada for x in itens))
        resultado[atleta_id] = {
            "distancia_total": distancia,
            "velocidade_maxima": velocidade_maxima
        }
    return resultado
