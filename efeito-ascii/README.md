# Efeito ASCII — preset Forest

Recriação em **Canvas2D puro** do efeito ASCII, sem nenhuma biblioteca.

| Arquivo | O que faz |
| --- | --- |
| `motor.js` | Parâmetros, conjuntos de caracteres, amostragem, Sobel e as 25 formas |
| `pipeline.js` | Os 8 passos: fundo, grade, formas, cor, pós-efeitos, luzes, máscara |
| `pagina.js` | Cena de origem, laço de animação e os controles |
| `index.html` | A página |

## Os 25 modos

characters, dither, mosaic, pixel, dots, cross, diamond, voxel, lego, mixed,
lines, diagonal, braille, disco, hexdump, matrix, rings, hearts, stars,
hexagons, triangles, bubbles, hatch, contour, halfblocks.

## Sobre a foto de origem

A especificação sugeria imagens do Unsplash, mas **imagens externas são
bloqueadas por CSP** no ambiente onde a página roda — não carregariam. Então a
cena de floresta é **gerada proceduralmente** (camadas de árvores, névoa e sol
difuso) e há um botão para carregar a sua própria foto, que fica no aparelho e
não sai dele.

## Dois ajustes em relação à especificação

1. **`bgDim` (novo, padrão 88).** Sem escurecer o fundo, os glifos saem na mesma
   cor do que está atrás deles e o desenho some. O parâmetro escurece a camada
   de fundo para a arte ler na frente.
2. **Escala do desfoque.** `blurAmount` estava virando raio dividido por 4, o
   que a 30 dava 7,5px e apagava glifos de 10px. Passou a dividir por 10: o
   tilt-shift continua amaciando, sem destruir a grade.

Os dois foram encontrados medindo o contraste local numa faixa nítida da
imagem — com o mapeamento antigo dava 2,4; com o novo, 5,9.
