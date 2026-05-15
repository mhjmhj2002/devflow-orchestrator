# app/prompts/planner_prompt_builder.py

from app.project_context.models import ProjectContext


def build_planner_prompt(
        issue_title: str,
        issue_body: str,
        context: ProjectContext
):
    services_section = "\n".join([
        f"- {s.name} (path={s.path}, language={s.language or context.language}, framework={s.framework or context.framework})"
        for s in (context.services or [])
    ]) or "- (no services discovered)"

    dependencies = ", ".join(context.dependencies) if context.dependencies else "(none detected)"

    source_dirs = ", ".join(context.source_directories) if context.source_directories else "(not provided)"

    return f"""
You are a senior software engineer and technical architect. Given the project context and an issue from GitHub, produce a professional, enterprise-grade implementation plan in MARKDOWN. Do NOT output anything else outside the requested structured plan.

Use the project context to make the plan specific to this repository. If the context lists services, mark them as Affected Components. If source directories or file paths are available, reference them concretely. When unsure, state assumptions clearly.

Output the plan using these sections (use the exact headings):

## Objective
- One-line statement of what to implement (use issue title and description).

## Impact Analysis
- Affected components (list services, packages, modules)
- Potential risks and rollback considerations

## Technical Design
- High-level architecture changes
- API surface and handlers
- Data models / DB migrations
- Security and validation
- Observability (logs, metrics, tracing)

## Contract Definition
- API endpoint(s) with request/response JSON schema
- Events produced/consumed (if any)

## Acceptance Criteria
- Concrete testable criteria (status codes, validations, side-effects)

## Testing Strategy
- Unit, integration, and end-to-end tests to cover behavior
- Mocking and test data recommendations

## Implementation Order
- Step-by-step workplan with small deliverable milestones

## Estimated Complexity
- One of: Low / Medium / High

## Estimated Effort
- Rough engineer-hours or story points (e.g., 2-4 hours, 1-2 days)

## Dependencies
- External systems, libraries, infra changes

## Notes & Assumptions
- Any assumptions you made about the codebase or environment

---

Project Context:

Repository: {context.repository}

Services:
{services_section}

Language: {context.language or 'unknown'}
Framework: {context.framework or 'unknown'}
Build Tool: {context.build_tool or 'unknown'}
Java Version: {context.java_version or 'unknown'}

Dependencies: {dependencies}

Source directories: {source_dirs}

Issue Title:
{issue_title}

Issue Description:
{issue_body}

Produce the plan now.
"""