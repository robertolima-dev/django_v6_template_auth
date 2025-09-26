## Django v6 Template (Python 3.13)

Estrutura base de projeto com `api_core/` e pacote `settings` (base/dev/prod),
e diretório `apps/` para apps.

### Requisitos
- Python 3.13

### Setup rápido
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --pre
python manage.py migrate
python manage.py runserver
```

### Banco de dados (Postgres)
1. Copie o arquivo de exemplo e ajuste variáveis:
```bash
cp env.example .env
```
2. Configure a `DATABASE_URL` (exemplo):
```
postgres://USER:PASSWORD@HOST:PORT/DBNAME
```
3. Rode as migrações:
```bash
python manage.py migrate
```

### Ambientes
- Desenvolvimento: `api_core.settings.dev` (padrão via `manage.py`)
- Produção: `api_core.settings.prod`

Para usar produção:
```bash
export DJANGO_SETTINGS_MODULE=api_core.settings.prod
python manage.py check --deploy
```
