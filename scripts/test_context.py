#!/usr/bin/env python3
# scripts/test_context.py

from app.project_context.context_builder import build_project_context

repo_path = "/home/mhj/git/devflow-ai"

context = build_project_context(
    repo_path=repo_path,
    repository="devflow-ai"
)

print("\n=== PROJECT CONTEXT ===\n")
print(context)

