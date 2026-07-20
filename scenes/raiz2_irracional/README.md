# √2 é Irracional — vídeo Manim

Vídeo vertical **1080x1920 (9:16)** com a prova por contradição mais
famosa da matemática (atribuída aos pitagóricos):

1. Suponha, por absurdo, $\sqrt2 = \frac{p}{q}$ com a fração irredutível
2. Eleve ao quadrado: $p^2 = 2q^2$ ⟹ $p$ é par ⟹ $p = 2k$
3. Substitua: $4k^2 = 2q^2$ ⟹ $q^2 = 2k^2$ ⟹ $q$ também é par
4. **Contradição** (cartão vermelho): a fração era irredutível!
5. Conclusão: $\therefore\ \sqrt2 \notin \mathbb{Q}$

## Como renderizar

Dentro desta pasta (`scenes/raiz2_irracional/`):

```powershell
python main.py --preview   # rápido, 540x960 @ 30 FPS
python main.py             # final, 1080x1920 @ 240 FPS
```

Saída: `media/videos/raiz2_irracional/<qualidade>/Raiz2Irracional.mp4`.

Mesmo modelo visual dos vídeos MIT Integration Bee, com um extra:
o cartão da contradição usa a cor `VERMELHO` (#F85149) adicionada
à paleta deste projeto.
