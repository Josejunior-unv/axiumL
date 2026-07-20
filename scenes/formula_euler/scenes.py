"""Cena principal: a Fórmula de Euler e a identidade e^{iπ} + 1 = 0.

Demonstração via séries de Taylor: substituir z = ix na exponencial,
separar real e imaginário, reconhecer cosseno e seno, avaliar em x = π.
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


class FormulaEuler(MovingCameraScene):
    """e, i, π, 1 e 0 — as cinco constantes numa equação só."""

    def construct(self):
        self.introducao()
        self.serie_da_exponencial()
        self.substituir_ix()
        self.separar_real_imaginario()
        self.formula_de_euler()
        self.avaliar_em_pi()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo
    # ------------------------------------------------------------------
    def introducao(self):
        titulo = Text("A Fórmula de Euler", font_size=48, color=DOURADO, weight=BOLD)
        subtitulo = Text("A Equação Mais Bela da Matemática", font_size=26, color=CINZA)
        subtitulo.next_to(titulo, DOWN, buff=0.4)

        self.play(Write(titulo, run_time=2.0))
        self.play(FadeIn(subtitulo, shift=UP * 0.3, run_time=1.0))
        self.wait(1.2)

        cabecalho = Text("A Fórmula de Euler", font_size=26, color=DOURADO)
        cabecalho.move_to(UP * 5.0)
        self.play(
            AnimationGroup(
                ReplacementTransform(titulo, cabecalho),
                FadeOut(subtitulo, shift=DOWN * 0.3),
                run_time=1.2,
            )
        )

    # ------------------------------------------------------------------
    # 2) A série de Taylor da exponencial
    # ------------------------------------------------------------------
    def serie_da_exponencial(self):
        self.eq = ajustar(
            MathTex(
                "e^{z}", "=",
                r"1+z+\frac{z^2}{2!}+\frac{z^3}{3!}+\frac{z^4}{4!}+\cdots",
                color=BRANCO,
            )
        )
        self.play(Write(self.eq, run_time=2.5))
        self.wait(0.8)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))

    # ------------------------------------------------------------------
    # 3) Substituindo z = ix (com i² = -1, os sinais alternam)
    # ------------------------------------------------------------------
    def substituir_ix(self):
        nota = MathTex(r"z=ix,\qquad i^2=-1", color=AZUL, font_size=32)
        carta = cartao(nota, "Substitua z = ix")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq))
        self.wait(0.6)

        nova = ajustar(
            MathTex(
                "e^{ix}", "=",
                r"1+ix-\frac{x^2}{2!}-i\frac{x^3}{3!}+\frac{x^4}{4!}+\cdots",
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
        self.wait(1.0)

    # ------------------------------------------------------------------
    # 4) Separando as parcelas reais das imaginárias
    # ------------------------------------------------------------------
    def separar_real_imaginario(self):
        separada = ajustar(
            MathTex(
                "e^{ix}", "=",
                r"\left(1-\frac{x^2}{2!}+\frac{x^4}{4!}-\cdots\right)"
                r"+i\left(x-\frac{x^3}{3!}+\cdots\right)",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(self.eq, separada, run_time=1.8))
        self.eq = separada
        self.wait(1.0)

    # ------------------------------------------------------------------
    # 5) As duas séries são velhas conhecidas: cos x e sin x
    # ------------------------------------------------------------------
    def formula_de_euler(self):
        linha1 = MathTex(r"\cos x=1-\frac{x^2}{2!}+\cdots", color=AZUL, font_size=30)
        linha2 = MathTex(r"\sin x=x-\frac{x^3}{3!}+\cdots", color=AZUL, font_size=30)
        linhas = VGroup(linha1, linha2).arrange(DOWN, buff=0.3)
        carta = cartao(linhas, "Reconheça as séries")
        carta.move_to(UP * 2.8)

        # As duas séries entram em cascata (LaggedStart)
        self.play(
            LaggedStart(
                FadeIn(carta[0]),
                FadeIn(carta[1], shift=DOWN * 0.2),
                lag_ratio=0.35,
                run_time=1.8,
            )
        )
        self.play(destacar(self.eq[2]))
        self.wait(0.8)

        # A Fórmula de Euler emerge
        formula = ajustar(
            MathTex("e^{ix}", "=", r"\cos x+i\,\sin x", color=BRANCO)
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, formula),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.eq = formula
        self.wait(1.2)

    # ------------------------------------------------------------------
    # 6) Avaliando no ângulo mais famoso: x = π
    # ------------------------------------------------------------------
    def avaliar_em_pi(self):
        nota = MathTex(r"\cos\pi=-1,\qquad\sin\pi=0", color=AZUL, font_size=32)
        carta = cartao(nota, "Avalie em x = π")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq[2]))
        self.wait(0.6)

        avaliada = ajustar(MathTex(r"e^{i\pi}", "=", "-1", color=BRANCO))
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, avaliada),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.eq = avaliada
        self.wait(1.0)

    # ------------------------------------------------------------------
    # 7) A Identidade de Euler em verde com glow
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex(r"e^{i\pi}+1", "=", "0", color=VERDE, font_size=64)
        self.play(TransformMatchingTex(self.eq, resultado, run_time=1.5))

        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))
        self.wait(0.5)

        nota = Text("e, i, π, 1 e 0 — juntos numa só equação", font_size=22, color=CINZA)
        nota.move_to(resultado.get_center() + DOWN * 1.8)
        self.play(FadeIn(nota, shift=UP * 0.2, run_time=1.2))
        self.wait(2.6)
        self.play(FadeOut(VGroup(luz, resultado, nota), run_time=1.2))
