"""Prevê as próximas 4 semanas de cada loja x produto.

    python -m demanda.prever
    python -m demanda.prever --saida artefatos/previsao.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

from demanda.dados import gerar_vendas
from demanda.modelo import prever_futuro


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=Path("artefatos/previsao.csv"))
    args = parser.parse_args()

    previsao = prever_futuro(gerar_vendas(semente=args.semente))

    # Quantis não somam entre séries, então o total da rede sai só com a previsão pontual
    total = previsao.groupby("data")["previsao"].sum().round(0)
    print("Previsão total da rede (unidades por dia), primeiras duas semanas:")
    print(total.head(14).to_string())

    exemplo = previsao[(previsao["loja"] == 1) & (previsao["produto"] == 1)]
    print("\nLoja 1, produto 1, com intervalo de 80%:")
    print(exemplo.set_index("data")[["previsao", "p10", "p90"]].head(7).round(1).to_string())

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    previsao.to_csv(args.saida, index=False)
    print(f"\nPrevisão por loja x produto salva em {args.saida}")


if __name__ == "__main__":
    main()
