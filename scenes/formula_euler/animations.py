"""Animações e efeitos reutilizáveis do vídeo."""

from manim import (
    Circumscribe,
    SurroundingRectangle,
    VGroup,
)

from colors import AZUL


def brilho(mobjeto, cor, camadas: int = 6, largura_maxima: float = 22.0, buff: float = 0.28):
    """Cria um efeito de glow ao redor de `mobjeto`.

    O glow é feito com várias cópias de um SurroundingRectangle de cantos
    arredondados, cada uma com traço mais largo e mais transparente que a
    anterior — somadas, elas parecem uma luz difusa.
    """
    camadas_de_luz = VGroup()
    for i in range(camadas, 0, -1):
        fracao = i / camadas
        contorno = SurroundingRectangle(
            mobjeto,
            color=cor,
            buff=buff,
            corner_radius=0.15,
            stroke_width=largura_maxima * fracao,
            stroke_opacity=0.12 * (1 - fracao) + 0.03,
        )
        camadas_de_luz.add(contorno)
    # Contorno nítido por cima das camadas difusas
    camadas_de_luz.add(
        SurroundingRectangle(
            mobjeto, color=cor, buff=buff, corner_radius=0.15, stroke_width=2.5
        )
    )
    return camadas_de_luz


def destacar(mobjeto, cor=AZUL, run_time: float = 1.4):
    """Circunda um trecho da equação para chamar atenção antes de aplicá-lo."""
    return Circumscribe(
        mobjeto,
        color=cor,
        buff=0.12,
        stroke_width=3,
        run_time=run_time,
        fade_out=True,
    )


def zoom_suave(camera_frame, alvo, escala: float, run_time: float = 1.6):
    """Zoom cinematográfico: aproxima (escala < 1) ou afasta (escala > 1) do alvo."""
    return camera_frame.animate(run_time=run_time).scale(escala).move_to(alvo)
