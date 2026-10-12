# Agente text-to-SQL com Claude

Pergunte em português, receba a resposta com números e a consulta SQL que a
gerou. O agente usa o **Claude** (`claude-opus-5-5`) com *tool use* para
explorar o esquema, escrever SQL, ler erros e corrigir, sobre o banco de uma
loja online fictícia. Durante a execução, a CLI mostra cada ferramenta que o
agente usa (`· executar_sql SELECT ...`), então dá para acompanhar o raciocínio
dele até a resposta.

## Como funciona

```
pergunta ──► Claude ──► ferramenta (listar_tabelas | descrever_tabela | executar_sql)
               ▲                                │
               └────────── resultado ◄──────────┘   (repete até ter a resposta)
```

- **Laço de ferramentas** (`agente_sql/agente.py`): o modelo decide o que
  consultar. O código executa as ferramentas e devolve os resultados. Erros de
  SQL voltam como `is_error`, e o modelo corrige sozinho. Chamadas paralelas
  voltam juntas numa só mensagem.
- **Conversa com memória**: dá para perguntar "e em 2024?" logo depois. Se uma
  pergunta falhar, ela sai do histórico e a conversa continua válida.
- **Ferramentas com `strict: true`**: os argumentos sempre batem com o esquema.
- **Recusa com reserva**: as requisições usam `fallbacks: "default"` (beta
  `server-side-fallback-2026-07-01`). Se o modelo recusar por engano, a própria
  API tenta de novo no modelo reserva recomendado.
- **Cache de prompt** (`cache_control`): instruções e ferramentas, que se
  repetem a cada passo, saem do cache.

### Segurança: o agente só lê

O SQL vem de um modelo, então o banco precisa se proteger sozinho. São três
camadas independentes (`agente_sql/ferramentas.py`):

1. a conexão abre o arquivo em **`mode=ro`**, e o próprio SQLite recusa escrita;
2. um **autorizador** só libera leitura. `INSERT`, `UPDATE`, `DROP`, `ATTACH`
   e `PRAGMA` de escrita são negados antes de executar;
3. um **tempo limite** interrompe consultas que demoram demais (por exemplo, uma
   CTE recursiva infinita).

Também roda uma instrução por vez e devolve no máximo 200 linhas por consulta.
Os testes tentam cada tipo de escrita e conferem que o hash do arquivo não muda.

## Avaliação

`python -m agente_sql.avaliar` roda 8 perguntas com consulta gabarito e mede a
**acurácia de execução**, a métrica de benchmarks como o Spider: a resposta
conta como certa se a última consulta do agente devolve as mesmas linhas que o
gabarito (ignorando a ordem das linhas e das colunas). As perguntas vão de
contagens simples a ticket médio com subconsulta. Cada pergunta chama a API,
então rodar o conjunto tem custo.

Os testes automatizados (`pytest`) **não** chamam a API: usam um cliente falso
com respostas roteirizadas para validar o laço, o tratamento de erros, as
chamadas paralelas e o histórico.

## Como rodar

```bash
cd projetos-ia/05-agente-text-to-sql
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # sua chave da API da Anthropic

python -m agente_sql "Quantos pedidos foram cancelados em 2025?"
python -m agente_sql                 # modo conversa ('nova' reinicia, 'sair' encerra)
python -m agente_sql --esforco high  # mais raciocínio para perguntas difíceis
python -m agente_sql.avaliar         # acurácia de execução no conjunto de perguntas
pytest                               # testes, sem chamar a API
```

Na primeira execução, o banco de exemplo é criado em `dados/loja.db`.

## O banco

| Tabela | Linhas | Conteúdo |
|---|---|---|
| `clientes` | 1.500 | nome, cidade, estado, data de cadastro |
| `produtos` | 57 | nome, categoria (Eletrônicos, Casa, Moda, Esporte, Livros, Beleza), preço |
| `pedidos` | 12.000 | cliente, data (2024–2025), status, canal (site, app, marketplace) |
| `itens_pedido` | 19.959 | produto, quantidade, preço pago com desconto |

Tem crescimento de um ano para o outro, pico em novembro e dezembro e
Black Friday. Assim as perguntas sobre tempo têm respostas interessantes.

## Animação

`animacao/index.html` explica o projeto de forma visual e interativa, com os números reais desta pasta. Um diorama isométrico em corte mostra, passo a passo, as mensagens que vão para a API (pergunta, chamadas de ferramenta, chamadas paralelas, erro e correção) e um laboratório em que você manda consultas ao banco e vê em qual camada cada uma para, com as mensagens reais de bloqueio.

Abra o arquivo no navegador; não precisa de servidor. Depois de mudar o código, refaça os dados embutidos na página com `python animacao/exportar_dados.py`.

## Estrutura

```
agente_sql/
├── banco.py         # gera o SQLite da loja
├── ferramentas.py   # acesso somente leitura (mode=ro + autorizador + tempo limite)
├── agente.py        # laço de tool use com o Claude
├── avaliar.py       # acurácia de execução com consultas gabarito
└── __main__.py      # CLI (pergunta única ou conversa)
tests/               # banco, segurança e laço do agente com cliente falso
```
