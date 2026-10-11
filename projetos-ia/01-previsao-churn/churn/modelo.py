"""Pipeline de modelagem: features, comparação de modelos e limiar de negócio."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

CATEGORICAS = ["contrato", "internet", "pagamento", "regiao"]
NUMERICAS_BRUTAS = [
    "meses_cliente",
    "idade",
    "dependentes",
    "mensalidade",
    "total_gasto",
    "chamados_suporte",
    "atrasos_pagamento",
    "streaming",
]
DERIVADAS = ["log_meses_cliente", "gasto_medio_mensal", "cliente_novo"]
NUMERICAS = NUMERICAS_BRUTAS + DERIVADAS
ENTRADAS = NUMERICAS_BRUTAS + CATEGORICAS


def adicionar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cria as variáveis derivadas. Roda dentro do pipeline, então a API
    recebe só os campos brutos do cliente."""
    df = df.copy()
    df["streaming"] = df["streaming"].astype(int)
    df["log_meses_cliente"] = np.log1p(df["meses_cliente"])
    df["gasto_medio_mensal"] = df["total_gasto"] / df["meses_cliente"].clip(lower=1)
    df["cliente_novo"] = (df["meses_cliente"] <= 6).astype(int)
    return df


def construir_pipeline(estimador) -> Pipeline:
    preprocessamento = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERICAS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
        ]
    )
    return Pipeline(
        [
            ("features", FunctionTransformer(adicionar_features)),
            ("prep", preprocessamento),
            ("modelo", estimador),
        ]
    )


def candidatos(semente: int = 42) -> dict[str, Pipeline]:
    return {
        "regressao_logistica": construir_pipeline(LogisticRegression(max_iter=2000, C=0.5)),
        "gradient_boosting": construir_pipeline(
            HistGradientBoostingClassifier(
                learning_rate=0.05,
                max_iter=250,
                max_leaf_nodes=15,
                l2_regularization=1.0,
                random_state=semente,
            )
        ),
    }


def lucro_campanha(
    y: np.ndarray,
    probabilidade: np.ndarray,
    valor_cliente: np.ndarray,
    limiar: float,
    custo_oferta: float = 120.0,
    taxa_sucesso: float = 0.30,
) -> float:
    """Lucro de oferecer retenção a quem tem probabilidade >= limiar.

    Cada oferta custa `custo_oferta`. Se o cliente ia mesmo cancelar, a oferta
    o segura com chance `taxa_sucesso`, preservando `valor_cliente`.
    """
    alvo = probabilidade >= limiar
    ganho = (y[alvo] * taxa_sucesso * valor_cliente[alvo]).sum()
    return float(ganho - custo_oferta * alvo.sum())


def limiar_otimo(
    y: np.ndarray, probabilidade: np.ndarray, valor_cliente: np.ndarray, **custos
) -> tuple[float, float]:
    """Varre limiares e devolve (limiar, lucro) que maximiza o lucro."""
    limiares = np.round(np.linspace(0.02, 0.98, 97), 2)
    lucros = [lucro_campanha(y, probabilidade, valor_cliente, t, **custos) for t in limiares]
    melhor = int(np.argmax(lucros))
    return float(limiares[melhor]), float(lucros[melhor])


@dataclass
class ResultadoValidacao:
    nome: str
    roc_auc: float
    pr_auc: float
    probabilidades: np.ndarray


def validar_candidatos(
    X: pd.DataFrame, y: pd.Series, semente: int = 42, folds: int = 5
) -> list[ResultadoValidacao]:
    """Validação cruzada estratificada; devolve as previsões fora da amostra
    de cada candidato (usadas depois para escolher o limiar sem olhar o teste)."""
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=semente)
    resultados = []
    for nome, pipeline in candidatos(semente).items():
        prob = cross_val_predict(pipeline, X, y, cv=cv, method="predict_proba")[:, 1]
        resultados.append(
            ResultadoValidacao(
                nome=nome,
                roc_auc=roc_auc_score(y, prob),
                pr_auc=average_precision_score(y, prob),
                probabilidades=prob,
            )
        )
    return sorted(resultados, key=lambda r: r.roc_auc, reverse=True)


def avaliar(y: np.ndarray, probabilidade: np.ndarray) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y, probabilidade)),
        "pr_auc": float(average_precision_score(y, probabilidade)),
        "brier": float(brier_score_loss(y, probabilidade)),
    }


def importancia_variaveis(
    pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, semente: int = 42
) -> pd.Series:
    """Importância por permutação, medida nas colunas brutas de entrada."""
    resultado = permutation_importance(
        pipeline, X, y, scoring="roc_auc", n_repeats=5, random_state=semente
    )
    return pd.Series(resultado.importances_mean, index=X.columns).sort_values(ascending=False)
