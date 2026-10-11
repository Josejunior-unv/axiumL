"""Features comportamentais por cliente, calculadas só com o passado.

Uma transação nunca enxerga transações posteriores a ela. Isso é o que permite
usar as mesmas features em tempo real, no momento da autorização.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

JANELAS = {"1h": 3600, "24h": 86_400, "7d": 7 * 86_400}

FEATURES = [
    "valor",
    "log_valor",
    "hora",
    "madrugada",
    "dia_semana",
    "online",
    "internacional",
    "dispositivo_novo",
    "log_distancia",
    "n_historico",
    "razao_valor_media",
    "minutos_desde_anterior",
    "categoria_nova",
    "categoria_risco",
    *[f"n_transacoes_{j}" for j in JANELAS],
    *[f"valor_{j}" for j in JANELAS],
]

CATEGORIAS_RISCO = {"eletronicos", "joias", "gift_card"}


def adicionar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Devolve uma cópia com as features, na mesma ordem das linhas de entrada."""
    ordem_original = df.index
    df = df.sort_values(["cliente_id", "data_hora", "transacao_id"]).copy()

    # Contagens e somas em janelas de tempo sem loop por cliente: a chave
    # cliente * deslocamento + segundos deixa cada cliente numa faixa própria,
    # e um searchsorted acha o começo da janela de cada transação.
    segundos = (df["data_hora"] - df["data_hora"].min()).dt.total_seconds().to_numpy()
    deslocamento = segundos.max() + 2 * max(JANELAS.values())
    chave = df["cliente_id"].to_numpy() * deslocamento + segundos
    posicao = np.arange(len(df))
    valores = df["valor"].to_numpy()
    soma_anterior = np.concatenate([[0.0], np.cumsum(valores)])
    for nome, janela in JANELAS.items():
        inicio = np.searchsorted(chave, chave - janela, side="left")
        df[f"n_transacoes_{nome}"] = posicao - inicio
        df[f"valor_{nome}"] = soma_anterior[posicao] - soma_anterior[inicio]

    por_cliente = df.groupby("cliente_id", sort=False)
    df["n_historico"] = por_cliente.cumcount()
    gasto_anterior = por_cliente["valor"].cumsum() - df["valor"]
    media_historica = gasto_anterior / df["n_historico"].replace(0, np.nan)
    df["razao_valor_media"] = df["valor"] / media_historica
    df["minutos_desde_anterior"] = por_cliente["data_hora"].diff().dt.total_seconds() / 60
    df["categoria_nova"] = (df.groupby(["cliente_id", "categoria"]).cumcount() == 0).astype(int)

    df["log_valor"] = np.log1p(df["valor"])
    df["log_distancia"] = np.log1p(df["distancia_casa_km"])
    df["hora"] = df["data_hora"].dt.hour
    df["madrugada"] = (df["hora"] < 6).astype(int)
    df["dia_semana"] = df["data_hora"].dt.dayofweek
    df["categoria_risco"] = df["categoria"].isin(CATEGORIAS_RISCO).astype(int)
    for coluna in ("online", "internacional", "dispositivo_novo"):
        df[coluna] = df[coluna].astype(int)

    return df.loc[ordem_original]
