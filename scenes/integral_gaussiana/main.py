"""Ponto de entrada do vÃ­deo a Integral Gaussiana.

Uso (dentro desta pasta):

    python main.py --preview   # render rÃ¡pido (540x960 @ 30 FPS) para conferir
    python main.py             # render final  (1080x1920 @ 240 FPS) â€” demorado!
"""

import argparse
import sys
from pathlib import Path

# Garante que os mÃ³dulos do projeto sejam encontrados mesmo se o script
# for chamado de outro diretÃ³rio
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import aplicar_configuracao


def main() -> None:
    parser = argparse.ArgumentParser(description="Renderiza o vÃ­deo a Integral Gaussiana")
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="render rÃ¡pido em baixa resoluÃ§Ã£o/FPS para prÃ©-visualizaÃ§Ã£o",
    )
    args = parser.parse_args()

    # A configuraÃ§Ã£o precisa ser aplicada ANTES de importar a cena,
    # pois a cÃ¢mera lÃª resoluÃ§Ã£o/FPS no momento da criaÃ§Ã£o
    aplicar_configuracao(preview=args.preview)

    from scenes import IntegralGaussiana

    cena = IntegralGaussiana()
    cena.render(preview=True)  # abre o vÃ­deo ao terminar


if __name__ == "__main__":
    main()

