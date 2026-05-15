from pathlib import Path
import os


def save_plan(issue_number: int, content: str):
    """Save the generated plan to `docs/plans` only when the environment
    variable DEVFLOW_SAVE_PLANS is set (true/1/yes). By default this
    function is a no-op because plan documentation should live in the
    issue itself (posted as a comment) rather than committed to the repo.
    """
    SAVE_PLANS = os.getenv("DEVFLOW_SAVE_PLANS", "false").lower() in ("1", "true", "yes")
    if not SAVE_PLANS:
        # indicate nothing was persisted on disk
        return None

    plans_dir = Path("docs/plans")

    plans_dir.mkdir(parents=True, exist_ok=True)

    file_path = plans_dir / f"issue-{issue_number}-development-plan.md"

    with open(file_path, "w") as file:
        file.write(content)

    return str(file_path)