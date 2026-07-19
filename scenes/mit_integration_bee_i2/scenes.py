"""Cena principal: segunda integral do MIT Integration Bee.

    I2 = ∫₀^{π/2} sin³(2x) cos(x) dx  =  16/35

Vídeo vertical 9:16, fundo #0D1117, câmera com zooms suaves — mesmo
storyboard cinematográfico do vídeo I1, com textos em português.
Somente as animações permitidas pelo briefing são usadas:
TransformMatchingTex, ReplacementTransform, Circumscribe, LaggedStart,
AnimationGroup, Write, FadeIn, FadeOut (+ movimento de câmera).
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

# Largura máxima (em unidades de cena) das equações principais, para que
# caibam no enquadramento vertical mesmo com a câmera aproximada
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


class MITIntegrationBeeI2(MovingCameraScene):
    """Storyboard completo da integral I2, na ordem do briefing."""

    def construct(self):
        self.introducao()
        self.escrever_integral()
        self.seno_do_arco_duplo()
        self.pitagoras()
        self.substituicao()
        self.integrar()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo (idêntico ao vídeo I1)
    # ------------------------------------------------------------------
    def introducao(self):
        titulo = Text("MIT Integration Bee", font_size=52, color=DOURADO, weight=BOLD)
        subtitulo = Text("Official Problem", font_size=30, color=CINZA)
        subtitulo.next_to(titulo, DOWN, buff=0.4)

        self.play(Write(titulo, run_time=2.0))
        self.play(FadeIn(subtitulo, shift=UP * 0.3, run_time=1.0))
        self.wait(1.0)

        # O título encolhe e vira um cabeçalho fixo no topo do quadro
        cabecalho = Text("MIT Integration Bee", font_size=26, color=DOURADO)
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
            MathTex(
                "I_2", "=", r"\int_0^{\pi/2}",
                r"\sin^3(2x)", r"\cos x", r"\,dx",
                color=BRANCO,
            )
        )
        self.play(Write(self.eq, run_time=2.5))
        self.wait(0.6)
        # Zoom suave de aproximação (cinematográfico)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))

    # ------------------------------------------------------------------
    # 3) Seno do arco duplo: sin(2x) = 2 sin x cos x, elevado ao cubo
    # ------------------------------------------------------------------
    def seno_do_arco_duplo(self):
        identidade = MathTex(
            r"\sin(2x)", "=", r"2\sin x\cos x",
            color=AZUL, font_size=34,
        )
        carta = cartao(identidade, "Arco duplo")
        carta.move_to(UP * 2.6)

        # Destaca o sin³(2x), onde a identidade será aplicada
        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq[3]))
        self.wait(0.4)

        # Eleva a identidade ao cubo: sin³(2x) = 8 sin³x cos³x
        ao_cubo = MathTex(
            r"\sin^3(2x)", "=", r"8\sin^3 x\cos^3 x",
            color=AZUL, font_size=34,
        )
        ao_cubo.move_to(identidade)
        self.play(ReplacementTransform(identidade, ao_cubo, run_time=1.4))
        # Reagrupa moldura + rótulo + nova identidade para o FadeOut posterior
        carta = VGroup(carta[0], carta[1][0], ao_cubo)
        self.wait(0.8)

        # Substituição na integral: cos³x · cos x = cos⁴x
        nova = ajustar(
            MathTex(
                "I_2", "=", "8", r"\int_0^{\pi/2}",
                r"\sin^3 x\,\cos^4 x", r"\,dx",
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
        self.wait(0.6)

    # ------------------------------------------------------------------
    # 4) Pitágoras: sin²x = 1 - cos²x, preparando a substituição
    # ------------------------------------------------------------------
    def pitagoras(self):
        identidade = MathTex(
            r"\sin^2 x", "=", r"1-\cos^2 x",
            color=AZUL, font_size=34,
        )
        carta = cartao(identidade, "Pitágoras")
        carta.move_to(UP * 2.6)

        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq[4]))
        self.wait(0.4)

        nova = ajustar(
            MathTex(
                "I_2", "=", "8", r"\int_0^{\pi/2}",
                r"\cos^4 x\left(1-\cos^2 x\right)", r"\sin x", r"\,dx",
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
        self.wait(0.6)

    # ------------------------------------------------------------------
    # 5) Substituição t = cos x, com a troca dos limites de integração
    # ------------------------------------------------------------------
    def substituicao(self):
        linha1 = MathTex(
            r"t=\cos x,\qquad dt=-\sin x\,dx",
            color=AZUL, font_size=32,
        )
        linha2 = MathTex(
            r"x=0\ \Rightarrow\ t=1,\qquad x=\tfrac{\pi}{2}\ \Rightarrow\ t=0",
            color=AZUL, font_size=32,
        )
        linhas = VGroup(linha1, linha2).arrange(DOWN, buff=0.3)
        ajustar(linhas)
        carta = cartao(linhas, "Substituição")
        carta.move_to(UP * 2.6)

        # As duas linhas entram em cascata (LaggedStart)
        self.play(
            LaggedStart(
                FadeIn(carta[0]),
                FadeIn(carta[1], shift=DOWN * 0.2),
                lag_ratio=0.35,
                run_time=1.8,
            )
        )
        self.wait(0.6)

        # A integral vira -8 ∫₁⁰ t⁴(1-t²) dt (limites trocados)
        invertida = ajustar(
            MathTex(
                "I_2", "=", "-8", r"\int_1^0",
                r"t^4\left(1-t^2\right)", r"\,dt",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(self.eq, invertida, run_time=1.8))
        self.eq = invertida
        self.wait(0.8)

        # Invertendo os limites, o sinal volta a ser positivo
        nova = ajustar(
            MathTex(
                "I_2", "=", "8", r"\int_0^1",
                r"\left(t^4-t^6\right)", r"\,dt",
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
        self.wait(0.6)

    # ------------------------------------------------------------------
    # 6) Primitiva e avaliação nos limites
    # ------------------------------------------------------------------
    def integrar(self):
        primitiva = ajustar(
            MathTex(
                "I_2", "=", "8",
                r"\left[\frac{t^5}{5}-\frac{t^7}{7}\right]_0^1",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(self.eq, primitiva, run_time=2.0))
        self.wait(1.0)

        avaliada = ajustar(
            MathTex(
                "I_2", "=", "8",
                r"\left(\frac{1}{5}-\frac{1}{7}\right)",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(primitiva, avaliada, run_time=1.5))
        self.eq = avaliada
        self.wait(0.8)

    # ------------------------------------------------------------------
    # 7) Resultado final em verde, com glow e zoom de encerramento
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex("I_2", "=", r"\frac{16}{35}", color=VERDE, font_size=64)
        self.play(TransformMatchingTex(self.eq, resultado, run_time=1.5))

        # Zoom final de aproximação sobre o resultado
        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        # Glow verde ao redor da resposta
        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))
        self.wait(2.5)
        self.play(FadeOut(VGroup(luz, resultado), run_time=1.2))
