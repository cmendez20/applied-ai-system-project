from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ai_planner import interpret_constraints, run_ai_planner_pipeline, select_candidates
from pawpal_system import Owner, Pet, Scheduler, Task


@dataclass(frozen=True)
class EvalScenario:
    name: str
    tasks: list[Task]
    available_minutes: int | None
    include_completed: bool
    today_only_schedule: bool
    use_time_tiebreaker: bool
    expected_non_empty: bool
    expected_includes_highest_priority: bool
    max_conflict_count: int


def _build_owner() -> Owner:
    owner = Owner(owner_name="Jordan")
    owner.add_pet(Pet(pet_id="pet-1", pet_name="Mochi", species="dog"))
    owner.add_pet(Pet(pet_id="pet-2", pet_name="Luna", species="cat"))
    return owner


def _task(
    *,
    description: str,
    minutes: int,
    priority: int,
    pet_id: str,
    due_date: date,
    time: str,
    is_completed: bool = False,
) -> Task:
    return Task(
        description=description,
        duration_in_minutes=minutes,
        frequency="daily",
        pet_id=pet_id,
        due_date=due_date,
        time=time,
        is_completed=is_completed,
        priority=priority,
    )


def _build_scenarios(today: date) -> list[EvalScenario]:
    off_day = date(2000, 1, 1)

    return [
        EvalScenario(
            name="tight_budget_prefers_high_priority",
            tasks=[
                _task(
                    description="Medication",
                    minutes=15,
                    priority=5,
                    pet_id="pet-1",
                    due_date=today,
                    time="08:00",
                ),
                _task(
                    description="Long walk",
                    minutes=25,
                    priority=3,
                    pet_id="pet-1",
                    due_date=today,
                    time="09:00",
                ),
                _task(
                    description="Playtime",
                    minutes=10,
                    priority=2,
                    pet_id="pet-2",
                    due_date=today,
                    time="10:00",
                ),
            ],
            available_minutes=15,
            include_completed=False,
            today_only_schedule=True,
            use_time_tiebreaker=True,
            expected_non_empty=True,
            expected_includes_highest_priority=True,
            max_conflict_count=0,
        ),
        EvalScenario(
            name="conflict_heavy_revises_to_non_conflicting",
            tasks=[
                _task(
                    description="Feed breakfast",
                    minutes=10,
                    priority=4,
                    pet_id="pet-1",
                    due_date=today,
                    time="07:30",
                ),
                _task(
                    description="Give medication",
                    minutes=5,
                    priority=5,
                    pet_id="pet-2",
                    due_date=today,
                    time="07:30",
                ),
                _task(
                    description="Brush fur",
                    minutes=8,
                    priority=2,
                    pet_id="pet-1",
                    due_date=today,
                    time="08:00",
                ),
            ],
            available_minutes=40,
            include_completed=False,
            today_only_schedule=True,
            use_time_tiebreaker=True,
            expected_non_empty=True,
            expected_includes_highest_priority=True,
            max_conflict_count=0,
        ),
        EvalScenario(
            name="exclude_completed_filters_finished_task",
            tasks=[
                _task(
                    description="Completed medicine",
                    minutes=10,
                    priority=5,
                    pet_id="pet-1",
                    due_date=today,
                    time="09:00",
                    is_completed=True,
                ),
                _task(
                    description="Pending meal",
                    minutes=10,
                    priority=4,
                    pet_id="pet-2",
                    due_date=today,
                    time="09:30",
                ),
            ],
            available_minutes=15,
            include_completed=False,
            today_only_schedule=True,
            use_time_tiebreaker=False,
            expected_non_empty=True,
            expected_includes_highest_priority=True,
            max_conflict_count=0,
        ),
        EvalScenario(
            name="include_completed_can_schedule_both",
            tasks=[
                _task(
                    description="Completed grooming",
                    minutes=10,
                    priority=3,
                    pet_id="pet-1",
                    due_date=today,
                    time="11:00",
                    is_completed=True,
                ),
                _task(
                    description="Pending walk",
                    minutes=10,
                    priority=5,
                    pet_id="pet-2",
                    due_date=today,
                    time="11:30",
                ),
            ],
            available_minutes=25,
            include_completed=True,
            today_only_schedule=True,
            use_time_tiebreaker=False,
            expected_non_empty=True,
            expected_includes_highest_priority=True,
            max_conflict_count=0,
        ),
        EvalScenario(
            name="today_only_with_off_day_tasks_is_empty",
            tasks=[
                _task(
                    description="Archive task one",
                    minutes=10,
                    priority=5,
                    pet_id="pet-1",
                    due_date=off_day,
                    time="06:00",
                ),
                _task(
                    description="Archive task two",
                    minutes=10,
                    priority=4,
                    pet_id="pet-2",
                    due_date=off_day,
                    time="06:30",
                ),
            ],
            available_minutes=30,
            include_completed=False,
            today_only_schedule=True,
            use_time_tiebreaker=False,
            expected_non_empty=False,
            expected_includes_highest_priority=True,
            max_conflict_count=0,
        ),
        EvalScenario(
            name="zero_budget_returns_empty_when_tasks_exist",
            tasks=[
                _task(
                    description="Quick walk",
                    minutes=5,
                    priority=5,
                    pet_id="pet-1",
                    due_date=today,
                    time="12:00",
                ),
                _task(
                    description="Water refill",
                    minutes=5,
                    priority=3,
                    pet_id="pet-2",
                    due_date=today,
                    time="12:30",
                ),
            ],
            available_minutes=0,
            include_completed=False,
            today_only_schedule=True,
            use_time_tiebreaker=True,
            expected_non_empty=False,
            expected_includes_highest_priority=False,
            max_conflict_count=0,
        ),
    ]


def _includes_highest_priority_task(
    final_schedule: list[Task],
    candidates: list[Task],
) -> bool:
    if not candidates:
        return True
    if not final_schedule:
        return False

    highest_priority = max(task.priority for task in candidates)
    return any(task.priority == highest_priority for task in final_schedule)


def _evaluate_scenario(scenario: EvalScenario) -> dict[str, object]:
    owner = _build_owner()
    scheduler = Scheduler()

    output = run_ai_planner_pipeline(
        owner=owner,
        scheduler=scheduler,
        tasks=scenario.tasks,
        available_minutes=scenario.available_minutes,
        include_completed=scenario.include_completed,
        today_only_schedule=scenario.today_only_schedule,
        use_time_tiebreaker=scenario.use_time_tiebreaker,
    )

    constraints = interpret_constraints(
        available_minutes=scenario.available_minutes,
        include_completed=scenario.include_completed,
        today_only_schedule=scenario.today_only_schedule,
        use_time_tiebreaker=scenario.use_time_tiebreaker,
    )
    candidates = select_candidates(scenario.tasks, constraints)

    used_minutes = sum(task.duration_in_minutes for task in output.final_schedule)
    passes_budget = (
        True
        if scenario.available_minutes is None
        else used_minutes <= scenario.available_minutes
    )

    includes_highest_priority = _includes_highest_priority_task(
        output.final_schedule,
        candidates,
    )

    final_conflicts = scheduler.detect_time_conflicts(
        owner,
        output.final_schedule,
        include_completed=scenario.include_completed,
    )
    conflict_count_within_threshold = len(final_conflicts) <= scenario.max_conflict_count
    non_empty_when_expected = bool(output.final_schedule) == scenario.expected_non_empty

    passed = (
        passes_budget
        and includes_highest_priority == scenario.expected_includes_highest_priority
        and conflict_count_within_threshold
        and non_empty_when_expected
    )

    return {
        "name": scenario.name,
        "passed": passed,
        "passes_budget": passes_budget,
        "includes_highest_priority": includes_highest_priority,
        "expected_includes_highest_priority": scenario.expected_includes_highest_priority,
        "conflict_count_within_threshold": conflict_count_within_threshold,
        "conflict_count": len(final_conflicts),
        "non_empty_when_expected": non_empty_when_expected,
        "confidence": output.confidence,
    }


def main() -> int:
    scenarios = _build_scenarios(date.today())
    results = [_evaluate_scenario(scenario) for scenario in scenarios]

    print("PawPal+ AI Planner Evaluation")
    print("----------------------------")
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            "- "
            f"[{status}] {result['name']} | "
            f"passes_budget={result['passes_budget']} | "
            f"includes_highest_priority={result['includes_highest_priority']} "
            f"(expected={result['expected_includes_highest_priority']}) | "
            f"conflict_count_within_threshold={result['conflict_count_within_threshold']} "
            f"(count={result['conflict_count']}) | "
            f"non_empty_when_expected={result['non_empty_when_expected']} | "
            f"confidence={result['confidence']:.3f}"
        )

    passed_count = sum(1 for result in results if result["passed"])
    avg_confidence = sum(float(result["confidence"]) for result in results) / len(results)
    failed_names = [str(result["name"]) for result in results if not result["passed"]]

    print("\nSummary")
    print(f"- passed/total: {passed_count}/{len(results)}")
    print(f"- avg confidence: {avg_confidence:.3f}")
    print(
        "- failed scenario names: "
        + (", ".join(failed_names) if failed_names else "None")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
