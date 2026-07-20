"""Ponto de entrada do vídeo A Soma de Gauss.

Uso (dentro desta pasta):

    python main.py --preview   # render rápido (540x960 @ 30 FPS) para conferir
    python main.py             # render final  (1080x1920 @ 240 FPS) — demorado!
"""

import argparse
import sys
from pathlib import Path

# Garante que os módulos do projeto sejam encontrados mesmo se o script
# for chamado de outro diretório
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import aplicar_configuracao


def main() -> None:
    parser = argparse.ArgumentParser(description="Renderiza o vídeo A Soma de Gauss")
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="render rápido em baixa resolução/FPS para pré-visualização",
    )
    args = parser.parse_args()

    # A configuração precisa ser aplicada ANTES de importar a cena,
    # pois a câmera lê resolução/FPS no momento da criação
    aplicar_configuracao(preview=args.preview)

    from scenes import SomaDeGauss

    cena = SomaDeGauss()
    cena.render(preview=True)  # abre o vídeo ao terminar


if __name__ == "__main__":
    main()
