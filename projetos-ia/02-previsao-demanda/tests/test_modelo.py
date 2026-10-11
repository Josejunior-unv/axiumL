import numpy as np
import pandas as pd
import pytest

from demanda.dados import gerar_vendas
from demanda.features import HORIZONTE, construir_features
from demanda.modelo import backtest, cobertura, prever_futuro, resumir, vies, wape


@pytest.fixture(scope="module")
def vendas():
    return gerar_vendas(lojas=2, produtos=3, inicio="2024-01-01", fim="2025-03-31", semente=3)


def test_metricas():
    y = np.array([10, 20, 30])
    assert wape(y, [12, 18, 30]) == pytest.approx(4 / 60)
    assert vies(y, [12, 18, 36]) == pytest.approx(6 / 60)
    assert cobertura(y, [9, 21, 0], [11, 25, 30]) == pytest.approx(2 / 3)


def test_features_nao_vazam_o_futuro(vendas):
    """Bagunçar as vendas a partir da origem não pode mudar nenhuma feature
    dos dias que serão previstos a partir dela."""
    origem = pd.Timestamp("2025-02-01")

    def janela(f):
        return f[(f["data"] >= origem) & (f["data"] < origem + pd.Timedelta(days=HORIZONTE))]

    original = janela(construir_features(vendas))
    adulterada = vendas.copy()
    adulterada.loc[adulterada["data"] >= origem, "vendas"] = 10_000
    alterado = janela(construir_features(adulterada))

    colunas = [c for c in original.columns if c != "vendas"]
    pd.testing.assert_frame_equal(original[colunas], alterado[colunas])


def test_backtest(vendas):
    resultado = backtest(vendas, janelas=2)
    assert resultado["origem"].nunique() == 2
    assert len(resultado) == 2 * HORIZONTE * 6
    assert resultado["data"].max() == vendas["data"].max()
    assert resultado[["gradient_boosting", "p10", "p90"]].notna().all().all()
    tabela = resumir(resultado)
    assert tabela.loc["gradient_boosting", "WAPE"] < tabela.loc["sazonal_ingenuo", "WAPE"]


def test_prever_futuro_usa_promocoes_planejadas(vendas):
    dia = vendas["data"].max() + pd.Timedelta(days=3)
    plano = pd.DataFrame({"data": [dia], "loja": [1], "produto": [1], "promocao": [1]})
    previsao = prever_futuro(vendas, promocoes=plano)

    assert len(previsao) == HORIZONTE * 6
    assert previsao["data"].min() == vendas["data"].max() + pd.Timedelta(days=1)
    assert previsao["promocao"].sum() == 1
    linha = previsao[(previsao["data"] == dia) & (previsao["loja"] == 1) & (previsao["produto"] == 1)]
    assert linha["promocao"].item() == 1
    assert (previsao["p10"] <= previsao["p90"]).all()
