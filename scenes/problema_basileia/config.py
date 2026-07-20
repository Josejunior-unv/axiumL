"""ConfiguraÃ§Ã£o do Manim para o vÃ­deo vertical 1080x1920 @ 240 FPS.

Chame `aplicar_configuracao()` ANTES de importar/instanciar as cenas,
pois a cÃ¢mera lÃª essas configuraÃ§Ãµes no momento em que a cena Ã© criada.
"""

from pathlib import Path

from manim import config

from colors import FUNDO

# ResoluÃ§Ã£o final exigida pelo briefing: 1080x1920 (9:16) a 240 FPS
LARGURA_FINAL = 1080
ALTURA_FINAL = 1920
FPS_FINAL = 240

# Valores reduzidos para prÃ©-visualizaÃ§Ã£o rÃ¡pida durante o desenvolvimento
LARGURA_PREVIEW = 540
ALTURA_PREVIEW = 960
FPS_PREVIEW = 30

# SaÃ­da centralizada na pasta media/ na raiz do repositÃ³rio axiumL
PASTA_MEDIA = Path(__file__).resolve().parents[2] / "media"


def aplicar_configuracao(preview: bool = False) -> None:
    """Aplica resoluÃ§Ã£o, FPS, enquadramento vertical e fundo escuro."""
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

    # OrganizaÃ§Ã£o da saÃ­da: media/videos/problema_basileia/<qualidade>/
    config.media_dir = str(PASTA_MEDIA)
    config.video_dir = "{media_dir}/videos/problema_basileia/{quality}"
    config.output_file = "ProblemaBasileia"

