"""Cena principal: a dízima 0,999... é exatamente igual a 1.

Demonstração clássica pelo truque do 10x: multiplicar por 10, subtrair,
e ver a dízima desaparecer. Não é aproximação — é igualdade.

Mesmo modelo visual dos vídeos MIT Integration Bee: vertical 9:16,
fundo #0D1117, cartões azuis, resultado verde com glow e zooms suaves.
"""

from manim import (
    BOLD,
    DOWN,
    ORIGIN,
    UP,
    AnimationGroup,
    FadeIn,
    FadeOut,
    MathTex,
    MovingCameraScene,
    ReplacementTransform,
    SurroundingRectangle,
    Text,
    TransformMatchingTex,
    VGroup,
    Write,
)

from animations import brilho, destacar, zoom_suave
from colors import AZUL, BRANCO, CINZA, DOURADO, VERDE

# Largura máxima (em unidades de cena) das equações principais
LARGURA_MAXIMA = 5.6


def ajustar(eq):
    """Reduz a equação se ela for mais larga que o enquadramento útil."""
    if eq.width > LARGURA_MAXIMA:
        eq.scale_to_fit_width(LARGURA_MAXIMA)
    return eq


def cartao(conteudo, titulo: str = "") -> VGroup:
    """Monta um cartão translúcido com um título opcional em português."""
    interno = conteudo
    if titulo:
        rotulo = Text(titulo, font_size=22, color=CINZA)
        interno = VGroup(rotulo, conteudo).arrange(DOWN, buff=0.3)
    moldura = SurroundingRectangle(
        interno,
        color=AZUL,
        buff=0.3,
        corner_radius=0.14,
        stroke_width=1.5,
        fill_color=AZUL,
        fill_opacity=0.06,
    )
    return VGroup(moldura, interno)


class Dizima0999(MovingCameraScene):
    """O truque do 10x que encerra a discussão."""

    def construct(self):
        self.introducao()
        self.chamar_de_x()
        self.multiplicar_por_dez()
        self.subtrair()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo provocador
    # ------------------------------------------------------------------
    def introducao(self):
        titulo = Text("0,999… = 1?", font_size=52, color=DOURADO, weight=BOLD)
        subtitulo = Text("Sim — e dá para provar", font_size=30, color=CINZA)
        subtitulo.next_to(titulo, DOWN, buff=0.4)

        self.play(Write(titulo, run_time=2.0))
        self.play(FadeIn(subtitulo, shift=UP * 0.3, run_time=1.0))
        self.wait(1.5)

        cabecalho = Text("0,999… = 1", font_size=26, color=DOURADO)
        cabecalho.move_to(UP * 5.0)
        self.play(
            AnimationGroup(
                ReplacementTransform(titulo, cabecalho),
                FadeOut(subtitulo, shift=DOWN * 0.3),
                run_time=1.2,
            )
        )

    # ------------------------------------------------------------------
    # 2) Batize a dízima de x
    # ------------------------------------------------------------------
    def chamar_de_x(self):
        self.eq = ajustar(MathTex("x", "=", r"0{,}999\ldots", color=BRANCO))
        self.play(Write(self.eq, run_time=2.4))
        self.wait(1.2)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))

    # ------------------------------------------------------------------
    # 3) Multiplique tudo por 10: a vírgula anda uma casa
    # ------------------------------------------------------------------
    def multiplicar_por_dez(self):
        nota = MathTex(r"\times\,10", color=AZUL, font_size=34)
        carta = cartao(nota, "Multiplique por 10")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq))
        self.wait(0.9)

        nova = ajustar(MathTex("10x", "=", r"9{,}999\ldots", color=BRANCO))
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, nova),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.eq = nova
        self.wait(1.6)

    # ------------------------------------------------------------------
    # 4) Subtraia x dos dois lados: a dízima infinita se cancela
    # ------------------------------------------------------------------
    def subtrair(self):
        nota = MathTex(r"9{,}999\ldots-0{,}999\ldots=9", color=AZUL, font_size=32)
        carta = cartao(nota, "Subtraia x dos dois lados")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.wait(1.2)

        subtraida = ajustar(MathTex("10x - x", "=", r"9{,}999\ldots-0{,}999\ldots", color=BRANCO))
        self.play(TransformMatchingTex(self.eq, subtraida, run_time=2.0))
        self.wait(1.6)

        # As infinitas casas 9 se cancelam perfeitamente
        limpa = ajustar(MathTex("9x", "=", "9", color=BRANCO))
        self.play(
            AnimationGroup(
                TransformMatchingTex(subtraida, limpa),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.wait(1.4)

        x_igual_1 = ajustar(MathTex("x", "=", "1", color=BRANCO))
        self.play(TransformMatchingTex(limpa, x_igual_1, run_time=1.4))
        self.eq = x_igual_1
        self.wait(1.4)

    # ------------------------------------------------------------------
    # 5) Conclusão em verde com glow: igualdade exata, não aproximação
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex(r"0{,}999\ldots", "=", "1", color=VERDE, font_size=64)
        self.play(TransformMatchingTex(self.eq, resultado, run_time=1.5))

        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))
        self.wait(0.6)

        nota = Text("Não é aproximação. É igualdade.", font_size=22, color=CINZA)
        nota.move_to(resultado.get_center() + DOWN * 1.8)
        self.play(FadeIn(nota, shift=UP * 0.2, run_time=1.2))
        self.wait(3.0)
        self.play(FadeOut(VGroup(luz, resultado, nota), run_time=1.2))
