# Projetos de IA e dados

Cinco projetos independentes de ciência de dados e IA. Cada um tem código,
testes, README com os resultados e roda com um comando. Todos geram os próprios
dados sintéticos com semente fixa: não precisa baixar nada e os números do
README se reproduzem.

| # | Projeto | O que faz | Técnicas | Animação |
|---|---|---|---|---|
| 1 | [Previsão de churn](01-previsao-churn/) | Prevê cancelamento de clientes de telecom e escolhe para quem oferecer retenção | scikit-learn, validação cruzada, limiar ótimo por lucro, importância por permutação, API FastAPI | [Fatura de Risco](01-previsao-churn/animacao/index.html) |
| 2 | [Previsão de demanda](02-previsao-demanda/) | Prevê 4 semanas de vendas diárias de 50 séries de varejo, com intervalo de 80% | gradient boosting global, perda Poisson e quantílica, features sem vazamento, backtest com origem móvel | [Quadro de Demanda](02-previsao-demanda/animacao/index.html) |
| 3 | [Detecção de fraude](03-deteccao-fraude/) | Pontua o risco de transações de cartão com orçamento limitado de alertas | features comportamentais causais, Isolation Forest, gradient boosting, PR-AUC, validação temporal | [Mesa Antifraude](03-deteccao-fraude/animacao/index.html) |
| 4 | [Sistema de recomendação](04-sistema-recomendacao/) | Recomenda filmes a partir do histórico de visualização | ALS implícito do zero em NumPy, ItemKNN, Recall@k, NDCG@k, ajuste em validação | [Gosto em Duas Tintas](04-sistema-recomendacao/animacao/index.html) |
| 5 | [Agente text-to-SQL](05-agente-text-to-sql/) | Responde perguntas em português consultando um banco SQLite | Claude com tool use, SQL somente leitura em três camadas, acurácia de execução | [Cofre de Consultas](05-agente-text-to-sql/animacao/index.html) |

## Destaques

- **Churn**: o limiar de negócio dá R$ 44 mil de lucro na campanha de retenção.
  Oferecer desconto para todos daria prejuízo de R$ 32 mil.
- **Demanda**: WAPE de 0,257 contra 0,328 da melhor referência simples. Na
  Black Friday, o modelo previu 2.448 unidades para 2.573 vendidas.
- **Fraude**: revisando só 0,5% das transações, o modelo pega 85% das fraudes,
  contra 17% das regras de negócio.
- **Recomendação**: o ALS acerta mais que o dobro da referência de popularidade
  (NDCG@10 de 0,120 contra 0,050).
- **Text-to-SQL**: o agente não consegue escrever no banco. Os testes tentam
  `DROP`, `UPDATE`, `ATTACH` e outras escritas e conferem que o arquivo fica
  intacto.

## Animações

Cada projeto tem uma animação interativa em `animacao/index.html`, com identidade visual própria e os números reais do projeto: uma fatura de operadora, um quadro de horários de loja, um dossiê impresso como papel-moeda, um cartaz em risografia e um diorama isométrico em corte. Elas combinam 2D e 3D (superfícies, calendários e nuvens de pontos que giram com o mouse ou o dedo), funcionam no celular e respeitam a preferência por menos movimento. Quatro delas seguem o tema claro ou escuro do sistema; o cartaz em risografia é sempre claro, porque a sobreposição de tintas só funciona sobre papel. Basta abrir o arquivo no navegador.

## Vídeos

As animações também viram vídeo (MP4, 1920 × 1080, 30 fps): um por projeto e um completo, com abertura e encerramento. O script `video/gravar.js` abre cada página com um relógio controlado, avança 1/30 s por quadro, encena as interações (o simulador, os cortes 3D, o limiar, as consultas barradas no cofre) e entrega os quadros ao ffmpeg. Por isso o vídeo sai liso mesmo com captura lenta.

```bash
npm install playwright && npx playwright install chromium   # uma vez
node projetos-ia/video/gravar.js                              # tudo; ou: churn, demanda, fraude, recomendacao, cofre
```

Os arquivos saem em `media/videos/projetos-ia/`, pasta que o git ignora.

### Reels para o Instagram

`video/reels.js` grava as mesmas animações em pé (1080 × 1920), no layout de celular, com uma cartela de abertura que serve de capa e uma de encerramento. O topo e a base do quadro ficam lisos, porque é ali que o Instagram desenha título, legenda e botões.

Cada reel tem trilha própria, composta por `video/trilhas/compor.py` no tamanho exato do vídeo:

| Projeto | Trilha |
|---|---|
| Fatura de Risco | 96 bpm, ré menor: pulso eletrônico limpo, arpejo com eco |
| Quadro de Demanda | 120 bpm: nu-disco, baixo em oitavas, guitarra funk e cordas |
| Mesa Antifraude | 84 bpm com swing: jazz noir, vassourinha, contrabaixo andando e vibrafone |
| Gosto em Duas Tintas | 90 bpm: lo-fi com chiado de disco; marimba e flauta se respondem, uma tinta cada |
| Cofre de Consultas | 110 bpm: synthwave, arpejo que abre o filtro e cliques de fechadura |

O roteiro de cada reel é medido em compassos da sua trilha, então as trocas de cena caem na cabeça do compasso, com prato ou virada. A introdução e o respiro do meio ficam mais baixos, e a mixagem sai em −14 LUFS com pico abaixo de −1 dBTP, o nível que o Instagram usa. Os timbres eletrônicos são sintetizados em NumPy; os acústicos vêm do banco FluidR3_GM (licença MIT), tocado pelo FluidSynth.

```bash
sudo apt install fluidsynth fluid-soundfont-gm ffmpeg               # uma vez
pip install -r projetos-ia/video/trilhas/requirements.txt          # uma vez
node projetos-ia/video/reels.js                                      # os cinco; ou um nome, como no gravar.js
node projetos-ia/video/reels.js --previa cofre                       # só JPEGs a cada 0,5 s, para ajustar o quadro
```

Saem em `media/videos/projetos-ia/reels/`, com a trilha também separada em `.m4a`. Se o Python com as bibliotecas não for o `python3` do sistema, aponte a variável `PYTHON` para ele.

## Como rodar

Cada pasta é autocontida (Python 3.10+):

```bash
cd projetos-ia/01-previsao-churn
pip install -r requirements.txt
pytest
```

O README de cada projeto traz os comandos de treino e avaliação. A integração
contínua (`.github/workflows/projetos-ia.yml`) roda os testes dos cinco a cada
mudança nesta pasta.
