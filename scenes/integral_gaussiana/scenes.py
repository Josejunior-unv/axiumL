"""Cena principal: a Integral Gaussiana.

    I = ∫_{-∞}^{∞} e^{-x²} dx  =  √π

O truque de Poisson: elevar ao quadrado, passar a coordenadas polares
e ver a integral impossível se render em três linhas.
Mesmo modelo visual dos vídeos anteriores: vertical 9:16, fundo #0D1117,
cartões azuis, resultado verde com glow e zooms suaves.
"""

from manim import (
    BOLD,
    DOWN,
    ORIGIN,
    UP,
    AnimationGroup,
    FadeIn,
    FadeOut,
    LaggedStart,
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


class IntegralGaussiana(MovingCameraScene):
    """A integral que não tem primitiva elementar — mas tem valor exato."""

    def construct(self):
        self.introducao()
        self.escrever_integral()
        self.elevar_ao_quadrado()
        self.coordenadas_polares()
        self.resolver()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo
    # ------------------------------------------------------------------
    def introducao(self):
        titulo = Text("A Integral Gaussiana", font_size=48, color=DOURADO, weight=BOLD)
        subtitulo = Text("O Truque de Poisson", font_size=30, color=CINZA)
        subtitulo.next_to(titulo, DOWN, buff=0.4)

        self.play(Write(titulo, run_time=2.0))
        self.play(FadeIn(subtitulo, shift=UP * 0.3, run_time=1.0))
        self.wait(1.2)

        cabecalho = Text("A Integral Gaussiana", font_size=26, color=DOURADO)
        cabecalho.move_to(UP * 5.0)
        self.play(
            AnimationGroup(
                ReplacementTransform(titulo, cabecalho),
                FadeOut(subtitulo, shift=DOWN * 0.3),
                run_time=1.2,
            )
        )

    # ------------------------------------------------------------------
    # 2) A integral é escrita e a câmera se aproxima
    # ------------------------------------------------------------------
    def escrever_integral(self):
        self.eq = ajustar(
            MathTex("I", "=", r"\int_{-\infty}^{\infty}e^{-x^2}\,dx", color=BRANCO)
        )
        self.play(Write(self.eq, run_time=2.5))
        self.wait(0.8)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))

    # ------------------------------------------------------------------
    # 3) O truque: elevar ao quadrado com duas variáveis independentes
    # ------------------------------------------------------------------
    def elevar_ao_quadrado(self):
        nota = MathTex(
            r"e^{-x^2}\,e^{-y^2}=e^{-(x^2+y^2)}",
            color=AZUL, font_size=32,
        )
        carta = cartao(nota, "Eleve ao quadrado (y independente)")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq))
        self.wait(0.6)

        # I² vira uma integral dupla sobre o plano todo
        nova = ajustar(
            MathTex(
                "I^2", "=",
                r"\iint_{\mathbb{R}^2}e^{-(x^2+y^2)}\,dx\,dy",
                color=BRANCO,
            )
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, nova),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.eq = nova
        self.wait(0.9)

    # ------------------------------------------------------------------
    # 4) Coordenadas polares: a simetria circular resolve tudo
    # ------------------------------------------------------------------
    def coordenadas_polares(self):
        linha1 = MathTex(r"x^2+y^2=r^2", color=AZUL, font_size=32)
        linha2 = MathTex(r"dx\,dy=r\,dr\,d\theta", color=AZUL, font_size=32)
        linhas = VGroup(linha1, linha2).arrange(DOWN, buff=0.3)
        carta = cartao(linhas, "Coordenadas polares")
        carta.move_to(UP * 2.8)

        # As duas relações entram em cascata (LaggedStart)
        self.play(
            LaggedStart(
                FadeIn(carta[0]),
                FadeIn(carta[1], shift=DOWN * 0.2),
                lag_ratio=0.35,
                run_time=1.8,
            )
        )
        self.wait(0.8)

        nova = ajustar(
            MathTex(
                "I^2", "=",
                r"\int_0^{2\pi}\!\!\int_0^{\infty}e^{-r^2}\,r\,dr\,d\theta",
                color=BRANCO,
            )
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, nova),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.eq = nova
        self.wait(0.9)

    # ------------------------------------------------------------------
    # 5) A integral interna vale 1/2 (substituição u = r²), sobra 2π·(1/2)
    # ------------------------------------------------------------------
    def resolver(self):
        nota = MathTex(
            r"u=r^2:\quad\int_0^{\infty}e^{-r^2}\,r\,dr=\frac{1}{2}",
            color=AZUL, font_size=32,
        )
        carta = cartao(nota, "Substituição u = r²")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq[2]))
        self.wait(0.6)

        meio = ajustar(
            MathTex("I^2", "=", r"\int_0^{2\pi}\frac{1}{2}\,d\theta", color=BRANCO)
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, meio),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.wait(0.8)

        pi = ajustar(MathTex("I^2", "=", r"\pi", color=BRANCO))
        self.play(TransformMatchingTex(meio, pi, run_time=1.5))
        self.eq = pi
        self.wait(1.0)

    # ------------------------------------------------------------------
    # 6) Resultado final em verde com glow: I = √π
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex("I", "=", r"\sqrt{\pi}", color=VERDE, font_size=64)
        self.play(TransformMatchingTex(self.eq, resultado, run_time=1.5))

        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))
        self.wait(0.5)

        nota = Text("A curva do sino tem área exatamente √π", font_size=22, color=CINZA)
        nota.move_to(resultado.get_center() + DOWN * 1.8)
        self.play(FadeIn(nota, shift=UP * 0.2, run_time=1.2))
        self.wait(2.8)
        self.play(FadeOut(VGroup(luz, resultado, nota), run_time=1.2))
