from datetime import datetime


def generate_markdown_plan(issue_title, issue_number, project_context, service_context, plan):

    # service_context may be a ServiceContext or a minimal ProjectContext fallback
    repo = getattr(project_context, "repository", "unknown")
    svc_name = getattr(service_context, "name", "unknown")
    language = getattr(service_context, "language", None) or getattr(project_context, "language", "unknown")
    framework = getattr(service_context, "framework", None) or getattr(project_context, "framework", "unknown")
    build_tool = getattr(service_context, "build_tool", None) or getattr(project_context, "build_tool", "unknown")
    java_version = getattr(service_context, "java_version", None) or getattr(project_context, "java_version", "")
    dependencies = getattr(service_context, "dependencies", []) or getattr(project_context, "dependencies", [])

    markdown = f"""
# Development Plan - Issue #{issue_number}

## Issue

{issue_title}

---

## Generated At

{datetime.utcnow().isoformat()} UTC

---

# Project Context

| Property | Value |
|---|---|
| Repository | {repo} |
| Service | {svc_name} |
| Language | {language} |
| Framework | {framework} |
| Build Tool | {build_tool} |
| Java Version | {java_version} |

---

# Dependencies

"""

    for dependency in dependencies:
        markdown += f"- {dependency}\n"

    markdown += "\n---\n"
    markdown += "\n# Planned Steps\n\n"

    steps = plan.get("steps", [])

    for step in steps:

        markdown += f"""
## Step {step.get("id")}

### Type
{step.get("type")}

### Description
{step.get("description")}

---
"""

    markdown += """

# Approval

- [ ] Approved
- [ ] Rejected

"""

    return markdown