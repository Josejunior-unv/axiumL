"""Cena principal: a Soma de Gauss.

    S = 1 + 2 + 3 + ... + n  =  n(n+1)/2

O truque lendário: escrever a soma de trás para frente e somar as duas.
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


class SomaDeGauss(MovingCameraScene):
    """A demonstração que Gauss (diz a lenda) fez aos 9 anos de idade."""

    def construct(self):
        self.introducao()
        self.escrever_soma()
        self.truque_de_gauss()
        self.somar_as_duas()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo
    # ------------------------------------------------------------------
    def introducao(self):
        titulo = Text("A Soma de Gauss", font_size=52, color=DOURADO, weight=BOLD)
        subtitulo = Text("Demonstração Clássica", font_size=30, color=CINZA)
        subtitulo.next_to(titulo, DOWN, buff=0.4)

        self.play(Write(titulo, run_time=2.0))
        self.play(FadeIn(subtitulo, shift=UP * 0.3, run_time=1.0))
        self.wait(1.5)

        cabecalho = Text("A Soma de Gauss", font_size=26, color=DOURADO)
        cabecalho.move_to(UP * 5.0)
        self.play(
            AnimationGroup(
                ReplacementTransform(titulo, cabecalho),
                FadeOut(subtitulo, shift=DOWN * 0.3),
                run_time=1.2,
            )
        )

    # ------------------------------------------------------------------
    # 2) A soma S é escrita e a câmera se aproxima
    # ------------------------------------------------------------------
    def escrever_soma(self):
        self.soma = ajustar(
            MathTex("S", "=", r"1+2+3+\cdots+n", color=BRANCO)
        )
        self.soma.move_to(UP * 0.9)
        self.play(Write(self.soma, run_time=2.8))
        self.wait(1.2)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))

    # ------------------------------------------------------------------
    # 3) O truque: escrever a MESMA soma de trás para frente
    # ------------------------------------------------------------------
    def truque_de_gauss(self):
        aviso = MathTex(
            r"S = n+(n-1)+\cdots+2+1",
            color=AZUL, font_size=32,
        )
        carta = cartao(aviso, "O truque: escreva ao contrário")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.soma[2]))
        self.wait(0.4)

        # A soma invertida aparece logo abaixo da original
        self.invertida = ajustar(
            MathTex("S", "=", r"n+(n-1)+\cdots+2+1", color=BRANCO)
        )
        self.invertida.move_to(DOWN * 0.5)
        self.play(Write(self.invertida, run_time=2.6))
        self.wait(1.4)
        self.play(FadeOut(carta, shift=UP * 0.3, run_time=0.9))

    # ------------------------------------------------------------------
    # 4) Somando as duas linhas: cada coluna dá exatamente (n+1)
    # ------------------------------------------------------------------
    def somar_as_duas(self):
        somadas = ajustar(
            MathTex(
                "2S", "=",
                r"\underbrace{(n+1)+(n+1)+\cdots+(n+1)}_{n\ \text{parcelas}}",
                color=BRANCO,
            )
        )
        somadas.move_to(ORIGIN)
        # Destaca as duas somas antes de combiná-las
        self.play(destacar(VGroup(self.soma, self.invertida)))
        self.wait(0.3)

        # As duas somas colapsam numa só: coluna a coluna, tudo vira (n+1)
        self.play(
            ReplacementTransform(VGroup(self.soma, self.invertida), somadas, run_time=2.6)
        )
        self.wait(2.2)

        # n parcelas iguais a (n+1): o produto n(n+1)
        produto = ajustar(MathTex("2S", "=", r"n(n+1)", color=BRANCO))
        self.play(TransformMatchingTex(somadas, produto, run_time=1.6))
        self.eq = produto
        self.wait(1.6)

    # ------------------------------------------------------------------
    # 5) Resultado final em verde com glow — e o exemplo lendário do 5050
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex("S", "=", r"\frac{n(n+1)}{2}", color=VERDE, font_size=64)
        self.play(TransformMatchingTex(self.eq, resultado, run_time=1.5))

        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))

        # A lenda: Gauss, aos 9 anos, somou de 1 a 100 em segundos
        exemplo = MathTex(
            r"1+2+\cdots+100 = \frac{100\cdot101}{2} = 5050",
            color=CINZA, font_size=26,
        )
        exemplo.move_to(resultado.get_center() + DOWN * 1.8)
        self.play(FadeIn(exemplo, shift=UP * 0.2, run_time=1.2))
        self.wait(4.2)
        self.play(FadeOut(VGroup(luz, resultado, exemplo), run_time=1.2))
