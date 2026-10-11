import numpy as np
import pytest
from sklearn.model_selection import train_test_split

from churn.dados import gerar_clientes
from churn.modelo import ENTRADAS, avaliar, candidatos, limiar_otimo, lucro_campanha


@pytest.fixture(scope="module")
def base():
    df = gerar_clientes(2500, semente=11)
    return train_test_split(df[ENTRADAS], df["churn"], test_size=0.3, random_state=0,
                            stratify=df["churn"])


@pytest.mark.parametrize("nome", ["regressao_logistica", "gradient_boosting"])
def test_modelos_aprendem_sinal(base, nome):
    X_treino, X_teste, y_treino, y_teste = base
    pipeline = candidatos()[nome].fit(X_treino, y_treino)
    prob = pipeline.predict_proba(X_teste)[:, 1]
    assert avaliar(y_teste.to_numpy(), prob)["roc_auc"] > 0.75


def test_lucro_campanha_conta_certo():
    y = np.array([1, 0, 1, 0])
    prob = np.array([0.9, 0.8, 0.2, 0.1])
    valor = np.array([1000.0, 1000.0, 1000.0, 1000.0])
    # aciona os dois primeiros: ganha 0.3 * 1000 de um churn real, paga 2 ofertas
    assert lucro_campanha(y, prob, valor, 0.5, custo_oferta=100, taxa_sucesso=0.3) == pytest.approx(100.0)
    assert lucro_campanha(y, prob, valor, 0.95) == 0.0


def test_limiar_otimo_separa_classes():
    y = np.array([1] * 10 + [0] * 90)
    prob = np.concatenate([np.full(10, 0.8), np.full(90, 0.1)])
    valor = np.full(100, 2000.0)
    limiar, lucro = limiar_otimo(y, prob, valor)
    assert 0.1 < limiar <= 0.8
    assert lucro == pytest.approx(10 * (0.30 * 2000 - 120))
