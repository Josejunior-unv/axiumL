from manim import *


class Exemplo(Scene):
    """Cena de teste para conferir que tudo funciona."""

    def construct(self):
        titulo = Text("axiumL", font_size=72)
        circulo = Circle(radius=1.5, color=BLUE)

        self.play(Write(titulo))
        self.wait(0.5)
        self.play(titulo.animate.to_edge(UP))
        self.play(Create(circulo))
        self.play(circulo.animate.set_fill(BLUE, opacity=0.5))
        self.wait(1)
