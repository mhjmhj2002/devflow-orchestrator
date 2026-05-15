# DevFlow Orchestrator

O **DevFlow Orchestrator** é o núcleo do projeto DevFlow AI: um serviço em **Python/FastAPI** responsável por receber webhooks do GitHub, analisar o contexto do repositório e gerar planos técnicos via LLM. Este documento explica como rodar o serviço localmente, além de descrever o fluxo e a estrutura do projeto.

## Índice
- [Visão geral](#visão-geral)
- [Principais responsabilidades](#principais-responsabilidades)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Fluxo do orquestrador](#fluxo-do-orquestrador)
- [Requisitos](#requisitos)
- [Configuração de ambiente](#configuração-de-ambiente)
- [Executando localmente](#executando-localmente)
- [Endpoints úteis](#endpoints-úteis)
- [Testando o webhook](#testando-o-webhook)
- [Dicas de desenvolvimento](#dicas-de-desenvolvimento)
- [Demonstração pública com ngrok](#demonstração-pública-com-ngrok)
- [Service-aware issues (monorepo)](#service-aware-issues-monorepo)
- [Próximos passos recomendados](#próximos-passos-recomendados)

## Visão geral
O `devflow-orchestrator` recebe eventos do GitHub, normaliza o payload, monta o contexto do repositório e aciona o agente de planejamento para gerar um plano em Markdown e comentar a issue.

## Principais responsabilidades
- Receber webhooks GitHub (`/webhook/github`)
- Normalizar eventos do GitHub
- Construir contexto do repositório (detecção de linguagem/stack)
- Gerar plano técnico via agente de planejamento (OpenAI)
- Postar comentário na issue com o plano
- Endpoints auxiliares: `/health` e `/docs`

## Estrutura do projeto
Estrutura relevante dentro de `devflow-orchestrator`:

- `app/main.py` — entrypoint FastAPI
- `app/api/webhook.py` — endpoint do webhook
- `app/workflows/workflow_router.py` — roteador de workflows
- `app/workflows/planning_workflow.py` — workflow de planejamento
- `app/github/normalizer.py` — normalizador de eventos GitHub
- `app/project_context/*` — scanner, detector de stack, context builder
- `app/agents/planning_agent.py` — integração com LLM
- `app/llm/openai_client.py` — cliente OpenAI (geração de texto)
- `app/github/github_commenter.py` — postagem de comentários no GitHub
- `app/core/logger.py` — logger central (`devflow-orchestrator`)

## Fluxo do orquestrador
1. `webhook/github` recebe o payload
2. `normalizer.normalize_github_event` normaliza o evento
3. `workflow_router.route_workflow` roteia para `start_planning_workflow`
4. `context_builder.build_project_context` analisa o repositório registrado
5. `planning_agent.generate_plan` constrói prompt e chama `llm.openai_client.generate_text`
6. Plano é transformado em Markdown por `skills.plan_markdown_generator` e salvo por `skills.plan_file_writer`
7. `github.github_commenter.post_github_comment` publica o comentário na issue (ou é mockado em dev)

## Requisitos
Dependências sugeridas (adicione em `requirements.txt` no futuro):

- fastapi
- uvicorn
- pydantic
- requests
- openai

## Configuração de ambiente
Crie um `.env` (ou exporte variáveis no shell):

- `OPENAI_API_KEY` — chave da OpenAI (pode ser mockada para desenvolvimento)
- `GITHUB_TOKEN` — token para postar comentários (usar mock em demos)
- `DEVFLOW_ENV` — (opcional) `development` / `production`

> **Importante:** nunca commite chaves reais.

## Executando localmente
Passo a passo mínimo para rodar o serviço localmente (Linux/macOS):

### 1) Criar e ativar virtualenv
```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependências
**Recomendado:** usar o conjunto mínimo.

> **Atenção:** `requirements.txt` pode conter pacotes de sistema e falhar em ambientes limpos.  
> Prefira `requirements-minimal.txt` para desenvolvimento local.

```sh
# a partir da pasta devflow-orchestrator
pip install -r requirements-minimal.txt
```

Se preferir instalar pacotes individualmente:
```sh
pip install fastapi uvicorn pydantic pydantic-settings requests openai python-dotenv
```

Caso tente instalar o `requirements.txt`, é provável encontrar erros como:
```
ERROR: Could not find a version that satisfies the requirement apt-clone==0.2.1
ERROR: No matching distribution found for apt-clone==0.2.1
```

### 3) Exportar variáveis de ambiente (exemplo com mocks)
```sh
export OPENAI_API_KEY="sk_test_xxx"
export GITHUB_TOKEN="ghp_test_xxx"
export PYTHONPATH=$(pwd)
```

### 4) Rodar o servidor

Existem duas formas confiáveis de executar o servidor localmente. A primeira é
usar o modulo do Python (recomendado em terminais onde o `uvicorn` não esteja no PATH,
como o terminal do IntelliJ quando não ativa automaticamente o virtualenv):

```sh
python -m uvicorn app.main:app --reload --port 8000
```

Alternativamente há um helper script no repositório que detecta/usa o Python do
virtualenv do projeto (procura `.venv`, `venv` ou `env`) e executa o uvicorn com ele:

```sh
# tornar executável (uma vez):
chmod +x scripts/run_uvicorn.sh
# rodar (porta padrão 8000):
./scripts/run_uvicorn.sh
# ou porta customizada:
./scripts/run_uvicorn.sh --port 9000
# apenas mostrar o comando resolvido sem executar:
./scripts/run_uvicorn.sh --dry-run
```

Se preferir usar diretamente o comando `uvicorn ...`, certifique-se de que o
IntelliJ esteja usando/ativando o mesmo virtualenv que você usou para instalar
as dependências. No IntelliJ isso é configurado em Settings > Tools > Terminal
ou ajustando o Python Interpreter do projeto para apontar para a virtualenv.

## Endpoints úteis
- Healthcheck: `GET http://localhost:8000/health`
- Webhook: `POST http://localhost:8000/webhook/github`
- Swagger UI: `http://localhost:8000/docs`

## Testando o webhook
Exemplo de payload (Issues opened):

```sh
curl -X POST "http://localhost:8000/webhook/github" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issues" \
  -d '{"action":"opened","repository":{"name":"meu-repo"},"issue":{"number":1,"title":"Adicionar endpoint X","labels":[{"name":"service:identity"}]}}'
```

## Dicas de desenvolvimento
- **Logs:** o logger usa a identificação `devflow-orchestrator`.
- **Mocks:** se não quiser usar chaves reais, crie funções dummy para `generate_text` e `post_github_comment`.
- **Projeto modular:** é possível testar `stack_detector` e `normalizer` isoladamente via REPL.

## Demonstração pública com ngrok
Para demonstrar o fluxo com GitHub real:

### 1) Instalar e autenticar ngrok
```sh
sudo snap install ngrok
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

### 2) Expor a porta do orquestrador
```sh
ngrok http 8000
```

### 3) Configurar o Webhook no GitHub
- Payload URL: `https://<YOUR_NGROK_HOST>/webhook/github`
- Content type: `application/json`
- Events: `Issues`

### 4) Testar com Issue real ou curl
```sh
curl -X POST "https://abc123.ngrok-free.app/webhook/github" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issues" \
  -d '{"action":"opened","repository":{"name":"meu-repo"},"issue":{"number":1,"title":"Adicionar endpoint X"}}'
```

**Observações de segurança:**
- Use tokens de teste/contas secundárias.
- Em `development`, utilize mocks para evitar efeitos colaterais.

## Service-aware issues (monorepo)
O `devflow-orchestrator` suporta duas abordagens para identificar o serviço alvo:

- **Labels:** `service:<name>` (ex.: `service:identity`)
- **Issue template:** campo `Target Service` (prioridade atual: labels)

Exemplo com labels:
1. Crie o label `service:identity`.
2. Aplique o label na issue.
3. O normalizador extrai `service = "identity"` e o context builder resolve o caminho do serviço.

Se quiser suporte para parsing de `Target Service` no corpo da issue, posso implementar.

## Próximos passos recomendados
1. Criar `requirements.txt` e um `run-local.sh` com os comandos acima.
2. Adicionar `.env.example` com variáveis necessárias.
3. Implementar mocks para OpenAI e GitHub em modo `development`.
4. Escrever 6-8 testes unitários cobrindo `normalizer`, `stack_detector` e `planning_agent`.
5. Melhorar o template de Markdown para comentários.

