# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

Recent updates added lightweight scheduling intelligence to the core system:

- **Time-aware ordering:** tasks can include a `time` field in `HH:MM` format, and the scheduler can sort tasks chronologically.
- **Priority with time tie-breaker:** schedule generation still prioritizes important tasks first, with optional time-based tie-breaking for tasks with similar urgency.
- **Task filtering:** owners can filter tasks by completion state and by pet name for faster review.
- **Recurring automation:** completing a `daily` or `weekly` task can automatically create the next occurrence with a correctly incremented `due_date`.
- **Conflict warnings:** the scheduler can detect tasks sharing the same time and return warnings (instead of crashing), including cross-pet conflicts.

## Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest
```

Current tests cover core scheduling behaviors, including task completion state changes,
adding tasks to pets, chronological sorting by time, recurring-task generation for daily
and weekly tasks, non-recurring task handling, empty-schedule behavior, and conflict
detection for duplicate times.

**Confidence Level:** ★★★★☆ (4/5)

The suite currently passes and covers key logic paths for scheduling, recurrence, and
conflict warnings. Confidence is high for implemented features, with room to grow through
additional UI and integration tests.
