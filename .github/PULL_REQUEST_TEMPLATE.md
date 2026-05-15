<!-- Título sugerido: [ORCH-<issue>] Breve descrição -->

## O que foi alterado
Liste os arquivos/módulos principais alterados:
- services/...
- gateway/...

## Como testar localmente
Passos para testar:

```bash
# exemplo: trocar branch e rodar testes do módulo alvo
git checkout <branch>
bash ci/orchestrator-run.sh services/identity-service <branch>
# ou
mvn -am -pl services/identity-service clean test
```

## Resultado esperado
Descreva o comportamento esperado ou o que os testes cobrem.

## Checklist
- [ ] mvn -am -pl <module> clean test (pass)
- [ ] mvn clean install (opcional — pass)
- [ ] Nenhum artefato em `target/` comitado
- [ ] Revisão humana aprovada caso `pom.xml` raiz tenha sido alterado

## Nota sobre root pom.xml
Se este PR altera o `pom.xml` na raiz, explique por quê e providencie referência/issue e marque o PR com a label `allow-root-pom-change` para indicar que revisão humana foi requisitada.

---

Link para a issue (se houver):
- https://...

