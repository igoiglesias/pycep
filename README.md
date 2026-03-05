# PyCEP

API de consulta de CEP construída com FastAPI, desenvolvida ao vivo no YouTube.

O PyCEP funciona como um wrapper inteligente sobre as APIs do [ViaCEP](https://viacep.com.br/) e [BrasilAPI](https://brasilapi.com.br/), adicionando cache local, fallback automático entre provedores e painel administrativo.

## Funcionalidades

- **Consulta de CEP** via API REST (`GET /cep/{cep}`)
- **Fallback automático**: se o ViaCEP falhar, consulta a BrasilAPI
- **Cache em memória** com `fastapi-cache2` para reduzir chamadas externas
- **Cache persistente** em SQLite para CEPs já consultados
- **Atualização em background**: CEPs com mais de 30 dias são atualizados automaticamente
- **Logging de requests**: registra IP, tempo de resposta, user-agent e erros
- **Painel Admin**: dashboard com total de consultas e top CEPs mais buscados
- **Painel de Usuário**: área autenticada para usuários comuns
- **Autenticação via JWT** com cookies HttpOnly e senhas com Argon2
- **Testes de carga** com Locust

## Estrutura do Projeto

```
pycep/
├── app.py                  # Entrypoint - registra os routers
├── bootstrap.py            # Inicialização do FastAPI, cache e templates
├── config/
│   └── config.py           # Configurações (URLs, DB, JWT, cookies)
├── databases/
│   └── db.py               # Camada de acesso ao SQLite
├── modules/
│   ├── viacep.py           # Cliente HTTP para ViaCEP
│   └── brasilapi.py        # Cliente HTTP para BrasilAPI
├── routes/
│   ├── api/
│   │   └── cep.py          # Rota da API de CEP
│   └── web/
│       ├── admin.py         # Rotas do painel admin
│       └── user.py          # Rotas do painel de usuário
├── services/
│   ├── auth.py             # Autenticação e verificação de sessão
│   ├── cep.py              # Lógica de consulta/cache de CEP
│   ├── admin.py            # Serviço do admin
│   ├── user.py             # Serviço do usuário
│   └── log.py              # Decorator de logging de requests
├── tools/
│   ├── key_builders.py     # Key builders para cache
│   ├── password.py         # Hash e verificação com Argon2
│   ├── session_error.py    # Helper para erros de sessão via cookie
│   ├── token_handler.py    # Criação e decodificação de JWT
│   └── validators.py       # Modelos Pydantic (CEP, CEP_RESPONSE)
├── scripts/
│   └── seed.py             # Seed do banco com dados iniciais
├── templates/              # Templates Jinja2 (login, dashboard, etc.)
├── static/                 # Arquivos estáticos (CSS)
├── locustfile.py           # Testes de carga com Locust
└── requirements.txt
```

## Requisitos

- Python 3.12+

## Instalação

```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd pycep

# Criar e ativar virtualenv
python -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Uso

```bash
# Iniciar o servidor
fastapi dev app.py

# Popular o banco com dados iniciais (admin e logs de exemplo)
python scripts/seed.py
```

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/cep/{cep}` | Consulta um CEP (API) |
| `GET` | `/` | Página inicial |
| `GET` | `/login` | Login de usuário |
| `GET` | `/dashboard` | Dashboard do usuário |
| `GET` | `/admin/login` | Login do admin |
| `GET` | `/admin/dashboard` | Dashboard do admin |

### Exemplo de resposta da API

```json
{
  "erro": false,
  "mensagem": null,
  "content": {
    "cep": "01310100",
    "logradouro": "Avenida Paulista",
    "complemento": "",
    "bairro": "Bela Vista",
    "localidade": "São Paulo",
    "uf": "SP",
    "ibge": "3550308",
    "gia": "1004",
    "ddd": "11",
    "siafi": "7107"
  }
}
```

### Credenciais padrão (seed)

| Perfil | Email | Senha |
|--------|-------|-------|
| Admin | admin@pycep.com | admin |
| Usuário | user@pycep.com | user |

## Testes de carga

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Acesse `http://localhost:8089` para configurar e iniciar o teste.

## Stack

- **FastAPI** - Framework web async
- **SQLite** - Banco de dados local
- **httpx** - Cliente HTTP async com suporte a HTTP/2
- **fastapi-cache2** - Cache em memória
- **PyJWT** - Tokens JWT
- **Argon2** - Hash de senhas
- **Jinja2** - Templates HTML
- **Locust** - Testes de carga
