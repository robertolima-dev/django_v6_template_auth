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


### WebSocket (Django Channels)

Esta base já está preparada para ASGI e Channels. Siga os passos abaixo para habilitar e testar um endpoint WebSocket simples.

1) Dependências

```bash
pip install channels daphne channels-redis
```

Opcionalmente, adicione ao `requirements.txt`:

```text
channels>=4,<5
daphne>=4,<5
channels-redis>=4,<5
```

2) Configurações

- Adicione `channels` em `INSTALLED_APPS` (arquivo `api_core/settings/base.py`):

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "django_summernote",
    "apps.api",
    "apps.user",
    "apps.communication",
    "channels",
]
```

- Camadas de canal (já configuradas por ambiente):
  - Desenvolvimento (`api_core/settings/dev.py`): usa `InMemoryChannelLayer`.
  - Produção (`api_core/settings/prod.py`): usa Redis; defina `REDIS_URL` (ex.: `redis://localhost:6379/0`).

3) ASGI e rotas WebSocket

- O `api_core/asgi.py` já está configurado com `ProtocolTypeRouter` e `AuthMiddlewareStack`.
- As rotas WebSocket ficam em `api_core/routing.py`. Este projeto inclui um exemplo:

```python
from django.urls import path
from apps.api.consumers import EchoConsumer

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),
]
```

4) Consumer de exemplo

`apps/api/consumers.py` contém um echo simples:

```python
from channels.generic.websocket import AsyncWebsocketConsumer

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            await self.send(text_data=text_data)
```

5) Como iniciar o servidor (ASGI)

- Script do projeto (recomendado):

```bash
chmod +x start_server.sh
./start_server.sh
```

- Ou diretamente com ASGI server:

```bash
# Daphne
daphne -b 0.0.0.0 -p 8000 api_core.asgi:application

# Uvicorn (alternativa)
uvicorn api_core.asgi:application --host 0.0.0.0 --port 8000
```

6) Teste rápido com wscat

```bash
# Instale se necessário
npm i -g wscat

# Conecte ao endpoint de eco
wscat -c ws://localhost:8000/ws/echo/
```

Digite qualquer texto e você deverá receber a mesma mensagem de volta.

7) Autenticação (opcional)

- O `AuthMiddlewareStack` usa sessão (cookies). Para autenticar com sessão via `wscat`, envie o cookie:

```bash
wscat -c ws://localhost:8000/ws/echo/ -H "Cookie: sessionid=<sua_sessao>"
```

- Para JWT, é necessário criar um middleware de autenticação para WebSocket que leia o token (querystring, header ou subprotocol). O header comum seria `Authorization: Bearer <token>`.

8) Proxy/produção

- Ao usar Nginx/ELB, garanta os headers de upgrade:
  - `Upgrade: websocket`
  - `Connection: upgrade`

---

### Event Sync (produtor/consumidor via SQS)

O app `apps.event_sync` provê um fluxo de sincronização de eventos entre serviços: registra um evento localmente, envia a mensagem para uma fila (SQS) e expõe um endpoint para receber a confirmação/processamento do consumidor externo.

1) Modelo principal

Campos do modelo `EventSync` (`apps/event_sync/models.py`):

- `apps` (JSON): apps/serviços destino
- `obj_type` (str): tipo do objeto/evento (ex.: `test_event_sync`)
- `obj_data` (JSON): payload do evento
- `obj_cmd` (str): comando (`put` | `delete`)
- `sent`, `received`, `processed` (datetime): timestamps do ciclo
- `log` (text): erros/observações

2) Produção de eventos (outbound)

Use o `ProducerMsg` para criar o registro e enviar a mensagem para a fila SQS:

```python
from apps.event_sync.managers.producer_msg import ProducerMsg

ProducerMsg(
    apps={"target": ["billing", "crm"]},
    obj_type="test_event_sync",
    obj_data={"foo": "bar"},
    obj_cmd="put",
).handle_msg_sync()
```

O produtor criará um `EventSync` e enviará uma mensagem SQS no formato:

```json
{
  "apps": {"target": ["billing", "crm"]},
  "data": {
    "obj_type": "test_event_sync",
    "obj_data": {"foo": "bar", "event_id": 123},
    "obj_cmd": "put"
  },
  "timestamp": 1710000000.0
}
```

Observação: há dependências externas em `common.sqs.sqs_sync.SqSManager` (envio) que devem existir no projeto onde for usar. Ajuste seu wrapper de SQS conforme necessário.

Variáveis necessárias (SQS):

- `SQS_QUEUE_URL`: URL da fila SQS (ex.: `https://sqs.us-east-1.amazonaws.com/123456789012/my-queue`)
- Credenciais AWS (o projeto já usa `boto3`): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` e, se aplicável, `AWS_DEFAULT_REGION` (padrão do código: `us-east-1`).

Implementação atual (`common/sqs/sqs_sync.py`):

```python
class SqSManager:
    def __init__(self) -> None:
        self.sqs = boto3.client('sqs', region_name='us-east-1')
        self.queue_url = settings.SQS_QUEUE_URL

    def _send(self, msg: dict) -> None:
        self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(msg))

    @staticmethod
    def send(msg: dict) -> None:
        SqSManager()._send(msg)
```

Permissão de callback (`common/sqs/sqs_permission.py`):

```python
class IsSqsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token and token.startswith('Token '):
            token_value = token.split(' ')[1].strip()
            if token_value == str(settings.APP_KEY):
                return True
        return False
```

Para chamadas ao endpoint de sync, envie o header:

```http
Authorization: Token <APP_KEY>
```

Defina `APP_KEY` no `.env` do servidor que receberá o callback.

3) Endpoint de consumo (inbound callback)

View: `apps.event_sync.api.viewsets.EventSyncApiView` (POST). O serializer espera:

```json
{
  "obj_type": "test_event_sync",
  "obj_data": {"event_id": 123, "...": "..."},
  "obj_cmd": "put"
}
```

Permissão: `common.sqs.sqs_permission.IsSqsAuthenticated` (auth custom). Ajuste conforme sua infra (token/IP allowlist). Para testes locais sem essa permission, você pode temporariamente substituir por `AllowAny`.

Para expor a rota (exemplo em `api_core/urls.py` ou dentro de `apps/api/urls_v1.py`):

```python
from django.urls import path
from apps.event_sync.api.viewsets import EventSyncApiView

urlpatterns += [
    path("event-sync/", EventSyncApiView.as_view(), name="event-sync"),
]
```

4) Fluxo de processamento

- O consumidor externo chama `POST /api/v1/event-sync/` com o corpo acima.
- `ConsumerMsg` (`apps/event_sync/managers/consumer_msg.py`) busca o `EventSync` pelo `event_id` em `obj_data`, marca `received` e, para `obj_type == "test_event_sync"`, marca `processed`.
- Em caso de erro, o campo `log` é preenchido.

Limitações conhecidas (a melhorar):

- O `ConsumerMsg` assume que `event_id` existe e o registro foi encontrado; adicione tratamento quando `EventSync` não existir (evita `AttributeError`).
- Só há branch explícita para `obj_type == "test_event_sync"`; inclua seus tipos reais e a lógica de domínio.
- Dependências externas `common.sqs.*` devem ser providas pelo seu projeto ou adaptadas.

5) Testes locais rápidos

Produzir um evento (shell):

```bash
python manage.py shell -c "from apps.event_sync.managers.producer_msg import ProducerMsg; ProducerMsg(apps={\"target\": [\"demo\"]}, obj_type=\"test_event_sync\", obj_data={\"foo\": \"bar\"}, obj_cmd=\"put\").handle_msg_sync()"
```

Simular callback (após expor a URL):

```bash
curl -X POST http://localhost:8000/api/v1/event-sync/ \
  -H 'Content-Type: application/json' \
  -d '{"obj_type":"test_event_sync","obj_data":{"event_id":1,"foo":"bar"},"obj_cmd":"put"}'
```

Se a permission custom bloquear no ambiente local, ajuste-a temporariamente apenas para o teste.

---

## Docker (local com hot reload)

Arquivos adicionados:

- `Dockerfile.local`: imagem Python 3.13, instala `requirements.txt` e usa entrypoint com migrações + `uvicorn --reload`.
- `docker/local/entrypoint.sh`: aplica migrações (com fallback `--run-syncdb`) e inicia ASGI com hot reload.
- `docker-compose.local.yml`: serviço `web` (porta 8000) e `redis` (opcional, Channels).

Como iniciar:

- Crie o arquivo .env baseado no .env.example

```bash
docker compose -f docker-compose.local.yml up -d --build
```

Como debugar:

```bash
docker ps
docker logs <ID_CONTAINER>
```

A aplicação estará em `http://localhost:8000` com recarregamento automático (montagem do volume `./:/app`).

Variáveis úteis:

- `DJANGO_SETTINGS_MODULE=api_core.settings.dev` (padrão)
- `COLLECTSTATIC=1` para coletar estáticos dentro do container (normalmente desnecessário em dev)

Parar/limpar:

```bash
docker compose -f docker-compose.local.yml down -v
```

---

## Docker (produção)

Arquivos relevantes:

- `Dockerfile`: build de produção
- `docker/prod/entrypoint.sh`: aplica migrações, `collectstatic` e inicia Daphne
- `docker-compose.yml`: serviço `web` sem Redis (use `REDIS_URL` externo)

Como buildar e subir:

```bash
docker compose up -d --build
```

Configuração de ambiente (via `.env`):

- `DJANGO_SETTINGS_MODULE=api_core.settings.prod`
- `DATABASE_URL=postgres://USER:PASS@HOST:5432/DBNAME`
- `DJANGO_ALLOWED_HOSTS=seu.dominio.com,localhost`
- `REDIS_URL=redis://host.externo:6379/0`  # Redis gerenciado/externo
- `SQS_QUEUE_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (se Event Sync/SQS ativo)
- `APP_KEY` (para autenticar callbacks do Event Sync)

Operações comuns:

```bash
# logs
docker compose logs -f web

# executar manage.py dentro do container
docker compose exec web python manage.py shell
```
