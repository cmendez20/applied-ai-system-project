# PawPal+ Project 4: Agentic AI Planner Mode

## 1. Original Project Context (Modules 1-3)

The original PawPal+ project is a pet care scheduling app built in Python and Streamlit. It lets a user create pets, add care tasks with duration/priority/time, and generate a daily schedule under a time budget.

Modules 1-3 focused on deterministic scheduling logic (`pawpal_system.py`) plus a lightweight Streamlit interface (`app.py`). Core capabilities included task filtering, priority ordering, conflict detection warnings, and recurrence handling for daily/weekly tasks.

## 2. Project 4 Title & Why It Matters

**Project 4 Title:** PawPal+ Agentic Planner Mode with Reliability Layer

This extension adds an explicit agentic workflow to schedule generation so intermediate reasoning steps are visible and testable. It also adds a reliability layer (self-check + revision + eval harness) so planning quality can be measured instead of assumed.

## 3. Architecture Overview

When AI Planner Mode is enabled, schedule generation follows a five-step pipeline in `ai_planner.py` and returns the final plan with trace, confidence, and warnings.

```text
[User Inputs in Streamlit]
        |
        v
[app.py UI Layer]
        |
        +--> (baseline) Scheduler.generate_schedule
        |
        +--> (AI Planner Mode ON)
                |
                v
        [ai_planner.py Pipeline]
        1) Interpret Constraints
        2) Select Candidates
        3) Draft Plan
        4) Self-Check
        5) Revise if Needed
                |
                +--> Trace + Confidence + Warnings
                v
         [Final Schedule Table]
                |
                v
      [Reliability Layer: eval_ai.py + tests]
                |
                v
        [Human review in UI]
```

## 4. Setup Instructions

Run all commands from the repo root.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Run tests:

```bash
python -m pytest
```

Run evaluation harness:

```bash
python eval_ai.py
```

## 5. Sample Interactions (Input -> AI Planner Output)

### Example 1: Tight budget
- **Input:** `available_minutes=15`, `today_only_schedule=True`, `include_completed=False`
- **Output:** planner keeps the highest-priority fitting task and skips longer lower-priority tasks.
- **Trace highlight:** `draft_plan` shows budget-based skips; `self_check_plan` passes budget constraint.

### Example 2: Conflict-heavy tasks
- **Input:** multiple tasks at `07:30`, `use_time_tiebreaker=True`
- **Output:** planner revises by removing lower-utility same-time conflicts and keeps one task in that slot.
- **Trace highlight:** `self_check_plan` warns on conflicts, then `revise_plan_if_needed` resolves overlap.

### Example 3: Normal planning day
- **Input:** `available_minutes=90`, mixed priorities/times
- **Output:** stable prioritized schedule with confidence near 1.0 and full five-step trace.
- **Trace highlight:** all required steps appear: interpret -> select -> draft -> self-check -> revise.

## 6. Design Decisions & Trade-offs

- **Deterministic planner over external LLM calls:** improves reproducibility, unit testing, and local execution reliability.
- **Interpretability over complexity:** pipeline emits trace rows for each step so users can inspect decisions.
- **Guardrail-first behavior:** negative budgets are rejected, empty candidate sets are handled gracefully, and conflict checks are non-blocking but surfaced.
- **Single revision pass:** keeps behavior predictable and easy to debug, at the cost of less exhaustive optimization.

## 7. Testing Summary

- Added planner tests in `tests/test_ai_planner.py` covering:
  - time budget enforcement
  - high-priority task selection
  - conflict-triggered revision behavior
  - full five-step trace presence
  - confidence bounds in `[0, 1]`
- Existing tests in `tests/test_pawpal.py` and `tests/test_ui_helpers.py` continue to validate domain and UI helper behavior.
- Evaluation harness in `eval_ai.py` runs fixed scenarios and prints a scoreboard.
- Latest harness run produced `passed/total: 6/6`, `avg confidence: 0.950`, `failed scenario names: None`.

## 8. Reflection

Reflection content for rubric prompts is tracked in `reflection.md`, including:
- AI collaboration process
- model limitations and bias risks
- misuse prevention considerations
- lessons learned and future improvements

## Demo Screenshots

<a href="final_streamlit_app_01.png" target="_blank"><img src='final_streamlit_app_01.png' title='PawPal App' alt='PawPal App screenshot 1' class='center-block' /></a>

<a href="final_streamlit_app_02.png" target="_blank"><img src='final_streamlit_app_02.png' title='PawPal App' alt='PawPal App screenshot 2' class='center-block' /></a>

<a href="final_streamlit_app_03.png" target="_blank"><img src='final_streamlit_app_03.png' title='PawPal App' alt='PawPal App screenshot 3' class='center-block' /></a>
