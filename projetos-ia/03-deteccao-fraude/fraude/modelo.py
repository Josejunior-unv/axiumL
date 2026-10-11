"""Detectores de fraude e métricas com orçamento de alertas."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score

from fraude.features import FEATURES


def separar_por_tempo(df: pd.DataFrame, dias_teste: int = 30) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Treina no passado e testa nos últimos `dias_teste` dias, como em produção.
    Um corte aleatório deixaria transações da mesma rajada de fraude dos dois lados."""
    corte = df["data_hora"].max() - pd.Timedelta(days=dias_teste)
    return df[df["data_hora"] <= corte], df[df["data_hora"] > corte]


def pontuacao_regras(df: pd.DataFrame) -> np.ndarray:
    """Regras de negócio típicas de um primeiro sistema antifraude."""
    return (
        2 * (df["razao_valor_media"].fillna(1) > 4)
        + (df["dispositivo_novo"] == 1)
        + (df["madrugada"] == 1)
        + (df["internacional"] == 1)
        + (df["categoria_risco"] == 1)
        + (df["n_transacoes_1h"] >= 2)
    ).to_numpy(dtype=float)


class DetectorAnomalia:
    """Isolation Forest: não usa rótulos, só aprende o que é comportamento comum."""

    def fit(self, df: pd.DataFrame) -> DetectorAnomalia:
        self.modelo = IsolationForest(n_estimators=300, random_state=0)
        self.modelo.fit(df[FEATURES].fillna(-1))
        return self

    def pontuar(self, df: pd.DataFrame) -> np.ndarray:
        return -self.modelo.score_samples(df[FEATURES].fillna(-1))


class DetectorSupervisionado:
    """Gradient boosting nos rótulos históricos, opcionalmente com a nota de
    anomalia do Isolation Forest como feature extra."""

    def __init__(self, usar_anomalia: bool = False):
        self.usar_anomalia = usar_anomalia

    def _matriz(self, df: pd.DataFrame) -> pd.DataFrame:
        X = df[FEATURES].copy()
        if self.usar_anomalia:
            X["nota_anomalia"] = self.anomalia.pontuar(df)
        return X

    def fit(self, df: pd.DataFrame) -> DetectorSupervisionado:
        if self.usar_anomalia:
            self.anomalia = DetectorAnomalia().fit(df)
        self.modelo = HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=300,
            max_leaf_nodes=15,
            min_samples_leaf=30,
            l2_regularization=1.0,
            random_state=0,
        )
        self.modelo.fit(self._matriz(df), df["fraude"])
        return self

    def pontuar(self, df: pd.DataFrame) -> np.ndarray:
        return self.modelo.predict_proba(self._matriz(df))[:, 1]


def alertas_no_orcamento(pontuacao: np.ndarray, fracao: float) -> np.ndarray:
    """Marca as `fracao` transações de maior pontuação: é o que o time de
    analistas consegue revisar."""
    k = max(1, int(round(len(pontuacao) * fracao)))
    marcadas = np.zeros(len(pontuacao), dtype=bool)
    marcadas[np.argsort(-pontuacao, kind="stable")[:k]] = True
    return marcadas


def avaliar(y, pontuacao, valor, fracao_alertas: float = 0.005) -> dict[str, float]:
    y, pontuacao, valor = map(np.asarray, (y, pontuacao, valor))
    alerta = alertas_no_orcamento(pontuacao, fracao_alertas)
    return {
        "pr_auc": float(average_precision_score(y, pontuacao)),
        "roc_auc": float(roc_auc_score(y, pontuacao)),
        "precisao_alertas": float(y[alerta].mean()),
        "recall_alertas": float(y[alerta].sum() / y.sum()),
        "valor_fraude_barrado": float((valor * y)[alerta].sum() / (valor * y).sum()),
    }
