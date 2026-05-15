from app.core.logger import logger
from app.prompts.planning_prompt import build_planning_prompt
from app.llm.openai_client import generate_text


async def generate_plan(issue_title: str, context):

    logger.info("Generating plan with OpenAI")

    prompt = build_planning_prompt(
        issue_title,
        context
    )

    response = await generate_text(prompt)

    logger.info("Plan generated successfully")

    return response