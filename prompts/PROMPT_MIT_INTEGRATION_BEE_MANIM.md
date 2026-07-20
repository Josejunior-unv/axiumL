# Prompt para Claude Code — MIT Integration Bee

> **Contexto**: Esta animação deve recriar uma questão proveniente do PDF público disponibilizado pelo **MIT Integration Bee**, produzindo um vídeo vertical cinematográfico em **Manim Community Edition**.

## Objetivo

Crie um projeto completo em **Python + ManimCE** para um vídeo **1080x1920 (9:16)** a **240 FPS**.

### Questão

\[
I_1=\int_0^{\pi/2}\sin(x)\sin(2x)\sin(3x)\,dx
\]

## Resolução (recriar exatamente)

1. Utilize a identidade

\[
\sin A\sin B=\frac{\cos(A-B)-\cos(A+B)}2
\]

com \(A=x\) e \(B=2x\),

\[
\sin(x)\sin(2x)=\frac{\cos(x)-\cos(3x)}2.
\]

2. Substitua na integral:

\[
I_1=-\frac12\int_0^{\pi/2}(\cos(3x)-\cos x)\sin(3x)\,dx.
\]

3. Expanda:

\[
=-\frac12\int_0^{\pi/2}\left(\sin(3x)\cos(3x)-\sin(3x)\cos x\right)dx.
\]

4. Aplique

\[
\sin A\cos A=\frac12\sin(2A)
\]

e

\[
\sin A\cos B=\frac12[\sin(A+B)+\sin(A-B)].
\]

Obtendo

\[
-\frac14\int_0^{\pi/2}\left(\sin6x-\sin4x-\sin2x\right)\,dx.
\]

5. Integre termo a termo:

\[
-\frac14\left[-\frac16\cos6x+\frac14\cos4x+\frac12\cos2x\right]_0^{\pi/2}.
\]

6. Avalie os limites.

7. Simplifique cuidadosamente até

\[
\boxed{I_1=-\frac16.}
\]

# Storyboard

- Introdução com o texto **"MIT Integration Bee"** e subtítulo **"Official Problem"**.
- Mostrar a integral sendo escrita.
- Destacar cada identidade antes de aplicá-la.
- Utilizar exclusivamente `TransformMatchingTex`, `ReplacementTransform`, `Circumscribe`, `LaggedStart`, `AnimationGroup`, `Write`, `FadeIn`, `FadeOut`.
- Nunca usar screenshots.
- Toda a matemática em MathTex.
- Câmera com zooms suaves.
- Fundo #0D1117.
- Resultado final em verde com glow.
- Duração entre 40 e 55 segundos.
- Comentários explicando cada trecho do código.
- Projeto modular (main.py, scenes.py, animations.py, config.py, colors.py, README.md).

