# Imagem do assistente. Serve para qualquer lugar que rode container
# (Railway, Fly.io, Koyeb, Render, ou um VPS com docker).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # O banco fica fora do código: aponte um volume para /dados,
    # senão a agenda some a cada deploy.
    BOT_DB=/dados/assistente.db

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /dados
VOLUME ["/dados"]

# Um teste de fumaça: se o código não importar, a imagem falha aqui e não no ar.
RUN python -c "import assistente.bot, assistente.ia"

CMD ["python", "run.py"]
