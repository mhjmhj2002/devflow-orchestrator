#!/usr/bin/env python3
"""Small demo to build and print a planner prompt using repository context."""
from app.agents.planner_agent import generate_plan
from app.project_context.models import ProjectContext, ServiceContext


def main():
    svc = ServiceContext(
        name="identity-service",
        path="services/identity-service",
        language="Java",
        framework="Spring Boot",
        build_tool="Maven",
        java_version="21",
        dependencies=["Spring Web", "Spring Data JPA"],
        entrypoints=["src/main/java/com/example/identity/Application.java"]
    )

    ctx = ProjectContext(
        repository="devflow-ai",
        services=[svc],
        language="Java",
        framework="Spring Boot",
        build_tool="Maven",
        java_version="21",
        dependencies=["Spring Web", "Spring Data JPA"],
        architecture_hints=["monolith"],
        source_directories=["services/identity-service/src/main/java"]
    )

    res = generate_plan(
        issue_title="Create POST /users endpoint",
        issue_body="Add an endpoint to create users stored in PostgreSQL; validate unique email and return 201.",
        context=ctx
    )

    print("\n=== GENERATED PROMPT (truncated) ===\n")
    print(res.get("prompt")[:1500])


if __name__ == "__main__":
    main()

