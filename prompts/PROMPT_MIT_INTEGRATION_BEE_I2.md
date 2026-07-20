# Prompt Claude Code ... 
## Questão
\[
I_2=\int_0^{\pi/2}\sin^3(2x)\cos x\,dx
\]

## Resolução (em português)

1. Escreva \(\sin(2x)=2\sin x\cos x\).

2. Então:
\[
\sin^3(2x)=(2\sin x\cos x)^3=8\sin^3x\cos^3x.
\]

Logo,

\[
I_2=8\int_0^{\pi/2}\sin^3x\cos^4x\,dx.
\]

3. Reescreva \(\sin^2x=1-\cos^2x\):

\[
\sin^3x=\sin x(1-\cos^2x).
\]

Assim,

\[
I_2=8\int_0^{\pi/2}\cos^4x(1-\cos^2x)\sin x\,dx.
\]

4. Faça a substituição

\[
t=\cos x,\qquad dt=-\sin x\,dx.
\]

Quando \(x=0,t=1\); quando \(x=\pi/2,t=0\).

5. A integral torna-se

\[
I_2=-8\int_1^0 t^4(1-t^2)\,dt
=8\int_0^1(t^4-t^6)\,dt.
\]

6.

\[
8\left[\frac{t^5}{5}-\frac{t^7}{7}\right]_0^1
=8\left(\frac15-\frac17\right)
=\frac{16}{35}.
\]

Resultado final:

\[
I_2=\frac{16}{35}.
\]

Instruções: vídeo vertical 1080x1920, 240 FPS, ManimCE, toda matemática em MathTex, storyboard cinematográfico semelhante ao prompt anterior, em português.
