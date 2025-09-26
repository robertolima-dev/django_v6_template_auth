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

---

### API

Base URLs:
- v1: `/api/v1/`
- v2: `/api/v2/` (ainda sem endpoints)

Saúde da aplicação:
- `GET /api/v1/health/` → `{ "status": "ok" }`

#### Autenticação

- Formato: JWT Bearer via `Authorization: Bearer <token>`
- Backend: `rest_framework_simplejwt.authentication.JWTAuthentication`
- Tempo de vida: 24h (configurável em `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME`)

Exemplo de header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
```

#### Endpoints v1

Prefixo: `/api/v1/`

1) Autenticação (`/api/v1/auth/`)

- `POST /api/v1/auth/login/`
  - Body:
    ```json
    { "email": "user@example.com", "password": "secret" }
    ```
  - 200 OK:
    ```json
    { "user": {"id": 1, "email": "user@example.com", ...}, "token": "<jwt>", "expired_at": 86399 }
    ```

- `POST /api/v1/auth/register/`
  - Body:
    ```json
    { "email": "user@example.com", "first_name": "Nome", "last_name": "Sobrenome", "password": "secret", "phone": "", "gender": "", "date_of_birth": "YYYY-MM-DD" }
    ```
  - 201 Created:
    ```json
    { "user": {"id": 1, ...}, "token": "<token_confirm_email>", "expired_at": 86400 }
    ```

- `POST /api/v1/auth/forgot_password/`
  - Body:
    ```json
    { "email": "user@example.com" }
    ```
  - 200 OK:
    ```json
    { "message": "Email enviado com sucesso" }
    ```
  - Observação: internamente também pode retornar `token` de teste e `expired_at` no serviço.

- `POST /api/v1/auth/reset_password/`
  - Body:
    ```json
    { "token": "<token_change_password>", "password": "nova_senha" }
    ```
  - 200 OK:
    ```json
    { "user": {"id": 1, ...}, "token": "<jwt>", "expired_at": 86399 }
    ```

- `POST /api/v1/auth/confirm_email/`
  - Body:
    ```json
    { "token": "<token_confirm_email>" }
    ```
  - 200 OK:
    ```json
    { "user": {"id": 1, ...}, "token": "<jwt>", "expired_at": 86399 }
    ```

2) Usuários (`/api/v1/users/`)

- Requer JWT em todas as rotas.
- O queryset é filtrado para o usuário autenticado.

- `GET /api/v1/users/`
  - Lista somente o próprio usuário

- `GET /api/v1/users/me/`
  - Retorna dados do usuário autenticado e o próprio token do header com tempo restante:
    ```json
    { "user": {"id": 1, ...}, "token": "<jwt>", "expired_at": 86399 }
    ```

- `GET /api/v1/users/{id}/`
- `PUT /api/v1/users/{id}/`
- `PATCH /api/v1/users/{id}/`
- `DELETE /api/v1/users/{id}/`

Campos do modelo `User` serializados em `UserSerializer` (padrão `__all__`) e, para `me`, `UserMeSerializer` (exclui `groups` e `user_permissions`).

---

### Configurações relevantes

- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` inclui JWT e sessão
- `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES = AllowAny` (endpoints específicos usam permissões próprias)
- `DEFAULT_ROUTER_TRAILING_SLASH = "/"` (as rotas terminam com `/`)

Variáveis de ambiente importantes (ver `.env.example`):
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL`
- `URL_BASE`
- Email: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- AWS (se aplicável): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

