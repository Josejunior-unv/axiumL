"""Modelos, métricas e backtest com origem móvel."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from demanda.features import CATEGORICAS, HORIZONTE, colunas_modelo, construir_features

QUANTIS = (0.1, 0.9)


def wape(y, previsao) -> float:
    """Erro absoluto ponderado: soma dos erros / soma das vendas."""
    return float(np.abs(np.asarray(y) - np.asarray(previsao)).sum() / np.asarray(y).sum())


def vies(y, previsao) -> float:
    """Positivo = previsão acima do realizado."""
    return float((np.asarray(previsao) - np.asarray(y)).sum() / np.asarray(y).sum())


def cobertura(y, inferior, superior) -> float:
    y = np.asarray(y)
    return float(((y >= np.asarray(inferior)) & (y <= np.asarray(superior))).mean())


def _boosting(**kwargs) -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=400,
        max_leaf_nodes=31,
        min_samples_leaf=40,
        categorical_features=CATEGORICAS,
        random_state=0,
        **kwargs,
    )


class ModeloDemanda:
    """Gradient boosting global (uma árvore para todas as séries) com perda
    Poisson para a previsão pontual e perda quantílica para o intervalo de 80%."""

    def fit(self, features: pd.DataFrame) -> ModeloDemanda:
        self.colunas = colunas_modelo(features)
        X, y = features[self.colunas], features["vendas"]
        self.pontual = _boosting(loss="poisson").fit(X, y)
        self.quantis = {q: _boosting(loss="quantile", quantile=q).fit(X, y) for q in QUANTIS}
        return self

    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        X = features[self.colunas]
        inferior, superior = (self.quantis[q].predict(X) for q in QUANTIS)
        return pd.DataFrame(
            {
                "previsao": self.pontual.predict(X),
                "p10": np.clip(inferior, 0, None),
                "p90": np.clip(superior, 0, None),
            },
            index=features.index,
        )


def _apto_para_treino(features: pd.DataFrame) -> pd.Series:
    return features["vendas"].notna() & features["lag_56"].notna()


def backtest(vendas: pd.DataFrame, janelas: int = 3, horizonte: int = HORIZONTE) -> pd.DataFrame:
    """Reproduz `janelas` previsões passadas de `horizonte` dias cada.

    Para cada origem, o modelo treina só com o que existia antes dela e prevê
    os `horizonte` dias seguintes. Devolve uma linha por (dia, loja, produto)
    previsto, com o realizado e a previsão de cada método.
    """
    features = construir_features(vendas, horizonte)
    fim = features["data"].max()
    resultados = []
    for i in reversed(range(janelas)):
        origem = fim - pd.Timedelta(days=horizonte * (i + 1) - 1)
        limite = origem + pd.Timedelta(days=horizonte)
        treino = features[(features["data"] < origem) & _apto_para_treino(features)]
        teste = features[(features["data"] >= origem) & (features["data"] < limite)]

        previsto = ModeloDemanda().fit(treino).predict(teste)
        resultados.append(
            pd.DataFrame(
                {
                    "origem": origem,
                    "data": teste["data"],
                    "loja": teste["loja"],
                    "produto": teste["produto"],
                    "vendas": teste["vendas"],
                    "sazonal_ingenuo": teste["lag_28"],
                    "media_4_semanas": teste["media_mesmo_dia_semana"],
                    "gradient_boosting": previsto["previsao"],
                    "p10": previsto["p10"],
                    "p90": previsto["p90"],
                }
            )
        )
    return pd.concat(resultados, ignore_index=True)


METODOS = ["sazonal_ingenuo", "media_4_semanas", "gradient_boosting"]


def resumir(resultado: pd.DataFrame) -> pd.DataFrame:
    """Tabela de métricas por método no backtest inteiro."""
    linhas = []
    for metodo in METODOS:
        y, p = resultado["vendas"], resultado[metodo]
        linhas.append(
            {
                "metodo": metodo,
                "WAPE": wape(y, p),
                "MAE": float(np.abs(y - p).mean()),
                "vies": vies(y, p),
            }
        )
    return pd.DataFrame(linhas).set_index("metodo")


def prever_futuro(
    vendas: pd.DataFrame,
    horizonte: int = HORIZONTE,
    promocoes: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Treina com todo o histórico e prevê os próximos `horizonte` dias.

    `promocoes` (opcional) tem colunas data, loja, produto, promocao com o
    calendário promocional planejado. Sem ele, assume que não haverá promoção.
    """
    ultimo_dia = vendas["data"].max()
    futuras = pd.date_range(ultimo_dia + pd.Timedelta(days=1), periods=horizonte, freq="D")
    series = vendas[["loja", "produto"]].drop_duplicates()
    futuro = series.merge(pd.DataFrame({"data": futuras}), how="cross")
    futuro["promocao"] = 0
    if promocoes is not None:
        planejado = futuro.drop(columns="promocao").merge(
            promocoes, on=["data", "loja", "produto"], how="left"
        )
        futuro["promocao"] = planejado["promocao"].fillna(0).astype(int).to_numpy()
    futuro["vendas"] = np.nan

    features = construir_features(pd.concat([vendas, futuro], ignore_index=True), horizonte)
    treino = features[_apto_para_treino(features)]
    alvo = features[features["data"] > ultimo_dia]
    previsto = ModeloDemanda().fit(treino).predict(alvo)
    return pd.concat([alvo[["data", "loja", "produto", "promocao"]], previsto], axis=1)
