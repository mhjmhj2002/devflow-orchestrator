#!/usr/bin/env bash
set -euo pipefail

# ci/orchestrator-run.sh
# Uso: ci/orchestrator-run.sh <MODULE_PATH> <BRANCH>
# Ex: bash ci/orchestrator-run.sh services/identity-service orchestrator/123-add-test

MODULE="${1:-}"
BRANCH="${2:-}"

if [[ -z "$MODULE" || -z "$BRANCH" ]]; then
  echo "Uso: $0 <MODULE_PATH> <BRANCH>"
  exit 2
fi

# Verificar que estamos no diretório do repo (existência de pom.xml)
if [[ ! -f "pom.xml" ]]; then
  echo "Arquivo pom.xml não encontrado na raiz. Certifique-se de executar este script no diretório raiz do repositório devflow-platform."
  exit 2
fi

# Atualizar refs
git fetch --no-tags --prune origin

# Se branch existir localmente, checkout; caso contrário, tentar criar a partir de origin/main
if git rev-parse --verify --quiet "$BRANCH" >/dev/null; then
  git checkout "$BRANCH"
else
  if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
    git checkout -b "$BRANCH" "origin/$BRANCH"
  else
    echo "Branch '$BRANCH' não encontrada localmente nem no origin. Aborting."
    exit 3
  fi
fi

# Garantir workspace limpo (não há mudanças não commitadas)
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Existem mudanças não commitadas no workspace. Commit ou stash antes de executar o script."
  git status --porcelain
  exit 4
fi

# Detectar se pom.xml da raiz foi alterado no diff entre base (origin/main) e a branch atual
# Obter nome do branch base (assume main)
BASE_REF="origin/main"

# Buscar diferenças entre base e HEAD
git fetch origin main:refs/remotes/origin/main || true
CHANGED_FILES=$(git diff --name-only "$BASE_REF...HEAD")

if echo "$CHANGED_FILES" | grep -xq "pom.xml"; then
  echo "Detected change in root pom.xml. For safety, automated orchestrator changes MUST NOT modify root pom.xml."
  echo "Aborting. If this change is intentional, open a PR manually and request a human reviewer with the 'allow-root-pom-change' label."
  exit 5
fi

# Garantir que target/ não está staged/committed
if echo "$CHANGED_FILES" | grep -q "^target/"; then
  echo "Existem alterações em 'target/' — verifique .gitignore e remova artefatos gerados antes de prosseguir."
  exit 6
fi

# Executar testes apenas no módulo alvo
echo "Executando testes para módulo: $MODULE"

if [[ ! -d "$MODULE" ]]; then
  echo "Módulo '$MODULE' não encontrado no path dado."
  exit 7
fi

mvn -am -pl "$MODULE" clean test

# Se quiser executar build completo, descomente a linha abaixo (opcional)
# mvn -T1C clean install

echo "Execução concluída com sucesso."

