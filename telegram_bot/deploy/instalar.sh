#!/usr/bin/env bash
#
# Instala (ou atualiza) o assistente em um servidor Ubuntu/Debian novo.
#
#   bash instalar.sh
#
# Pode ser rodado de novo à vontade: atualiza o código, as dependências e
# reinicia o serviço, sem mexer no .env nem no banco.
#
# Variáveis opcionais:
#   REPO=...     endereço do git      (padrão: este repositório)
#   BRANCH=...   branch a usar        (padrão: a principal do repositório)
#   DESTINO=...  onde clonar          (padrão: ~/axiumL)
#   SERVICO=...  nome do serviço      (padrão: assistente)

set -euo pipefail

REPO="${REPO:-https://github.com/Josejunior-unv/axiumL.git}"
DESTINO="${DESTINO:-$HOME/axiumL}"
SERVICO="${SERVICO:-assistente}"
PROJETO="$DESTINO/telegram_bot"

msg()   { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
aviso() { printf '\033[1;33m!!  %s\033[0m\n' "$*"; }

SUDO=""
if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
fi

definir() {  # definir CHAVE valor  -> grava no .env sem quebrar com / e $
    local chave="$1" valor="${2:-}"
    [ -z "$valor" ] && return 0
    python3 - "$PROJETO/.env" "$chave" "$valor" <<'PY'
import pathlib, sys
arquivo, chave, valor = sys.argv[1], sys.argv[2], sys.argv[3]
caminho = pathlib.Path(arquivo)
linhas, achou = [], False
for linha in caminho.read_text(encoding="utf-8").splitlines():
    if linha.split("=", 1)[0].strip() == chave:
        linha, achou = f"{chave}={valor}", True
    linhas.append(linha)
if not achou:
    linhas.append(f"{chave}={valor}")
caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
PY
}

msg "1/5  Pacotes do sistema"
if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update -qq
    $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        python3 python3-venv python3-pip git sqlite3 >/dev/null
    echo "python3, git e sqlite3 prontos."
else
    aviso "Sem apt-get aqui. Garanta python3, python3-venv e git instalados."
fi

msg "2/5  Código"
if [ -d "$DESTINO/.git" ]; then
    git -C "$DESTINO" pull --ff-only
else
    git clone --depth 1 ${BRANCH:+--branch "$BRANCH"} "$REPO" "$DESTINO"
fi

msg "3/5  Dependências do Python"
python3 -m venv "$PROJETO/.venv"
"$PROJETO/.venv/bin/pip" install -q --upgrade pip
"$PROJETO/.venv/bin/pip" install -q -r "$PROJETO/requirements.txt"
echo "ambiente em $PROJETO/.venv"

msg "4/5  Configuração"
[ -f "$PROJETO/.env" ] || cp "$PROJETO/.env.exemplo" "$PROJETO/.env"
if grep -qE '^TELEGRAM_TOKEN=.+' "$PROJETO/.env"; then
    echo "Token já configurado — mantido."
elif [ -t 0 ]; then
    read -rp "Token do @BotFather: " token
    definir TELEGRAM_TOKEN "$token"
    read -rp "Chave da Anthropic (Enter para pular a conversa com IA): " chave
    definir ANTHROPIC_API_KEY "$chave"
else
    aviso "Sem terminal interativo: edite $PROJETO/.env e preencha TELEGRAM_TOKEN."
fi
chmod 600 "$PROJETO/.env"

msg "5/5  Serviço"
if command -v systemctl >/dev/null 2>&1 && [ -d /etc/systemd/system ]; then
    $SUDO tee "/etc/systemd/system/$SERVICO.service" >/dev/null <<UNIT
[Unit]
Description=Assistente pessoal no Telegram
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(id -un)
WorkingDirectory=$PROJETO
ExecStart=$PROJETO/.venv/bin/python $PROJETO/run.py
Restart=always
RestartSec=10
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
UNIT
    $SUDO systemctl daemon-reload
    $SUDO systemctl enable "$SERVICO" >/dev/null 2>&1 || true
    $SUDO systemctl restart "$SERVICO"
    sleep 2
    $SUDO systemctl --no-pager --lines=10 status "$SERVICO" || true
    cat <<FIM

Pronto. O bot sobe sozinho quando a máquina liga.

  ver os logs:   sudo journalctl -u $SERVICO -f
  parar:         sudo systemctl stop $SERVICO
  atualizar:     bash $PROJETO/deploy/instalar.sh
  backup:        copie $PROJETO/dados/assistente.db

Agora abra o Telegram e mande /start para o seu bot — a primeira
mensagem tranca o bot em quem enviou.
FIM
else
    aviso "systemd não encontrado."
    echo "Rode na mão:  $PROJETO/.venv/bin/python $PROJETO/run.py"
fi
