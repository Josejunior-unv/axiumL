"""Cena principal: a irracionalidade de √2.

Prova por contradição (redução ao absurdo), atribuída aos pitagóricos:
suponha √2 = p/q irredutível; então p e q são ambos pares — absurdo.

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
from colors import AZUL, BRANCO, CINZA, DOURADO, VERDE, VERMELHO

# Largura máxima (em unidades de cena) das equações principais
LARGURA_MAXIMA = 5.6


def ajustar(eq):
    """Reduz a equação se ela for mais larga que o enquadramento útil."""
    if eq.width > LARGURA_MAXIMA:
        eq.scale_to_fit_width(LARGURA_MAXIMA)
    return eq


def cartao(conteudo, titulo: str = "", cor=AZUL) -> VGroup:
    """Monta um cartão translúcido com título opcional e cor configurável."""
    interno = conteudo
    if titulo:
        rotulo = Text(titulo, font_size=22, color=CINZA)
        interno = VGroup(rotulo, conteudo).arrange(DOWN, buff=0.3)
    moldura = SurroundingRectangle(
        interno,
        color=cor,
        buff=0.3,
        corner_radius=0.14,
        stroke_width=1.5,
        fill_color=cor,
        fill_opacity=0.06,
    )
    return VGroup(moldura, interno)


class Raiz2Irracional(MovingCameraScene):
    """A prova por absurdo mais famosa da matemática."""

    def construct(self):
        self.introducao()
        self.hipotese_do_absurdo()
        self.elevar_ao_quadrado()
        self.p_e_par()
        self.q_tambem_e_par()
        self.contradicao()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo
    # ------------------------------------------------------------------
    def introducao(self):
        titulo = Text("√2 é Irracional", font_size=52, color=DOURADO, weight=BOLD)
        subtitulo = Text("Prova por Contradição", font_size=30, color=CINZA)
        subtitulo.next_to(titulo, DOWN, buff=0.4)

        self.play(Write(titulo, run_time=2.0))
        self.play(FadeIn(subtitulo, shift=UP * 0.3, run_time=1.0))
        self.wait(1.0)

        cabecalho = Text("√2 é Irracional", font_size=26, color=DOURADO)
        cabecalho.move_to(UP * 5.0)
        self.play(
            AnimationGroup(
                ReplacementTransform(titulo, cabecalho),
                FadeOut(subtitulo, shift=DOWN * 0.3),
                run_time=1.2,
            )
        )

    # ------------------------------------------------------------------
    # 2) Hipótese do absurdo: √2 seria uma fração irredutível p/q
    # ------------------------------------------------------------------
    def hipotese_do_absurdo(self):
        nota = MathTex(
            r"\frac{p}{q}\ \text{irredutível:}\ \mathrm{mdc}(p,q)=1",
            color=AZUL, font_size=32,
        )
        carta = cartao(nota, "Suponha, por absurdo")
        carta.move_to(UP * 2.8)

        self.eq = ajustar(MathTex(r"\sqrt{2}", "=", r"\frac{p}{q}", color=BRANCO))
        self.play(Write(self.eq, run_time=2.0))
        self.wait(0.4)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))
        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.wait(1.0)
        self.carta_hipotese = carta

    # ------------------------------------------------------------------
    # 3) Elevando os dois lados ao quadrado
    # ------------------------------------------------------------------
    def elevar_ao_quadrado(self):
        self.play(destacar(self.eq))
        quadrado = ajustar(MathTex("2", "=", r"\frac{p^2}{q^2}", color=BRANCO))
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, quadrado),
                FadeOut(self.carta_hipotese, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.wait(0.8)

        isolado = ajustar(MathTex("p^2", "=", "2q^2", color=BRANCO))
        self.play(TransformMatchingTex(quadrado, isolado, run_time=1.5))
        self.eq = isolado
        self.wait(0.8)

    # ------------------------------------------------------------------
    # 4) p² é par ⟹ p é par ⟹ p = 2k
    # ------------------------------------------------------------------
    def p_e_par(self):
        nota = MathTex("p = 2k", color=AZUL, font_size=32)
        carta = cartao(nota, "p² é par ⟹ p é par")
        carta.move_to(UP * 2.8)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq[0]))
        self.wait(0.6)

        substituido = ajustar(MathTex("(2k)^2", "=", "2q^2", color=BRANCO))
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, substituido),
                FadeOut(carta, shift=UP * 0.3),
                run_time=1.8,
            )
        )
        self.wait(0.6)

        expandido = ajustar(MathTex("4k^2", "=", "2q^2", color=BRANCO))
        self.play(TransformMatchingTex(substituido, expandido, run_time=1.4))
        self.eq = expandido
        self.wait(0.7)

    # ------------------------------------------------------------------
    # 5) Simplificando: q² = 2k², logo q também é par
    # ------------------------------------------------------------------
    def q_tambem_e_par(self):
        simplificado = ajustar(MathTex("q^2", "=", "2k^2", color=BRANCO))
        self.play(TransformMatchingTex(self.eq, simplificado, run_time=1.5))
        self.eq = simplificado
        self.wait(0.6)
        self.play(destacar(self.eq[0]))
        self.wait(0.5)

    # ------------------------------------------------------------------
    # 6) A contradição: p e q pares, mas a fração era irredutível!
    # ------------------------------------------------------------------
    def contradicao(self):
        linha1 = Text("p e q são ambos pares…", font_size=26, color=BRANCO)
        linha2 = Text("mas a fração era irredutível!", font_size=26, color=VERMELHO)
        linhas = VGroup(linha1, linha2).arrange(DOWN, buff=0.25)
        carta = cartao(linhas, "Contradição", cor=VERMELHO)
        carta.move_to(UP * 2.8)

        self.play(
            LaggedStart(
                FadeIn(carta[0]),
                FadeIn(carta[1], shift=DOWN * 0.2),
                lag_ratio=0.35,
                run_time=1.8,
            )
        )
        self.wait(1.4)
        self.carta_contradicao = carta

    # ------------------------------------------------------------------
    # 7) Conclusão em verde com glow: √2 não é racional
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex(
            r"\therefore", r"\ \sqrt{2}", r"\notin", r"\mathbb{Q}",
            color=VERDE, font_size=64,
        )
        self.play(
            AnimationGroup(
                TransformMatchingTex(self.eq, resultado),
                FadeOut(self.carta_contradicao, shift=UP * 0.3),
                run_time=1.6,
            )
        )

        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))
        self.wait(2.5)
        self.play(FadeOut(VGroup(luz, resultado), run_time=1.2))
