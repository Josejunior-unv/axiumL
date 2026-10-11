"""Compara regras, detecção de anomalia e modelos supervisionados.

    python -m fraude.avaliar
    python -m fraude.avaliar --orcamento 0.01
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from fraude.dados import gerar_transacoes
from fraude.features import adicionar_features
from fraude.modelo import (
    DetectorAnomalia,
    DetectorSupervisionado,
    avaliar,
    pontuacao_regras,
    separar_por_tempo,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orcamento", type=float, default=0.005,
                        help="fração das transações que os analistas conseguem revisar")
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=Path("artefatos"))
    args = parser.parse_args()

    df = adicionar_features(gerar_transacoes(semente=args.semente))
    treino, teste = separar_por_tempo(df)
    print(f"Transações: {len(df):,} | fraudes: {df['fraude'].sum():,} ({df['fraude'].mean():.2%})")
    print(f"Treino: {len(treino):,} (até {treino['data_hora'].max():%d/%m}) | "
          f"teste: {len(teste):,} com {teste['fraude'].sum()} fraudes")

    pontuacoes = {
        "regras_de_negocio": pontuacao_regras(teste),
        "isolation_forest": DetectorAnomalia().fit(treino).pontuar(teste),
        "gradient_boosting": DetectorSupervisionado().fit(treino).pontuar(teste),
        "gb_+_anomalia": DetectorSupervisionado(usar_anomalia=True).fit(treino).pontuar(teste),
    }
    tabela = pd.DataFrame(
        {nome: avaliar(teste["fraude"], p, teste["valor"], args.orcamento)
         for nome, p in pontuacoes.items()}
    ).T

    print(f"\nRevisando {args.orcamento:.1%} das transações do teste:\n")
    print(tabela.to_string(float_format=lambda v: f"{v:.3f}"))

    args.saida.mkdir(parents=True, exist_ok=True)
    (args.saida / "metricas.json").write_text(json.dumps(tabela.to_dict("index"), indent=2))
    print(f"\nMétricas salvas em {args.saida / 'metricas.json'}")


if __name__ == "__main__":
    main()
