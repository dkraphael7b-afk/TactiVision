from datetime import date
from sqlalchemy.orm import Session
from modelos import Usuario
from seguranca import gerar_hash

def criar_dados_iniciais():
    from banco_de_dados import SessaoBanco
    banco = SessaoBanco()
    try:
        usuario = banco.query(Usuario).filter(Usuario.email == "demo@tactivision.com").first()
        if not usuario:
            banco.add(Usuario(
                nome="Usuário Demonstração",
                cargo="Analista de Desempenho",
                email="demo@tactivision.com",
                senha=gerar_hash("TactiVision123")
            ))
            banco.commit()
    finally:
        banco.close()

def idade_na_data(data_nascimento, data_referencia):
    idade = data_referencia.year - data_nascimento.year
    if (data_referencia.month, data_referencia.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade
