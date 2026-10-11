"""Features para previsão direta com horizonte de até 28 dias.

Todas as variáveis que olham o histórico de vendas usam defasagem de pelo
menos `HORIZONTE` dias. Assim um único modelo serve para prever qualquer dia
das próximas 4 semanas sem usar informação que ainda não existiria no momento
da previsão. Promoções e feriados entram porque são planejados com antecedência.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from demanda.dados import eventos_calendario

HORIZONTE = 28
LAGS = [28, 35, 42, 49, 56, 364]
CATEGORICAS = ["loja", "produto"]


def construir_features(df: pd.DataFrame, horizonte: int = HORIZONTE) -> pd.DataFrame:
    """Recebe colunas data, loja, produto, promocao, vendas (NaN nos dias a prever).

    Cada série precisa ter todos os dias, sem buracos, para os lags baterem.
    """
    if min(LAGS) < horizonte:
        raise ValueError("todo lag precisa ser >= horizonte")

    df = df.sort_values(["loja", "produto", "data"]).reset_index(drop=True)
    chaves = [df["loja"], df["produto"]]
    vendas = df.groupby(chaves, sort=False)["vendas"]

    for k in LAGS:
        df[f"lag_{k}"] = vendas.shift(k)

    deslocada = vendas.shift(horizonte).groupby(chaves, sort=False)
    for janela in (7, 28, 91):
        df[f"media_{janela}"] = deslocada.transform(
            lambda s, j=janela: s.rolling(j, min_periods=1).mean()
        )
    df["desvio_28"] = deslocada.transform(lambda s: s.rolling(28, min_periods=7).std())
    df["media_mesmo_dia_semana"] = df[["lag_28", "lag_35", "lag_42", "lag_49"]].mean(axis=1)

    datas = pd.DatetimeIndex(df["data"])
    df["dia_semana"] = datas.dayofweek
    df["dia_mes"] = datas.day
    df["mes"] = datas.month
    angulo = 2 * np.pi * datas.dayofyear / 365.25
    df["ano_sin"] = np.sin(angulo)
    df["ano_cos"] = np.cos(angulo)
    for coluna, valores in eventos_calendario(datas).items():
        df[coluna] = valores.to_numpy()
    return df


def colunas_modelo(df: pd.DataFrame) -> list[str]:
    ignorar = {"data", "vendas"}
    return [c for c in df.columns if c not in ignorar]
