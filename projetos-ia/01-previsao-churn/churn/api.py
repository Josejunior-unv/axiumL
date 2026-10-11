"""API de previsão de churn.

    uvicorn churn.api:app --reload

O modelo é lido de `artefatos/modelo.joblib` (ou do caminho na variável
de ambiente CHURN_MODELO) quando a API sobe.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

CAMINHO_MODELO = Path(os.environ.get("CHURN_MODELO", "artefatos/modelo.joblib"))


class Cliente(BaseModel):
    contrato: Literal["mensal", "anual", "bianual"]
    internet: Literal["fibra", "dsl", "sem_internet"]
    pagamento: Literal["boleto", "cartao_credito", "pix", "debito_automatico"]
    regiao: Literal["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
    meses_cliente: int = Field(ge=1, le=240)
    idade: int = Field(ge=18, le=110)
    dependentes: int = Field(ge=0, le=20)
    streaming: bool
    mensalidade: float = Field(gt=0)
    total_gasto: float = Field(ge=0)
    chamados_suporte: int = Field(ge=0)
    atrasos_pagamento: int = Field(ge=0)


class Previsao(BaseModel):
    probabilidade_churn: float
    acionar_retencao: bool
    limiar: float


def criar_app(artefato: dict | None = None) -> FastAPI:
    estado = {"artefato": artefato}

    @asynccontextmanager
    async def ciclo_de_vida(_: FastAPI):
        if estado["artefato"] is None:
            estado["artefato"] = joblib.load(CAMINHO_MODELO)
        yield

    app = FastAPI(title="Previsão de churn", lifespan=ciclo_de_vida)

    @app.get("/saude")
    def saude() -> dict:
        return {"status": "ok", "modelo": estado["artefato"]["modelo"]}

    @app.post("/prever", response_model=Previsao)
    def prever(cliente: Cliente) -> Previsao:
        pipeline, limiar = estado["artefato"]["pipeline"], estado["artefato"]["limiar"]
        prob = float(pipeline.predict_proba(pd.DataFrame([cliente.model_dump()]))[0, 1])
        return Previsao(
            probabilidade_churn=round(prob, 4),
            acionar_retencao=prob >= limiar,
            limiar=limiar,
        )

    return app


app = criar_app()
