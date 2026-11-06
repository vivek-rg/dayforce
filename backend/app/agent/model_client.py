"""The agent's one model seam, delegating to the shared AI harness."""

from collections.abc import Callable

from app.ai.harness import RunResult, run_operation
from app.ai.prompts import AGENT_SYSTEM, agent_user


def generate_next_step(
    message: str,
    steps_json: str,
    *,
    user_id: str,
    hire_id: str,
    case_id: str,
    before_attempt: Callable[[], bool],
) -> RunResult:
    return run_operation(
        "agent.next_step",
        [
            {"role": "system", "content": AGENT_SYSTEM},
            {"role": "user", "content": agent_user(message, steps_json)},
        ],
        user_id=user_id,
        hire_id=hire_id,
        case_id=case_id,
        before_attempt=before_attempt,
    )
