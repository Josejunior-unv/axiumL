"""Cena principal: resolução da integral do MIT Integration Bee.

    I1 = ∫₀^{π/2} sin(x) sin(2x) sin(3x) dx  =  1/6

Vídeo vertical 9:16, fundo #0D1117, câmera com zooms suaves.
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


def ajustar(eq: MathTex) -> MathTex:
    """Reduz a equação se ela for mais larga que o enquadramento útil."""
    if eq.width > LARGURA_MAXIMA:
        eq.scale_to_fit_width(LARGURA_MAXIMA)
    return eq


def cartao(tex: VGroup) -> VGroup:
    """Monta um cartão translúcido para exibir identidades trigonométricas."""
    moldura = SurroundingRectangle(
        tex,
        color=AZUL,
        buff=0.3,
        corner_radius=0.14,
        stroke_width=1.5,
        fill_color=AZUL,
        fill_opacity=0.06,
    )
    return VGroup(moldura, tex)


class MITIntegrationBee(MovingCameraScene):
    """Storyboard completo, na ordem exigida pelo briefing."""

    def construct(self):
        self.introducao()
        self.escrever_integral()
        self.primeira_identidade()
        self.expandir()
        self.identidades_produto_soma()
        self.integrar_termo_a_termo()
        self.avaliar_limites()
        self.resultado_final()

    # ------------------------------------------------------------------
    # 1) Introdução — título dourado e subtítulo
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
                "I_1", "=", r"\int_0^{\pi/2}",
                r"\sin(x)\sin(2x)", r"\sin(3x)", r"\,dx",
                color=BRANCO,
            )
        )
        self.play(Write(self.eq, run_time=2.5))
        self.wait(0.6)
        # Zoom suave de aproximação (cinematográfico)
        self.play(zoom_suave(self.camera.frame, ORIGIN, 0.82, run_time=1.6))

    # ------------------------------------------------------------------
    # 3) Identidade produto→soma aplicada a sin(x)sin(2x)
    # ------------------------------------------------------------------
    def primeira_identidade(self):
        identidade = MathTex(
            r"\sin A\sin B", "=", r"\frac{\cos(A-B)-\cos(A+B)}{2}",
            color=AZUL, font_size=34,
        )
        identidade.move_to(UP * 2.6)
        carta = cartao(identidade)

        # Destaca o trecho da integral onde a identidade será aplicada
        self.play(FadeIn(carta, shift=DOWN * 0.3, run_time=1.2))
        self.play(destacar(self.eq[3]))
        self.wait(0.4)

        # A identidade geral vira o caso particular A = x, B = 2x
        aplicada = MathTex(
            r"\sin(x)\sin(2x)", "=", r"\frac{\cos(x)-\cos(3x)}{2}",
            color=AZUL, font_size=34,
        )
        aplicada.move_to(identidade)
        self.play(ReplacementTransform(identidade, aplicada, run_time=1.4))
        carta = VGroup(carta[0], aplicada)
        self.wait(0.8)

        # Substituição na integral principal
        nova = ajustar(
            MathTex(
                "I_1", "=", r"-\frac{1}{2}", r"\int_0^{\pi/2}",
                r"\left(\cos(3x)-\cos(x)\right)", r"\sin(3x)", r"\,dx",
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
    # 4) Distribui sin(3x) dentro dos parênteses
    # ------------------------------------------------------------------
    def expandir(self):
        nova = ajustar(
            MathTex(
                "I_1", "=", r"-\frac{1}{2}", r"\int_0^{\pi/2}",
                r"\left(\sin(3x)\cos(3x)-\sin(3x)\cos(x)\right)", r"\,dx",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(self.eq, nova, run_time=1.6))
        self.eq = nova
        self.wait(0.9)

    # ------------------------------------------------------------------
    # 5) Duas identidades produto→soma, exibidas juntas num cartão
    # ------------------------------------------------------------------
    def identidades_produto_soma(self):
        id_a = MathTex(
            r"\sin A\cos A", "=", r"\frac{1}{2}\sin(2A)",
            color=AZUL, font_size=32,
        )
        id_b = MathTex(
            r"\sin A\cos B", "=", r"\frac{1}{2}\left[\sin(A+B)+\sin(A-B)\right]",
            color=AZUL, font_size=32,
        )
        grupo = VGroup(id_a, id_b).arrange(DOWN, buff=0.35)
        grupo.move_to(UP * 2.6)
        ajustar(grupo)
        carta = cartao(grupo)

        # As duas identidades entram em cascata (LaggedStart)
        self.play(
            LaggedStart(
                FadeIn(carta[0]),
                FadeIn(id_a, shift=DOWN * 0.2),
                FadeIn(id_b, shift=DOWN * 0.2),
                lag_ratio=0.35,
                run_time=2.0,
            )
        )
        # Destaca o integrando inteiro, que será reescrito como soma de senos
        self.play(destacar(self.eq[4]))
        self.wait(0.5)

        nova = ajustar(
            MathTex(
                "I_1", "=", r"-\frac{1}{4}", r"\int_0^{\pi/2}",
                r"\left(\sin 6x-\sin 4x-\sin 2x\right)", r"\,dx",
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
        self.wait(0.8)

    # ------------------------------------------------------------------
    # 6) Primitiva de cada termo
    # ------------------------------------------------------------------
    def integrar_termo_a_termo(self):
        nova = ajustar(
            MathTex(
                "I_1", "=", r"-\frac{1}{4}",
                r"\left[-\frac{1}{6}\cos 6x+\frac{1}{4}\cos 4x"
                r"+\frac{1}{2}\cos 2x\right]_0^{\pi/2}",
                color=BRANCO,
            )
        )
        # Afasta levemente a câmera para a expressão mais larga respirar
        self.play(zoom_suave(self.camera.frame, ORIGIN, 1.1, run_time=1.2))
        self.play(TransformMatchingTex(self.eq, nova, run_time=2.0))
        self.eq = nova
        self.wait(1.1)

    # ------------------------------------------------------------------
    # 7) Avaliação nos limites e simplificação
    # ------------------------------------------------------------------
    def avaliar_limites(self):
        # Em x = π/2 o colchete vale -1/12; em x = 0 vale 7/12
        avaliada = ajustar(
            MathTex(
                "I_1", "=", r"-\frac{1}{4}",
                r"\left[-\frac{1}{12}-\frac{7}{12}\right]",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(self.eq, avaliada, run_time=1.8))
        self.wait(1.0)

        simplificada = ajustar(
            MathTex(
                "I_1", "=", r"-\frac{1}{4}", r"\left(-\frac{2}{3}\right)",
                color=BRANCO,
            )
        )
        self.play(TransformMatchingTex(avaliada, simplificada, run_time=1.5))
        self.eq = simplificada
        self.wait(0.8)

    # ------------------------------------------------------------------
    # 8) Resultado final em verde, com glow e zoom de encerramento
    # ------------------------------------------------------------------
    def resultado_final(self):
        resultado = MathTex("I_1", "=", r"\frac{1}{6}", color=VERDE, font_size=64)
        self.play(TransformMatchingTex(self.eq, resultado, run_time=1.5))

        # Zoom final de aproximação sobre o resultado
        self.play(zoom_suave(self.camera.frame, resultado.get_center(), 0.72, run_time=1.6))

        # Glow verde ao redor da resposta
        luz = brilho(resultado, VERDE)
        self.play(FadeIn(luz, scale=1.08, run_time=1.5))
        self.wait(2.5)
        self.play(FadeOut(VGroup(luz, resultado), run_time=1.2))
