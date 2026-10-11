import numpy as np
import pytest

from fraude.dados import gerar_transacoes
from fraude.features import adicionar_features
from fraude.modelo import (
    DetectorSupervisionado,
    alertas_no_orcamento,
    avaliar,
    pontuacao_regras,
    separar_por_tempo,
)


def test_alertas_no_orcamento():
    marcadas = alertas_no_orcamento(np.array([0.1, 0.9, 0.5, 0.7]), fracao=0.5)
    assert marcadas.tolist() == [False, True, False, True]


def test_avaliar_pontuacao_perfeita():
    y = np.array([0] * 98 + [1, 1])
    pontuacao = y.astype(float)
    valor = np.full(100, 10.0)
    m = avaliar(y, pontuacao, valor, fracao_alertas=0.02)
    assert m["recall_alertas"] == m["precisao_alertas"] == m["valor_fraude_barrado"] == 1.0
    assert m["pr_auc"] == pytest.approx(1.0)


def test_supervisionado_supera_regras():
    df = adicionar_features(gerar_transacoes(clientes=1500, dias=90, taxa_comprometidos=0.06, semente=4))
    treino, teste = separar_por_tempo(df, dias_teste=25)
    assert treino["data_hora"].max() < teste["data_hora"].min()

    modelo = avaliar(teste["fraude"], DetectorSupervisionado().fit(treino).pontuar(teste), teste["valor"])
    regras = avaliar(teste["fraude"], pontuacao_regras(teste), teste["valor"])
    assert modelo["pr_auc"] > regras["pr_auc"]
    assert modelo["pr_auc"] > 0.3
