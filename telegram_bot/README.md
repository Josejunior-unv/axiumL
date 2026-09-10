# Assistente pessoal no Telegram

Um bot de uso pessoal que **conversa**, **guarda coisas** e **lembra dos compromissos**.
A pessoa escreve do jeito que fala e ele resolve:

> — dentista quinta às 15h
> — Anotado ✅ dentista · 🕒 quinta-feira, 17/09 às 15:00 (nº 4 · te aviso antes)

> — anota que o wifi do escritório é casa123
> — Guardado 📝

> — o que eu tenho amanhã?
> — Amanhã: 09:00 academia e 15:00 dentista. Só isso. 🙂

Meia hora antes de cada compromisso (dá para mudar) chega um lembrete com botões de
**Feito** e **adiar**. E toda manhã, um resumo do dia.

## O que ele faz

| | |
|---|---|
| 🗓 **Agenda** | criar, listar, remarcar, concluir e cancelar compromissos; repetição diária, semanal ou mensal |
| ⏰ **Lembretes** | aviso antes da hora + na hora, lembretes soltos ("me lembra de tomar o remédio às 22h") e resumo diário |
| 📝 **Notas** | guardar qualquer coisa e buscar depois por palavra |
| 💬 **Conversa** | entende linguagem natural via Claude e usa as mesmas funções dos comandos |
| 🔒 **Particular** | o bot se tranca na primeira pessoa que falar com ele; os outros levam um "não" |

Tudo fica em **um arquivo SQLite** na sua máquina. Nada de banco externo.

## Instalação

**1. Crie o bot no Telegram.** Fale com o [@BotFather](https://t.me/BotFather), mande
`/newbot`, escolha nome e usuário. Ele devolve um token parecido com
`8123456789:AAF...`.

**2. Instale as dependências.**

```bash
cd telegram_bot
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure.**

```bash
cp .env.exemplo .env
```

Abra o `.env` e preencha:

- `TELEGRAM_TOKEN` — o token do passo 1 (obrigatório).
- `ANTHROPIC_API_KEY` — chave da [API da Anthropic](https://console.anthropic.com).
  Opcional: sem ela o bot continua agendando e anotando, só conversa menos (veja
  *Modo sem IA*).
- `TELEGRAM_CHATS_PERMITIDOS` — pode deixar vazio. O bot é de uma pessoa só: quem
  mandar a primeira mensagem vira o dono e ninguém mais consegue usar. Preencha
  apenas se quiser fixar o id na mão ou liberar para duas pessoas (o id sai no
  [@userinfobot](https://t.me/userinfobot)).

> ⚠️ Mande o `/start` você mesma antes de divulgar o usuário do bot: é a primeira
> mensagem que fecha o cadeado.

**4. Rode.**

```bash
python run.py
```

Agora é só abrir a conversa do bot no Telegram e mandar `/start`.

## Usando

Fale normalmente — ou use os comandos, se preferir:

```
/agendar <o quê> <quando>     ex.: /agendar reunião com a Ana sexta 10h
/agenda [hoje|amanha|semana|tudo]
/adiar <nº> <novo horário>    ex.: /adiar 3 amanhã 9h
/concluir <nº>   /cancelar <nº>
/lembrete <o quê> <quando>    aviso solto, sem entrar na agenda

/anotar <texto>   /notas [busca]   /apagar <nº>

/config     ver preferências
/fuso America/Sao_Paulo
/resumo 08:00   (ou /resumo off)
/aviso 30       minutos de antecedência dos lembretes
/limpar         esquece o histórico da conversa (agenda e notas ficam)
```

Datas que ele entende: `hoje`, `amanhã`, `depois de amanhã`, `sexta`, `segunda que vem`,
`15/03`, `dia 10`, `20 de novembro`, `às 15h`, `15h30`, `meio-dia`, `de manhã`,
`daqui a 2 horas`, `todo dia às 7h`, `toda segunda`, `todo mês`, e `me avisa 1h antes`.

## Deixando ligado o tempo todo

Os lembretes só saem com o processo rodando. Em um servidor Linux, o jeito mais
simples é um serviço do systemd (`/etc/systemd/system/assistente.service`):

```ini
[Unit]
Description=Assistente pessoal no Telegram
After=network-online.target

[Service]
Type=simple
User=SEU_USUARIO
WorkingDirectory=/caminho/para/axiumL/telegram_bot
ExecStart=/caminho/para/axiumL/telegram_bot/.venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now assistente
journalctl -u assistente -f      # acompanhar os logs
```

Se o bot ficar fora do ar, nada se perde: a fila de lembretes está no banco e é
reprocessada ao voltar (avisos com mais de 6 horas de atraso são descartados para
não inundar o chat).

**Backup:** copie `dados/assistente.db` (é o arquivo com tudo).

**Trocar o dono** (bot travado no chat errado, celular novo com outra conta):

```bash
sqlite3 dados/assistente.db "DELETE FROM configuracao WHERE chave='dono_chat_id'"
```

O próximo chat que falar com ele assume. Para não depender disso, basta pôr o id
certo em `TELEGRAM_CHATS_PERMITIDOS`, que tem prioridade sobre o cadeado
automático.

## Modo sem IA

Sem `ANTHROPIC_API_KEY` o bot ainda:

- entende datas em português e cria compromissos a partir de texto solto;
- guarda como nota o que não tiver data;
- responde a todos os comandos e envia todos os lembretes.

O que muda é que ele não conversa nem responde perguntas abertas. Com a chave,
o Claude (`claude-opus-5` por padrão) usa exatamente as mesmas funções dos comandos —
não existe um caminho paralelo de dados. Para gastar menos, dá para trocar o modelo
ou o esforço no `.env` (`BOT_MODELO`, `BOT_ESFORCO`).

> As mensagens enviadas em conversa livre vão para a API da Anthropic para gerar a
> resposta. Comandos, notas e a agenda ficam só no seu banco local. Evite guardar
> senhas e dados de cartão aqui — o arquivo `.db` não é criptografado.

## Estrutura

```
telegram_bot/
├── run.py                    # sobe o bot
├── assistente/
│   ├── config.py             # variáveis de ambiente / .env
│   ├── db.py                 # esquema SQLite e conversão de datas UTC
│   ├── datas.py              # interpreta "sexta às 15h" e afins
│   ├── servicos.py           # regras: agenda, lembretes, notas, preferências
│   ├── lembretes.py          # fila de disparo, recorrência e resumo diário
│   ├── ia.py                 # conversa com o Claude + ferramentas
│   └── bot.py                # comandos do Telegram e laço de lembretes
└── tests/                    # 64 testes, sem rede
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

64 testes, nenhum deles chamando a API ou o Telegram — a conversa é exercitada com
um cliente falso.
