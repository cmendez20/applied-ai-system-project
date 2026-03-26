from __future__ import annotations

from datetime import date
from typing import Sequence

from pawpal_system import Task


def filter_tasks_by_due_date(tasks: Sequence[Task], due_on: date | None) -> list[Task]:
    """Return tasks due on a specific date, or all tasks when no date is set."""
    if due_on is None:
        return list(tasks)
    return [task for task in tasks if task.due_date == due_on]


def conflict_ui_payload(conflict_warnings: Sequence[str]) -> tuple[str, list[str]]:
    """Return UI status and messages for conflict warnings display."""
    if conflict_warnings:
        return (
            "warning",
            [
                "Potential time conflicts found in your tasks:",
                *conflict_warnings,
            ],
        )
    return ("success", ["No task time conflicts detected."])


def completion_feedback_message(next_task: Task | None) -> str:
    """Return user-facing completion feedback for the Streamlit UI."""
    if next_task is None:
        return "Task completed."
    return (
        "Task completed. Added next occurrence for "
        f"{next_task.due_date.isoformat()} at {next_task.time}."
    )
