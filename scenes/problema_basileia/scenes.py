"""Cena principal: o Problema da Basileia.

    ∑ 1/n²  =  1 + 1/4 + 1/9 + 1/16 + ...  =  π²/6

A solução original de Euler (1735): tratar sin(x)/x como um "polinômio
infinito", fatorá-lo pelas raízes e comparar os coeficientes de x².
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


class ProblemaBasileia(MovingCameraScene):
    """O problema que derrotou os Bernoulli e consagrou Euler aos 28 anos."""

    def construct(self):
        self.introducao()
        self.escrever_serie()
        self.serie_de_taylor()
        self.produto_de_euler()
        self.comparar_coeficientes()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo
    # ------------------------------------------------------------------
    def introducao(self):
        titulo = Text("O Problema da Basileia", font_size=46, color=DOURADO, weight=BOLD)
        subtitulo = Text("A Solução de Euler (1735)", font_size=30, color=CINZA)
        subtitulo.next_to(titulo, DOWN, buff=0.4)

        self.play(Write(titulo, run_time=2.0))
        self.play(FadeIn(subtitulo, shift=UP * 0.3, run_time=1.0))
        self.wait(1.2)

        cabecalho = Text("O Problema da Basileia", font_size=26, color=DOURADO)
        cabecalho.move_to(UP * 5.0)
        self.play(
            AnimationGroup(
                ReplacementTransform(titulo, cabecalho),
                FadeOut(subtitulo, shift=DOWN * 0.3),
                run_time=1.2,
            )
        )

    # ------------------------------------------------------------------
    # 2) A série misteriosa: qual é a soma exata?
    # ------------------------------------------------------------------
    def escrever_serie(self):
        self.eq = ajustar(
            MathTex(
                r"\sum_{n=1}^{\infty}\frac{1}{n^2}", "=",
                r"1+\frac{1}{4}+\frac{1}{9}+\frac{1}{16}+\cdots",
                color=BRANCO,
            )
        )
        self.play(Write(self.eq, run_time=2.5))
        self.wait(0.8)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))

    # ------------------------------------------------------------------
    # 3) Ponto de partida: a série de Taylor de sin(x)/x
    # ------------------------------------------------------------------
    def serie_de_taylor(self):
        nota = MathTex(
            r"\frac{\sin x}{x}=1-\frac{x^2}{3!}+\frac{x^4}{5!}-\cdots",
            color=AZUL, font_size=32,
        )
        carta = cartao(nota, "Série de Taylor do seno")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.wait(1.2)
        self.carta_taylor = carta

    # ------------------------------------------------------------------
    # 4) O golpe de gênio: fatorar sin(x)/x pelas raízes ±nπ
    # ------------------------------------------------------------------
    def produto_de_euler(self):
        # A equação principal vira a igualdade série = produto infinito
        igualdade = ajustar(
            MathTex(
                r"1-\frac{x^2}{3!}+\cdots", "=",
                r"\prod_{n=1}^{\infty}\left(1-\frac{x^2}{n^2\pi^2}\right)",
                color=BRANCO,
            )
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, igualdade),
                FadeOut(self.carta_taylor, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.wait(1.0)

        nota = Text('um "polinômio infinito" com raízes ±nπ', font_size=24, color=AZUL)
        carta = cartao(nota, "A ideia de Euler")
        carta.move_to(UP * 2.8)
        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(igualdade[2]))
        self.wait(0.8)

        # Expandindo o produto: o coeficiente de x² é a soma que procuramos
        expandida = ajustar(
            MathTex(
                r"1-\frac{x^2}{3!}+\cdots", "=",
                r"1-\left(\sum_{n=1}^{\infty}\frac{1}{n^2\pi^2}\right)x^2+\cdots",
                color=BRANCO,
            )
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(igualdade, expandida),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.eq = expandida
        self.wait(1.0)

    # ------------------------------------------------------------------
    # 5) Igualando os coeficientes de x² dos dois lados
    # ------------------------------------------------------------------
    def comparar_coeficientes(self):
        nota = MathTex(r"x^2", color=AZUL, font_size=34)
        carta = cartao(nota, "Iguale os coeficientes de x²")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq))
        self.wait(0.6)

        coeficientes = ajustar(
            MathTex(
                r"\frac{1}{3!}", "=",
                r"\sum_{n=1}^{\infty}\frac{1}{n^2\pi^2}",
                color=BRANCO,
            )
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, coeficientes),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.wait(1.0)

        # Multiplicando os dois lados por π²
        isolada = ajustar(
            MathTex(
                r"\sum_{n=1}^{\infty}\frac{1}{n^2}", "=",
                r"\frac{\pi^2}{6}",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(coeficientes, isolada, run_time=1.6))
        self.eq = isolada
        self.wait(0.8)

    # ------------------------------------------------------------------
    # 6) Resultado final em verde com glow: π²/6
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex(
            r"\sum_{n=1}^{\infty}\frac{1}{n^2}", "=", r"\frac{\pi^2}{6}",
            color=VERDE, font_size=60,
        )
        self.play(TransformMatchingTex(self.eq, resultado, run_time=1.5))

        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))
        self.wait(0.5)

        nota = Text("O π escondido nos quadrados perfeitos", font_size=22, color=CINZA)
        nota.move_to(resultado.get_center() + DOWN * 1.9)
        self.play(FadeIn(nota, shift=UP * 0.2, run_time=1.2))
        self.wait(2.6)
        self.play(FadeOut(VGroup(luz, resultado, nota), run_time=1.2))
