"""Configuração via variáveis de ambiente (ou arquivo .env)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def carregar_env(caminho: Path | None = None) -> None:
    """Lê um arquivo .env simples (KEY=valor) sem sobrescrever o ambiente."""
    arquivo = caminho or (RAIZ / ".env")
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        chave, valor = chave.strip(), valor.strip().strip("'\"")
        os.environ.setdefault(chave, valor)


@dataclass(frozen=True)
class Config:
    token: str
    banco: str          # caminho de arquivo (SQLite) ou URL do Postgres
    fuso_padrao: str
    chats_permitidos: frozenset[int]
    aberto: bool
    antecedencia_padrao: int
    hora_resumo_padrao: str | None
    intervalo_lembretes: int
    chave_anthropic: str | None
    modelo: str
    esforco: str
    max_tokens: int
    usar_fallback: bool
    historico_max: int
    porta: int | None   # definida pela hospedagem (Render etc.); None = sem servidor HTTP

    @property
    def ia_ativa(self) -> bool:
        return bool(self.chave_anthropic)

    @property
    def banco_visivel(self) -> str:
        """Versão do endereço do banco sem a senha, para aparecer no log."""
        return mascarar(self.banco)


def mascarar(destino: str) -> str:
    casamento = re.match(r"^(\w+://)([^@/]+)@(.*)$", destino)
    if not casamento:
        return destino
    return f"{casamento.group(1)}***@{casamento.group(3)}"


def _inteiro(nome: str, padrao: int) -> int:
    try:
        return int(os.environ.get(nome, "").strip() or padrao)
    except ValueError:
        return padrao


def _booleano(nome: str, padrao: bool) -> bool:
    bruto = os.environ.get(nome, "").strip().lower()
    if not bruto:
        return padrao
    return bruto in {"1", "true", "sim", "yes", "on"}


def carregar(env_file: Path | None = None) -> Config:
    carregar_env(env_file)

    token = os.environ.get("TELEGRAM_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Falta a variável TELEGRAM_TOKEN.\n"
            "Crie o bot no @BotFather do Telegram, copie o token e coloque em "
            f"{RAIZ / '.env'} (veja o .env.exemplo)."
        )

    permitidos = {
        int(p) for p in os.environ.get("TELEGRAM_CHATS_PERMITIDOS", "").replace(";", ",").split(",")
        if p.strip().lstrip("-").isdigit()
    }

    resumo = os.environ.get("BOT_RESUMO_DIARIO", "08:00").strip()

    return Config(
        token=token,
        # DATABASE_URL é o nome que Render, Neon, Supabase e afins usam.
        banco=(
            os.environ.get("DATABASE_URL", "").strip()
            or os.environ.get("BOT_DB", "").strip()
            or str(RAIZ / "dados" / "assistente.db")
        ),
        fuso_padrao=os.environ.get("BOT_FUSO", "America/Sao_Paulo").strip(),
        chats_permitidos=frozenset(permitidos),
        aberto=_booleano("BOT_ABERTO", False),
        antecedencia_padrao=_inteiro("BOT_ANTECEDENCIA_MIN", 30),
        hora_resumo_padrao=resumo or None,
        intervalo_lembretes=max(10, _inteiro("BOT_INTERVALO_SEGUNDOS", 30)),
        chave_anthropic=os.environ.get("ANTHROPIC_API_KEY", "").strip() or None,
        modelo=os.environ.get("BOT_MODELO", "claude-opus-5").strip(),
        esforco=os.environ.get("BOT_ESFORCO", "low").strip(),
        max_tokens=_inteiro("BOT_MAX_TOKENS", 16000),
        usar_fallback=_booleano("BOT_FALLBACK", True),
        historico_max=_inteiro("BOT_HISTORICO", 20),
        porta=_inteiro("PORT", 0) or None,
    )
