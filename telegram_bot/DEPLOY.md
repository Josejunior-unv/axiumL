# Colocar o bot na nuvem (de graça)

Duas coisas precisam ser verdade, ou o assistente não funciona direito:

1. **Um processo ligado o tempo todo** — é ele que dispara os lembretes. Serviço que
   "dorme" quando ninguém usa não serve: o lembrete das 7h não chega.
2. **Disco que não some** — a agenda e as notas vivem em `dados/assistente.db`. Em
   várias hospedagens grátis o disco é apagado a cada reinício; sem um volume de
   verdade, ela perde tudo sem aviso.

Abaixo, as opções que atendem aos dois pontos.

## Opção A — VM grátis (recomendada)

Uma máquina virtual pequena, grátis "para sempre", com disco de verdade. O código
roda sem adaptação nenhuma e sobe sozinho quando a máquina liga.

| | Google Cloud (e2-micro) | Oracle Cloud (Always Free) |
|---|---|---|
| Preço | grátis permanente (1 instância) | grátis permanente |
| Onde | só `us-west1`, `us-central1` ou `us-east1` | várias regiões |
| Máquina | 2 vCPU compartilhadas, 1 GB RAM, 30 GB disco padrão | até 4 núcleos ARM / 24 GB |
| Cartão de crédito | exigido só para verificar identidade | idem (cobrança simbólica que é estornada) |
| Pegadinha | confirme se o IP externo entra na cobrança (costuma sair alguns dólares/mês) | derruba instância ociosa: abaixo de ~5% de CPU por 24 h, ela é parada |

Para este bot, que fica quase sempre parado esperando mensagem, o **Google Cloud
tende a dar menos dor de cabeça** — a política de ociosidade da Oracle é justamente
o caso dele.

### Passo a passo

1. Crie a conta do provedor e depois uma VM com **Ubuntu 24.04**, o tipo mais
   fraco disponível (`e2-micro` no Google) e disco padrão de 30 GB.
2. Conecte por SSH. **Dá para fazer isso pelo celular**: no Google Cloud existe um
   botão "SSH" que abre um terminal no próprio navegador; na Oracle, dá para usar o
   Cloud Shell ou um app como o Termius.
3. Cole isto no terminal da VM:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/Josejunior-unv/axiumL/master/telegram_bot/deploy/instalar.sh | bash
   ```

   Ele instala o Python, baixa o código, pergunta o token do @BotFather (e a chave
   da Anthropic, se você quiser a conversa por IA) e registra o serviço no systemd.
4. Abra o Telegram e mande `/start` para o bot. Essa primeira mensagem tranca o bot
   em quem enviou.

Depois disso:

```bash
sudo journalctl -u assistente -f    # ver o que está acontecendo
sudo systemctl restart assistente   # reiniciar
bash ~/axiumL/telegram_bot/deploy/instalar.sh   # atualizar para a versão nova
```

## Opção B — container

Serve para Railway, Fly.io, Koyeb, Render ou qualquer VPS com docker. Use o
`Dockerfile` da pasta:

```bash
docker build -t assistente .
docker run -d --name assistente --restart unless-stopped \
  -e TELEGRAM_TOKEN=... \
  -e ANTHROPIC_API_KEY=... \
  -v assistente-dados:/dados \
  assistente
```

⚠️ **O `-v` (ou o volume da plataforma montado em `/dados`) não é opcional.** Sem
ele, cada deploy zera a agenda. A imagem já vem com `BOT_DB=/dados/assistente.db`.

Nessas plataformas, confira também se o plano grátis mantém o processo ativo sem
requisições HTTP — o bot não é um site, ninguém vai "acessar" ele. Nos planos
gratuitos atuais de Render e Railway isso normalmente **não** vale para processos
de fundo.

## Opção C — sites de hospedagem grátis para bots

Existem serviços que hospedam bot de Telegram de graça e sem cartão. São rápidos de
usar, mas pense duas vezes antes:

- você entrega o **token do bot** (acesso total às conversas dele) e, se usar IA, a
  **chave da API** (que é dinheiro) a um terceiro desconhecido;
- costumam ter disco volátil — de novo, a agenda some;
- podem sumir do ar sem aviso.

Se for testar, use um bot separado e sem a chave da Anthropic.

## Cuidados que valem para qualquer opção

- **Backup:** `dados/assistente.db` é o arquivo com tudo. Copie de vez em quando.
- **Fuso:** não importa o fuso da máquina; o bot guarda tudo em UTC e mostra no fuso
  configurado no `/fuso`.
- **Custo da IA:** hospedagem grátis não deixa a API da Anthropic grátis. Cada
  conversa consome créditos. Sem `ANTHROPIC_API_KEY`, o bot continua agendando,
  lembrando e anotando — só não bate papo.
