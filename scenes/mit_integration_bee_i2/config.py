"""Configuração do Manim para o vídeo vertical 1080x1920 @ 240 FPS (I2).

Chame `aplicar_configuracao()` ANTES de importar/instanciar as cenas,
pois a câmera lê essas configurações no momento em que a cena é criada.
"""

from pathlib import Path

from manim import config

from colors import FUNDO

# Resolução final exigida pelo briefing: 1080x1920 (9:16) a 240 FPS
LARGURA_FINAL = 1080
ALTURA_FINAL = 1920
FPS_FINAL = 240

# Valores reduzidos para pré-visualização rápida durante o desenvolvimento
LARGURA_PREVIEW = 540
ALTURA_PREVIEW = 960
FPS_PREVIEW = 30

# Saída centralizada na pasta media/ na raiz do repositório axiumL
PASTA_MEDIA = Path(__file__).resolve().parents[2] / "media"


def aplicar_configuracao(preview: bool = False) -> None:
    """Aplica resolução, FPS, enquadramento vertical e fundo escuro."""
    if preview:
        config.pixel_width = LARGURA_PREVIEW
        config.pixel_height = ALTURA_PREVIEW
        config.frame_rate = FPS_PREVIEW
    else:
        config.pixel_width = LARGURA_FINAL
        config.pixel_height = ALTURA_FINAL
        config.frame_rate = FPS_FINAL

    # Enquadramento em unidades de cena: largura 8, altura 8 * 16/9 (retrato)
    config.frame_width = 8.0
    config.frame_height = 8.0 * ALTURA_FINAL / LARGURA_FINAL

    config.background_color = FUNDO

    # Organização da saída: media/videos/mit_integration_bee_i2/<qualidade>/
    config.media_dir = str(PASTA_MEDIA)
    config.video_dir = "{media_dir}/videos/mit_integration_bee_i2/{quality}"
    config.output_file = "MITIntegrationBeeI2"
