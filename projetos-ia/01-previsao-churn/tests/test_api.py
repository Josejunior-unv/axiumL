import pytest
from fastapi.testclient import TestClient

from churn.dados import gerar_clientes
from churn.modelo import ENTRADAS, candidatos


@pytest.fixture(scope="module")
def cliente_http():
    df = gerar_clientes(1500, semente=5)
    pipeline = candidatos()["regressao_logistica"].fit(df[ENTRADAS], df["churn"])
    from churn.api import criar_app

    app = criar_app({"pipeline": pipeline, "limiar": 0.4, "modelo": "regressao_logistica"})
    return TestClient(app)


CLIENTE = {
    "contrato": "mensal",
    "internet": "fibra",
    "pagamento": "boleto",
    "regiao": "Sudeste",
    "meses_cliente": 2,
    "idade": 25,
    "dependentes": 0,
    "streaming": True,
    "mensalidade": 129.9,
    "total_gasto": 259.8,
    "chamados_suporte": 5,
    "atrasos_pagamento": 2,
}


def test_saude(cliente_http):
    assert cliente_http.get("/saude").json()["status"] == "ok"


def test_cliente_de_risco_aciona_retencao(cliente_http):
    resposta = cliente_http.post("/prever", json=CLIENTE)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["probabilidade_churn"] > 0.7
    assert corpo["acionar_retencao"] is True


def test_cliente_fiel_nao_aciona(cliente_http):
    fiel = CLIENTE | {"contrato": "bianual", "internet": "dsl", "pagamento": "debito_automatico",
                      "meses_cliente": 60, "total_gasto": 5000.0, "chamados_suporte": 0,
                      "atrasos_pagamento": 0, "dependentes": 2}
    assert cliente_http.post("/prever", json=fiel).json()["acionar_retencao"] is False


def test_valida_entrada(cliente_http):
    assert cliente_http.post("/prever", json=CLIENTE | {"contrato": "vitalicio"}).status_code == 422
