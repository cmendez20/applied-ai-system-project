from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Sequence

from pawpal_system import Owner, Scheduler, Task


@dataclass
class PlannerOutput:
    final_schedule: list[Task]
    trace: list[dict[str, Any]]
    confidence: float
    warnings: list[str]


def interpret_constraints(
    available_minutes: int | None,
    include_completed: bool,
    today_only_schedule: bool,
    use_time_tiebreaker: bool,
) -> dict[str, Any]:
    """Normalize planner controls into a single constraint bundle."""
    if available_minutes is not None and int(available_minutes) < 0:
        raise ValueError("available_minutes cannot be negative.")

    return {
        "planning_date": date.today(),
        "available_minutes": None
        if available_minutes is None
        else int(available_minutes),
        "include_completed": bool(include_completed),
        "today_only_schedule": bool(today_only_schedule),
        "use_time_tiebreaker": bool(use_time_tiebreaker),
    }


def select_candidates(
    tasks: Sequence[Task],
    constraints: dict[str, Any],
) -> list[Task]:
    """Apply hard filters, then rank tasks deterministically for planning."""
    planning_date: date = constraints["planning_date"]
    include_completed: bool = constraints["include_completed"]
    today_only_schedule: bool = constraints["today_only_schedule"]
    use_time_tiebreaker: bool = constraints["use_time_tiebreaker"]

    filtered = list(tasks)

    if today_only_schedule:
        filtered = [task for task in filtered if task.due_date == planning_date]

    if not include_completed:
        filtered = [task for task in filtered if not task.is_completed]

    return sorted(
        filtered,
        key=lambda task: _candidate_sort_key(
            task,
            planning_date,
            use_time_tiebreaker,
        ),
    )


def draft_plan(
    candidates: Sequence[Task],
    available_minutes: int | None,
) -> tuple[list[Task], list[dict[str, str]], int]:
    """Greedily build a budget-aware plan and record skipped reasons."""
    selected: list[Task] = []
    skipped: list[dict[str, str]] = []
    used_minutes = 0

    for task in candidates:
        if available_minutes is not None:
            would_use = used_minutes + task.duration_in_minutes
            if would_use > available_minutes:
                skipped.append(
                    {
                        "task": task.description,
                        "reason": "exceeds available time budget",
                    }
                )
                continue

        selected.append(task)
        used_minutes += task.duration_in_minutes

    return selected, skipped, used_minutes


def self_check_plan(
    owner: Owner,
    scheduler: Scheduler,
    planned_tasks: Sequence[Task],
    candidates: Sequence[Task],
    constraints: dict[str, Any],
) -> dict[str, Any]:
    """Validate budget, conflict warnings, and baseline plan feasibility."""
    available_minutes: int | None = constraints["available_minutes"]
    include_completed: bool = constraints["include_completed"]

    minutes_used = sum(task.duration_in_minutes for task in planned_tasks)
    passes_budget = (
        True if available_minutes is None else minutes_used <= available_minutes
    )

    conflict_warnings = scheduler.detect_time_conflicts(
        owner,
        list(planned_tasks),
        include_completed=include_completed,
    )

    feasible = _is_non_empty_plan_feasible(candidates, available_minutes)
    non_empty_when_feasible = (not feasible) or bool(planned_tasks)

    return {
        "passes_budget": passes_budget,
        "conflict_warnings": conflict_warnings,
        "non_empty_when_feasible": non_empty_when_feasible,
        "is_valid": passes_budget and not conflict_warnings and non_empty_when_feasible,
        "minutes_used": minutes_used,
    }


def revise_plan_if_needed(
    owner: Owner,
    scheduler: Scheduler,
    planned_tasks: Sequence[Task],
    candidates: Sequence[Task],
    constraints: dict[str, Any],
    check_result: dict[str, Any],
) -> tuple[list[Task], dict[str, Any], list[str]]:
    """Attempt a single revision pass when self-check flags issues."""
    if check_result["is_valid"]:
        return list(planned_tasks), check_result, ["No revision needed."]

    planning_date: date = constraints["planning_date"]
    available_minutes: int | None = constraints["available_minutes"]
    use_time_tiebreaker: bool = constraints["use_time_tiebreaker"]

    revised = list(planned_tasks)
    revision_notes: list[str] = []

    if check_result["conflict_warnings"]:
        revised = _remove_conflicting_tasks(
            revised,
            planning_date=planning_date,
            use_time_tiebreaker=use_time_tiebreaker,
            revision_notes=revision_notes,
        )

    if available_minutes is not None:
        revised = _trim_to_budget(
            revised,
            available_minutes=available_minutes,
            planning_date=planning_date,
            use_time_tiebreaker=use_time_tiebreaker,
            revision_notes=revision_notes,
        )

    if not revised and _is_non_empty_plan_feasible(candidates, available_minutes):
        fallback = _best_fit_candidate(
            candidates,
            available_minutes=available_minutes,
            planning_date=planning_date,
            use_time_tiebreaker=use_time_tiebreaker,
        )
        if fallback is not None:
            revised = [fallback]
            revision_notes.append(
                f"Added fallback task '{fallback.description}' to avoid empty feasible plan."
            )

    final_check = self_check_plan(
        owner,
        scheduler,
        revised,
        candidates,
        constraints,
    )
    return revised, final_check, revision_notes


def run_ai_planner_pipeline(
    owner: Owner,
    scheduler: Scheduler,
    tasks: Sequence[Task],
    available_minutes: int | None,
    include_completed: bool = False,
    today_only_schedule: bool = True,
    use_time_tiebreaker: bool = False,
) -> PlannerOutput:
    """Run the full planning pipeline with trace, confidence, and warnings."""
    trace: list[dict[str, Any]] = []

    constraints = interpret_constraints(
        available_minutes=available_minutes,
        include_completed=include_completed,
        today_only_schedule=today_only_schedule,
        use_time_tiebreaker=use_time_tiebreaker,
    )
    trace.append(
        _trace_entry(
            step="interpret_constraints",
            input_summary=(
                f"available_minutes={constraints['available_minutes']}, "
                f"include_completed={constraints['include_completed']}, "
                f"today_only_schedule={constraints['today_only_schedule']}, "
                f"use_time_tiebreaker={constraints['use_time_tiebreaker']}"
            ),
            decision="Normalized planning controls.",
            result_count=len(tasks),
            minutes_used=0,
            status="ok",
            notes="Rejected negative budgets, set planning_date to today.",
        )
    )

    candidates = select_candidates(tasks, constraints)
    trace.append(
        _trace_entry(
            step="select_candidates",
            input_summary=f"input_tasks={len(tasks)}",
            decision="Applied filters and deterministic rank ordering.",
            result_count=len(candidates),
            minutes_used=0,
            status="ok" if candidates else "warning",
            notes="Empty candidate set is allowed and handled gracefully."
            if not candidates
            else "",
        )
    )

    drafted_schedule, skipped_tasks, drafted_minutes = draft_plan(
        candidates,
        available_minutes=constraints["available_minutes"],
    )
    trace.append(
        _trace_entry(
            step="draft_plan",
            input_summary=f"candidate_tasks={len(candidates)}",
            decision="Greedy selection under time budget.",
            result_count=len(drafted_schedule),
            minutes_used=drafted_minutes,
            status="ok",
            notes=f"Skipped {len(skipped_tasks)} task(s) due to budget."
            if skipped_tasks
            else "No tasks skipped.",
        )
    )

    initial_check = self_check_plan(
        owner,
        scheduler,
        drafted_schedule,
        candidates,
        constraints,
    )
    trace.append(
        _trace_entry(
            step="self_check_plan",
            input_summary=f"drafted_tasks={len(drafted_schedule)}",
            decision="Validated budget, conflict warnings, and feasibility.",
            result_count=len(initial_check["conflict_warnings"]),
            minutes_used=initial_check["minutes_used"],
            status="ok" if initial_check["is_valid"] else "warning",
            notes=_self_check_notes(initial_check),
        )
    )

    final_schedule, final_check, revision_notes = revise_plan_if_needed(
        owner,
        scheduler,
        drafted_schedule,
        candidates,
        constraints,
        initial_check,
    )
    trace.append(
        _trace_entry(
            step="revise_plan_if_needed",
            input_summary=f"initial_valid={initial_check['is_valid']}",
            decision="Ran one revision pass when needed.",
            result_count=len(final_schedule),
            minutes_used=final_check["minutes_used"],
            status="ok" if final_check["is_valid"] else "warning",
            notes="; ".join(revision_notes) if revision_notes else "No revision notes.",
        )
    )

    warnings: list[str] = []
    warnings.extend(final_check["conflict_warnings"])
    if not candidates:
        warnings.append("No candidate tasks match current planner constraints.")
    if not final_check["non_empty_when_feasible"]:
        warnings.append("Plan is empty even though at least one task could be scheduled.")

    confidence = _compute_confidence(
        final_schedule=final_schedule,
        candidates=candidates,
        final_check=final_check,
    )

    return PlannerOutput(
        final_schedule=final_schedule,
        trace=trace,
        confidence=confidence,
        warnings=warnings,
    )


def _trace_entry(
    step: str,
    input_summary: str,
    decision: str,
    result_count: int,
    minutes_used: int,
    status: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "step": step,
        "input_summary": input_summary,
        "decision": decision,
        "result_count": result_count,
        "minutes_used": minutes_used,
        "status": status,
        "notes": notes,
    }


def _candidate_sort_key(
    task: Task,
    planning_date: date,
    use_time_tiebreaker: bool,
) -> tuple[Any, ...]:
    due_today_rank = 0 if task.due_date == planning_date else 1
    base = (
        -task.priority,
        due_today_rank,
        task.duration_in_minutes,
    )
    if use_time_tiebreaker:
        base += (_time_key(task.time),)
    return base + (task.description.casefold(),)


def _time_key(value: str) -> tuple[int, int]:
    return tuple(map(int, value.split(":")))


def _is_non_empty_plan_feasible(
    candidates: Sequence[Task],
    available_minutes: int | None,
) -> bool:
    if not candidates:
        return False
    if available_minutes is None:
        return True
    return any(task.duration_in_minutes <= available_minutes for task in candidates)


def _self_check_notes(check_result: dict[str, Any]) -> str:
    if check_result["is_valid"]:
        return "All checks passed."

    notes: list[str] = []
    if not check_result["passes_budget"]:
        notes.append("Budget exceeded")
    if check_result["conflict_warnings"]:
        notes.append(f"Conflicts: {len(check_result['conflict_warnings'])}")
    if not check_result["non_empty_when_feasible"]:
        notes.append("Feasible plan should not be empty")
    return "; ".join(notes)


def _remove_conflicting_tasks(
    tasks: Sequence[Task],
    planning_date: date,
    use_time_tiebreaker: bool,
    revision_notes: list[str],
) -> list[Task]:
    tasks_by_time: dict[str, list[Task]] = {}
    for task in tasks:
        tasks_by_time.setdefault(task.time, []).append(task)

    revised: list[Task] = []
    for time_slot in sorted(tasks_by_time.keys()):
        grouped = tasks_by_time[time_slot]
        if len(grouped) == 1:
            revised.append(grouped[0])
            continue

        winner = min(
            grouped,
            key=lambda task: _candidate_sort_key(
                task,
                planning_date,
                use_time_tiebreaker,
            ),
        )
        revised.append(winner)
        removed_count = len(grouped) - 1
        revision_notes.append(
            f"Removed {removed_count} conflicting task(s) at {time_slot}; kept '{winner.description}'."
        )

    return sorted(
        revised,
        key=lambda task: _candidate_sort_key(
            task,
            planning_date,
            use_time_tiebreaker,
        ),
    )


def _trim_to_budget(
    tasks: Sequence[Task],
    available_minutes: int,
    planning_date: date,
    use_time_tiebreaker: bool,
    revision_notes: list[str],
) -> list[Task]:
    revised = list(tasks)
    while sum(task.duration_in_minutes for task in revised) > available_minutes and revised:
        remove_candidate = max(
            revised,
            key=lambda task: _candidate_sort_key(
                task,
                planning_date,
                use_time_tiebreaker,
            ),
        )
        revised.remove(remove_candidate)
        revision_notes.append(
            f"Removed '{remove_candidate.description}' to satisfy time budget."
        )
    return revised


def _best_fit_candidate(
    candidates: Sequence[Task],
    available_minutes: int | None,
    planning_date: date,
    use_time_tiebreaker: bool,
) -> Task | None:
    ordered = sorted(
        candidates,
        key=lambda task: _candidate_sort_key(
            task,
            planning_date,
            use_time_tiebreaker,
        ),
    )
    if available_minutes is None:
        return ordered[0] if ordered else None

    for task in ordered:
        if task.duration_in_minutes <= available_minutes:
            return task
    return None


def _compute_confidence(
    final_schedule: Sequence[Task],
    candidates: Sequence[Task],
    final_check: dict[str, Any],
) -> float:
    budget_score = 1.0 if final_check["passes_budget"] else 0.0
    conflict_score = 1.0 if not final_check["conflict_warnings"] else 0.0

    if not candidates:
        high_priority_coverage = 1.0
    else:
        highest_priority = max(task.priority for task in candidates)
        high_priority_candidates = [
            task for task in candidates if task.priority == highest_priority
        ]
        if not high_priority_candidates:
            high_priority_coverage = 1.0
        else:
            covered = sum(task in final_schedule for task in high_priority_candidates)
            high_priority_coverage = covered / len(high_priority_candidates)

    confidence = (
        (budget_score * 0.4)
        + (conflict_score * 0.3)
        + (high_priority_coverage * 0.3)
    )
    return max(0.0, min(1.0, round(confidence, 3)))
