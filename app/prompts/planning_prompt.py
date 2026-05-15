def build_planning_prompt(issue_title: str, context):

    # context is service-aware (ServiceContext) and may expose entrypoints
    source_dirs = getattr(context, "entrypoints", None) or getattr(context, "source_directories", [])

    return f"""
You are an AI software architect.

Generate a development implementation plan for the following issue.

ISSUE:
{issue_title}

PROJECT CONTEXT:

Language:
{getattr(context, 'language', 'unknown')}

Framework:
{getattr(context, 'framework', 'unknown')}

Build Tool:
{getattr(context, 'build_tool', 'unknown')}

Source Directories / Entrypoints:
{source_dirs}

Generate a concise implementation plan in JSON format.

Expected format:

{{
  "steps": [
    {{
      "id": 1,
      "type": "controller",
      "description": "Create REST controller"
    }}
  ]
}}
"""