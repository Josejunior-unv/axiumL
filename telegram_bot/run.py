#!/usr/bin/env python3
"""Sobe o assistente. Rode com: python run.py"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from telegram import Update  # noqa: E402

from assistente import bot, config  # noqa: E402


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s",
        datefmt="%d/%m %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    cfg = config.carregar()
    aplicacao = bot.montar(cfg)

    logging.info("banco: %s", cfg.caminho_db)
    logging.info("fuso padrão: %s", cfg.fuso_padrao)
    logging.info("conversa com IA: %s", "ligada" if cfg.ia_ativa else "desligada")
    if cfg.chats_permitidos:
        logging.info("chats permitidos: %s", sorted(cfg.chats_permitidos))
    logging.info("assistente no ar — Ctrl+C para parar")

    aplicacao.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
