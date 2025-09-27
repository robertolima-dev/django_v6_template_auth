#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configurações
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-api_core.settings.dev}"
export DJANGO_SETTINGS_MODULE

echo "==> Python bin: $PYTHON_BIN"
echo "==> Virtualenv: $VENV_DIR"
echo "==> Host/Port:  ${HOST}:${PORT}"
echo "==> Settings:   $DJANGO_SETTINGS_MODULE"

# 1) Virtualenv
if [ ! -d "$VENV_DIR" ]; then
  echo "==> Criando virtualenv..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 2) Dependências
if [ -f "requirements.txt" ] && [ "${SKIP_PIP:-0}" != "1" ]; then
  echo "==> Instalando dependências..."
  pip install --upgrade pip
  pip install -r requirements.txt --pre
fi

# 3) Sanidade
echo "==> Verificando projeto..."
python manage.py check

# 4) Testes (pule com SKIP_TESTS=1)
if [ "${SKIP_TESTS:-0}" != "1" ]; then
  echo "==> Rodando testes..."
  python manage.py test -v 2
else
  echo "==> Pulando testes (SKIP_TESTS=1)."
fi

# 5) Migrações
echo "==> Aplicando migrações..."
python manage.py migrate --noinput

# Fallback para apps de terceiros sem migrations declaradas e sync de tabelas
python manage.py migrate --run-syncdb --noinput || true

# Coleta de estáticos (quando desejado). Em DEBUG, o ASGI já serve static via ASGIStaticFilesHandler.
if [ "${COLLECTSTATIC:-0}" = "1" ]; then
  echo "==> Coletando estáticos..."
  python manage.py collectstatic --noinput
fi

# 6) Dependências externas (ex.: Docker) — placeholder
# Descomente se/quando houver docker-compose.yml
# if [ -f "docker-compose.yml" ] && [ "${SKIP_DOCKER:-0}" != "1" ]; then
#   echo "==> Subindo serviços Docker..."
#   docker compose up -d
# fi

# 7) Seed opcional (idempotente)
# python manage.py seed_email_templates || true

# 8) Inicialização do servidor (ASGI p/ WebSocket)
start_asgi() {
  if command -v daphne >/dev/null 2>&1; then
    echo "==> Iniciando Daphne..."
    exec daphne -b "$HOST" -p "$PORT" api_core.asgi:application
  elif command -v uvicorn >/dev/null 2>&1; then
    echo "==> Iniciando Uvicorn..."
    exec uvicorn api_core.asgi:application --host "$HOST" --port "$PORT"
  else
    echo "!! Daphne/Uvicorn não encontrados. Iniciando runserver (HTTP apenas)."
    exec python manage.py runserver "${HOST}:${PORT}"
  fi
}

start_asgi