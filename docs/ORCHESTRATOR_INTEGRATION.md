# Integração: DevFlow Orchestrator → devflow-platform

Resumo objetivo para o time do DevFlow Orchestrator: o que este repo contém, onde o Orchestrator deve atuar, quais mudanças automáticas são seguras e quais cuidados tomar para abrir PRs, rodar testes e garantir qualidade.

---

## Checklist rápido (para leitura automática pelo Orchestrator)

- [ ] Repositório raiz: `devflow-platform/`
- [ ] Módulos Maven (parent POM): `pom.xml` (packaging = pom)
- [ ] Locais-alvo (onde modificar código):
  - `services/identity-service/`
  - `services/workflow-service/`
  - `gateway/devflow-gateway/`
  - `web/devflow-web/`
- [ ] Comandos básicos que Orchestrator pode executar:
  - `mvn -T1C -DskipTests=false clean install` (build + tests)
  - `mvn -am -pl <module> clean test` (build+test de módulo)
- [ ] Não commitar diretórios `target/` nem `devflow_ai_generated/` (já no `.gitignore`)

---

## Objetivo do Orchestrator

O Orchestrator automatiza alterações de código, testes unitários, criação de branches e PRs neste repo. Para integrar com segurança ele precisa:

1. Clonar `devflow-platform` a partir do main remoto.
2. Criar branch de trabalho seguindo convenção: `orchestrator/<ticket>-<short-desc>`.
3. Aplicar patch no(s) módulo(s) alvo.
4. Rodar build e testes locais no módulo alterado e no parent (opcionalmente somente no módulo com `-am -pl`).
5. Se tudo passar, abrir PR contra `main` com um template já definido.

---

## Estrutura relevante do repo

```
devflow-platform/
├── services/
│   ├── identity-service/     # Spring Boot service (módulo Maven)
│   └── workflow-service/     # Spring Boot service (módulo Maven)
├── gateway/
│   └── devflow-gateway/      # Spring Boot gateway (módulo Maven)
├── web/
│   └── devflow-web/          # frontend (aqui tem pom.xml; adaptar se frontend for Node)
├── infra/
├── docs/
├── pom.xml                   # parent POM (módulos referenciados com paths relativos)
└── docker-compose.yml
```

Cada módulo contém um `pom.xml` e os `src/main/java` e `src/test/java` mínimos (os testes de smoke já existem). Os módulos compilam com `mvn clean install` na raiz.

---

## Operações recomendadas do Orchestrator

1. Preparação

```bash
git clone git@github.com:<org>/devflow-platform.git
cd devflow-platform
git checkout -b orchestrator/<ticket>-<short-desc>
```

2. Aplicar alteração (exemplo: adicionar teste unitário)

- Modificar apenas arquivos dentro do módulo alvo (ex: `services/identity-service/src/main/java/...` ou `.../src/test/java/...`).
- Evitar modificar `pom.xml` raiz sem validação humana (mudar versão parent ou módulos pode impactar todos os builds).

3. Build e testes

Execute somente o módulo e dependências relevantes para acelerar feedback:

```bash
# Compila+testa apenas o módulo alvo e módulos que dependem dele
mvn -am -pl services/identity-service clean test

# Se alteração envolver API ou integração entre módulos, rodar build completo
mvn -T1C clean install
```

4. Verificação de hygiene

- Confirmar que não há artefatos gerados stageados (`target/`).
- Confirmar que linter / formatter (se existir) passou.
- Checar se `docs/` ou `README.md` precisam atualização (se alteração afetar contract/api).

5. Commit, push e PR

- Mensagem de commit: `feat(orchestrator): <breve descrição>` ou `test(orchestrator): add ...`
- Push: `git push origin orchestrator/<ticket>-<short-desc>`
- PR: criar contra `main` com template (ver seção PR template)

---

## Regras de segurança e boas práticas

- Não alterar o `pom.xml` raiz automaticamente. Se necessário, abrir PR com descrição clara e um reviewer humano.
- Não modificar nada fora das pastas de módulo sem aprovação (ex: `.gitignore`, `docker-compose.yml`, docs top-level — a não ser que Orchestrator inclua mudança de infra explícita).
- Evitar alterações em `LICENSE`, `README.md` global sem revisão humana.
- Garantir que todos os testes do módulo alvo passam antes de abrir PR.
- Preferir pequenas mudanças atomizadas (um PR por feature/teste) — facilita reverts e revisão.

---

## Padrões de branch, commit e PR (sugestão)

- Branch: `orchestrator/<issue-number>-<short>`  (ex: `orchestrator/123-add-auth-test`)
- Commit message:
  - `feat(service): descrição curta` — para código
  - `test(service): descrição curta` — para testes
  - `chore: atualiza docs` — para alterações de documentação
- PR title: `[ORCH-<issue>] <breve descrição>`
- PR body: incluir:
  - O que foi alterado (arquivos principais)
  - Como testar localmente (comandos mvn)
  - Resultado esperado
  - Checklist: testes executados, lint, build completo

Exemplo de checklist para PR body:

- [ ] mvn -am -pl <module> clean test (pass)
- [ ] mvn clean install (pass) — opcional
- [ ] Código revisado por 1+ reviewers

---

## Como rodar testes unitários programaticamente (scripts)

Orchestrator pode usar um script simples para executar o fluxo:

```bash
#!/usr/bin/env bash
set -euo pipefail
MODULE="$1"  # ex: services/identity-service
BRANCH="$2"

# checkout branch e aplicar patch (já feito antes)
# rodar testes do módulo
mvn -am -pl "$MODULE" clean test

# opcional: rodar build da raiz se quiser validar integração
# mvn -T1C clean install
```

Salve como `ci/orchestrator-run.sh` e execute com:

```bash
bash ci/orchestrator-run.sh services/identity-service orchestrator/123-add-test
```

---

## Integração com CI do repositório

- Sugerimos adicionar um workflow em `.github/workflows/orchestrator.yml` que valide PRs abertos pelo Orchestrator:
  - Trigger: pull_request (from: orchestrator/*)
  - Jobs: `build` (mvn -T1C clean install), `test` (mvn -am -pl changed-module clean test)

Exemplo mínimo de step no GitHub Actions:

```yaml
name: Orchestrator PR Validation
on:
  pull_request:
    branches: [ main ]
    paths:
      - 'services/**'
      - 'gateway/**'
      - 'web/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          distribution: temurin
          java-version: '21'
      - name: Build & test
        run: mvn -T1C clean install
```

Nota: workflow completo pode incluir caching de Maven, upload de artefatos e relatórios de cobertura.

---

## Requisitos extras recomendados para facilitar automações

1. Dockerfiles por módulo (multi-stage) para permitir construção de imagens pelo Orchestrator.
   - Local: `services/identity-service/Dockerfile`, etc.
2. Expor OpenAPI/Swagger JSON por cada serviço para comparação de contratos antes de mudanças.
3. Coverage (Jacoco) configurado nos `pom.xml` dos módulos para gerar relatórios e bloquear PRs com queda significativa de cobertura.
4. Testes de integração básicos ou testes de contrato (pact / contract tests) para alterar APIs com segurança.
5. `CONTRIBUTING.md`, `PULL_REQUEST_TEMPLATE.md` e `CODEOWNERS` para automatizar reviewers e políticas.

---

## Onde o Orchestrator deve aplicar mudanças tipicamente

- Adição/alteração de testes unitários: `*/src/test/java/**`
- Pequenas correções de código (bugfixes): `*/src/main/java/**`
- Ajustes de dependências específicos de módulo: `*/pom.xml` (evitar alterar parent POM automaticamente)
- Geração de código (scaffolding): colocar saída em `*/src/generated/` e incluir `.gitignore` rules apropriadas

---

## Exemplo de fluxo completo automatizado

1. Issue criada no tracker com ID 432
2. Orchestrator recebe webhook → cria branch `orchestrator/432-add-login-test`
3. Orchestrator aplica patch: adiciona `LoginControllerTest` em `services/identity-service/src/test/java/...`
4. Orchestrator executa `mvn -am -pl services/identity-service clean test`
   - Se testes PASSAM → Orchestrator cria commit e push para branch
   - Se testes FALHAM → Orchestrator abre issue com log e não cria PR
5. Orchestrator abre PR contra `main` com descrição e checklist preenchidos
6. CI (workflow) executa `mvn clean install` e reporta status
7. Se CI PASSA e reviewers aprovam → PR merge

---

## Mensagens de erro comuns e como tratá-las (para Orchestrator)

- "Dependency resolution failed" → tentar `mvn -U` ou reportar rede/credentials
- Testes intermitentes → re-run tests, anexar logs e flakiness label
- Build que modifica múltiplos módulos inesperadamente → abortar e exigir revisão humana

---

## Contatos e reviewers padrão

Sugestão inicial (adicionar ao `CODEOWNERS`):

```
# CODEOWNERS (exemplo)
/services/identity-service/ @team-identity
/services/workflow-service/ @team-workflow
/gateway/ @team-gateway
/web/ @team-web
```

---

## Conclusão

O `devflow-platform` está organizado para suportar automações do Orchestrator. A peça crítica é manter o parent `pom.xml` estável e executar testes no módulo alvo antes de abrir PRs. Se desejar, posso:

- adicionar o script `ci/orchestrator-run.sh` no repo (para padronizar execução),
- criar um workflow GitHub Actions minimal para validar PRs do Orchestrator,
- ou adicionar `CONTRIBUTING.md` e `PULL_REQUEST_TEMPLATE.md` para padronizar PRs.

Diga qual destes passos quer que eu execute e eu implemento automaticamente.

