#!/bin/sh

export TERM=xterm

echo "⏳ Aguardando Postgres iniciar..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ Postgres está no ar!"

echo "📦 Rodando migrations..."
alembic upgrade head

echo "🚀 Iniciando aplicação..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000