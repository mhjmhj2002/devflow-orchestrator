# app/agents/planner_agent.py

from app.prompts.planner_prompt_builder import (
    build_planner_prompt
)


def generate_plan(
        issue_title,
        issue_body,
        context
):

    prompt = build_planner_prompt(
        issue_title,
        issue_body,
        context
    )

    print("\n========== PROMPT ==========\n")
    print(prompt)

    # In the current MVP we only build the prompt for the LLM. Return the prompt for callers
    # so that the execution layer can send it to the model and persist the result.
    return {
        "status": "planning",
        "message": "planner executed",
        "prompt": prompt
    }