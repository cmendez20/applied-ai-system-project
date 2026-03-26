from datetime import date

from pawpal_system import Task
from ui_helpers import (
    completion_feedback_message,
    conflict_ui_payload,
    filter_tasks_by_due_date,
)


def test_conflict_ui_payload_returns_warning_messages_when_conflicts_exist() -> None:
    status, messages = conflict_ui_payload(
        ["Warning: time conflict at 07:30 across pets [Luna, Mochi] (Feed, Meds)."]
    )

    assert status == "warning"
    assert messages[0] == "Potential time conflicts found in your tasks:"
    assert "time conflict at 07:30" in messages[1]


def test_completion_feedback_message_describes_recurring_task_creation() -> None:
    next_task = Task(
        description="Morning walk",
        duration_in_minutes=30,
        frequency="daily",
        pet_id="pet-1",
        due_date=date(2026, 3, 27),
        time="08:00",
    )

    message = completion_feedback_message(next_task)

    assert "Added next occurrence for 2026-03-27 at 08:00" in message


def test_filter_tasks_by_due_date_only_keeps_today_items() -> None:
    tasks = [
        Task(
            description="Today task",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=date(2026, 3, 26),
            time="09:00",
        ),
        Task(
            description="Tomorrow task",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=date(2026, 3, 27),
            time="09:00",
        ),
    ]

    filtered = filter_tasks_by_due_date(tasks, date(2026, 3, 26))

    assert len(filtered) == 1
    assert filtered[0].description == "Today task"
