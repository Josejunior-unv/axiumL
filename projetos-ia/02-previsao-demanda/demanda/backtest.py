"""Backtest com origem móvel: compara o modelo com duas referências simples.

    python -m demanda.backtest
    python -m demanda.backtest --janelas 6 --saida artefatos
"""

from __future__ import annotations

import argparse
from pathlib import Path

from demanda.dados import black_friday, gerar_vendas
from demanda.modelo import backtest, cobertura, resumir, wape


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--janelas", type=int, default=3)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=Path("artefatos"))
    args = parser.parse_args()

    vendas = gerar_vendas(semente=args.semente)
    series = vendas.groupby(["loja", "produto"]).ngroups
    print(f"{series} séries diárias, {vendas['data'].min():%d/%m/%Y} a "
          f"{vendas['data'].max():%d/%m/%Y} ({len(vendas):,} linhas)")

    resultado = backtest(vendas, janelas=args.janelas)
    print(f"\nBacktest: {args.janelas} janelas de 28 dias\n")
    print(resumir(resultado).to_string(float_format=lambda v: f"{v:.3f}"))

    print(f"\nCobertura do intervalo de 80% (p10-p90): "
          f"{cobertura(resultado['vendas'], resultado['p10'], resultado['p90']):.1%}")

    print("\nWAPE por janela:")
    for origem, janela in resultado.groupby("origem"):
        print(f"  a partir de {origem:%d/%m/%Y}: modelo {wape(janela['vendas'], janela['gradient_boosting']):.3f}"
              f" | média 4 semanas {wape(janela['vendas'], janela['media_4_semanas']):.3f}")

    bf = resultado[resultado["data"].isin([black_friday(a) for a in resultado["data"].dt.year.unique()])]
    if len(bf):
        print(f"\nBlack Friday: vendas {bf['vendas'].sum():,.0f} | modelo {bf['gradient_boosting'].sum():,.0f}"
              f" | média 4 semanas {bf['media_4_semanas'].sum():,.0f}")

    args.saida.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(args.saida / "backtest.csv", index=False)
    print(f"\nPrevisões do backtest salvas em {args.saida / 'backtest.csv'}")


if __name__ == "__main__":
    main()
