# Contributing — DevFlow Orchestrator

Este documento descreve como o Orchestrator deve atuar e as convenções para mudanças automáticas no repositório.

Resumo rápido
- Branches do Orchestrator: `orchestrator/<issue>-<short>` (ex: `orchestrator/123-add-test`)
- Não alterar `pom.xml` raiz automaticamente. Se for necessário, abrir PR manual e obter revisão humana.

Como rodar testes localmente
- Rodar apenas o módulo alvo e dependências:

```bash
# ex: executar testes do módulo identity-service
mvn -am -pl services/identity-service clean test

# usar o helper do Orchestrator (script)
bash ci/orchestrator-run.sh services/identity-service orchestrator/123-add-test
```

Regras importantes
- Evitar modificar arquivos fora dos módulos alvo (ex: `pom.xml` raiz, `README.md` global) sem revisão humana.
- Não commitar diretórios `target/` nem artefatos gerados.
- Prefira pequenas mudanças atomizadas (um PR por feature/teste).

Commits e Branches
- Branch: `orchestrator/<issue>-<short>`.
- Mensagem de commit:
  - `feat(service): descrição curta` — código
  - `test(service): descrição curta` — testes
  - `chore: ...` — tarefas

PRs
- Título sugerido: `[ORCH-<issue>] <breve descrição>`
- Use o template de PR presente em `.github/PULL_REQUEST_TEMPLATE.md`.

Segurança: alterações no parent `pom.xml`
- O Orchestrator NÃO deve modificar o `pom.xml` na raiz automaticamente.
- Se necessário, abra PR manual com justificativa clara e adicione a label `allow-root-pom-change`.
- O workflow de CI valida e bloqueará PRs que tentem alterar o `pom.xml` raiz sem a label.

Checklist mínimo antes de abrir PR
- [ ] mvn -am -pl <module> clean test (pass)
- [ ] Nenhum artefato em `target/` commitado
- [ ] Descrição clara no PR e comandos para reproduzir (no template)

Contato / CODEOWNERS
- Recomenda-se adicionar `CODEOWNERS` para automatizar reviewers por módulo (exemplo em /CODEOWNERS).

