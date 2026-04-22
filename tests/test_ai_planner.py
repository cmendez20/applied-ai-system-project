from datetime import date

from ai_planner import run_ai_planner_pipeline
from pawpal_system import Owner, Pet, Scheduler, Task


def _owner_with_pet() -> Owner:
    owner = Owner(owner_name="Jordan")
    owner.add_pet(Pet(pet_id="pet-1", pet_name="Mochi", species="dog"))
    return owner


def test_ai_planner_respects_time_budget() -> None:
    owner = _owner_with_pet()
    scheduler = Scheduler()
    today = date.today()

    tasks = [
        Task(
            description="Long walk",
            duration_in_minutes=30,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="08:00",
            priority=5,
        ),
        Task(
            description="Feed breakfast",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="07:30",
            priority=4,
        ),
        Task(
            description="Quick brush",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="09:00",
            priority=3,
        ),
    ]

    output = run_ai_planner_pipeline(
        owner=owner,
        scheduler=scheduler,
        tasks=tasks,
        available_minutes=20,
        include_completed=False,
        today_only_schedule=True,
        use_time_tiebreaker=True,
    )

    assert sum(task.duration_in_minutes for task in output.final_schedule) <= 20


def test_ai_planner_prioritizes_high_priority_tasks() -> None:
    owner = _owner_with_pet()
    scheduler = Scheduler()
    today = date.today()

    tasks = [
        Task(
            description="Low priority play",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="10:00",
            priority=1,
        ),
        Task(
            description="Medication",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="08:00",
            priority=5,
        ),
    ]

    output = run_ai_planner_pipeline(
        owner=owner,
        scheduler=scheduler,
        tasks=tasks,
        available_minutes=10,
        include_completed=False,
        today_only_schedule=True,
        use_time_tiebreaker=True,
    )

    assert len(output.final_schedule) == 1
    assert output.final_schedule[0].description == "Medication"


def test_ai_planner_revises_on_conflict() -> None:
    owner = _owner_with_pet()
    scheduler = Scheduler()
    today = date.today()

    tasks = [
        Task(
            description="Nail trim",
            duration_in_minutes=15,
            frequency="weekly",
            pet_id="pet-1",
            due_date=today,
            time="09:00",
            priority=3,
        ),
        Task(
            description="Feed breakfast",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="09:00",
            priority=3,
        ),
    ]

    output = run_ai_planner_pipeline(
        owner=owner,
        scheduler=scheduler,
        tasks=tasks,
        available_minutes=30,
        include_completed=False,
        today_only_schedule=True,
        use_time_tiebreaker=True,
    )

    assert output.trace[3]["step"] == "self_check_plan"
    assert output.trace[3]["status"] == "warning"
    assert output.trace[4]["step"] == "revise_plan_if_needed"
    assert output.trace[4]["notes"] != "No revision needed."
    assert len(output.final_schedule) == 1
    assert output.final_schedule[0].description == "Feed breakfast"
    assert scheduler.detect_time_conflicts(owner, output.final_schedule) == []


def test_ai_planner_trace_contains_all_five_steps() -> None:
    owner = _owner_with_pet()
    scheduler = Scheduler()
    today = date.today()

    tasks = [
        Task(
            description="Morning walk",
            duration_in_minutes=20,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="07:00",
            priority=4,
        )
    ]

    output = run_ai_planner_pipeline(
        owner=owner,
        scheduler=scheduler,
        tasks=tasks,
        available_minutes=60,
        include_completed=False,
        today_only_schedule=True,
        use_time_tiebreaker=True,
    )

    assert [entry["step"] for entry in output.trace] == [
        "interpret_constraints",
        "select_candidates",
        "draft_plan",
        "self_check_plan",
        "revise_plan_if_needed",
    ]


def test_ai_planner_confidence_within_unit_interval() -> None:
    owner = _owner_with_pet()
    scheduler = Scheduler()
    today = date.today()

    tasks = [
        Task(
            description="Evening walk",
            duration_in_minutes=25,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="18:00",
            priority=2,
        )
    ]

    output = run_ai_planner_pipeline(
        owner=owner,
        scheduler=scheduler,
        tasks=tasks,
        available_minutes=15,
        include_completed=False,
        today_only_schedule=True,
        use_time_tiebreaker=True,
    )

    assert 0.0 <= output.confidence <= 1.0
