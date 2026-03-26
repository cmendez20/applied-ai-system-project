from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status() -> None:
    task = Task(
        description="Evening walk",
        duration_in_minutes=20,
        frequency="daily",
        pet_id="pet-1",
    )

    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_adding_task_to_pet_increases_task_count() -> None:
    pet = Pet(pet_id="pet-1", pet_name="Mochi", species="dog")
    task = Task(
        description="Feed dinner",
        duration_in_minutes=10,
        frequency="daily",
        pet_id="pet-1",
    )

    initial_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1


def test_mark_task_complete_creates_next_daily_occurrence() -> None:
    owner = Owner(owner_name="Jordan")
    pet = Pet(pet_id="pet-1", pet_name="Mochi", species="dog")
    owner.add_pet(pet)
    task = Task(
        description="Morning walk",
        duration_in_minutes=30,
        frequency="daily",
        pet_id="pet-1",
        due_date=date(2026, 3, 26),
        time="08:00",
        priority=3,
    )
    owner.add_task(task)
    scheduler = Scheduler()

    next_task = scheduler.mark_task_complete(owner, task)

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 27)
    assert next_task.is_completed is False
    assert next_task.description == task.description
    assert len(owner.tasks) == 2


def test_mark_task_complete_creates_next_weekly_occurrence() -> None:
    owner = Owner(owner_name="Jordan")
    pet = Pet(pet_id="pet-1", pet_name="Mochi", species="dog")
    owner.add_pet(pet)
    task = Task(
        description="Nail trim",
        duration_in_minutes=15,
        frequency="weekly",
        pet_id="pet-1",
        due_date=date(2026, 3, 26),
        time="10:00",
        priority=2,
    )
    owner.add_task(task)
    scheduler = Scheduler()

    next_task = scheduler.mark_task_complete(owner, task)

    assert next_task is not None
    assert next_task.due_date == date(2026, 4, 2)


def test_mark_task_complete_does_not_create_non_recurring_occurrence() -> None:
    owner = Owner(owner_name="Jordan")
    pet = Pet(pet_id="pet-1", pet_name="Mochi", species="dog")
    owner.add_pet(pet)
    task = Task(
        description="Vet visit",
        duration_in_minutes=45,
        frequency="once",
        pet_id="pet-1",
        due_date=date(2026, 3, 26),
        time="14:00",
        priority=5,
    )
    owner.add_task(task)
    scheduler = Scheduler()

    next_task = scheduler.mark_task_complete(owner, task)

    assert task.is_completed is True
    assert next_task is None
    assert len(owner.tasks) == 1


def test_sort_by_time_returns_chronological_order() -> None:
    scheduler = Scheduler()
    tasks = [
        Task(
            description="Evening walk",
            duration_in_minutes=25,
            frequency="daily",
            pet_id="pet-1",
            time="19:00",
        ),
        Task(
            description="Breakfast",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            time="07:30",
        ),
        Task(
            description="Midday play",
            duration_in_minutes=15,
            frequency="daily",
            pet_id="pet-1",
            time="12:15",
        ),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [task.time for task in ordered] == ["07:30", "12:15", "19:00"]


def test_detect_time_conflicts_flags_duplicate_times() -> None:
    owner = Owner(owner_name="Jordan")
    owner.add_pet(Pet(pet_id="pet-1", pet_name="Mochi", species="dog"))
    owner.add_pet(Pet(pet_id="pet-2", pet_name="Luna", species="cat"))
    owner.add_task(
        Task(
            description="Feed breakfast",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            time="07:30",
        )
    )
    owner.add_task(
        Task(
            description="Give medication",
            duration_in_minutes=5,
            frequency="daily",
            pet_id="pet-2",
            time="07:30",
        )
    )

    scheduler = Scheduler()
    warnings = scheduler.detect_time_conflicts(owner, owner.get_tasks_for_pets())

    assert len(warnings) == 1
    assert "time conflict at 07:30" in warnings[0]


def test_generate_schedule_for_owner_returns_empty_for_pet_with_no_tasks() -> None:
    owner = Owner(owner_name="Jordan")
    owner.add_pet(Pet(pet_id="pet-1", pet_name="Mochi", species="dog"))

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule_for_owner(owner)

    assert schedule == []


def test_detect_time_conflicts_ignores_completed_by_default() -> None:
    owner = Owner(owner_name="Jordan")
    owner.add_pet(Pet(pet_id="pet-1", pet_name="Mochi", species="dog"))
    owner.add_task(
        Task(
            description="Completed task",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            time="09:00",
            is_completed=True,
        )
    )
    owner.add_task(
        Task(
            description="Pending task",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            time="09:00",
            is_completed=False,
        )
    )

    scheduler = Scheduler()

    default_warnings = scheduler.detect_time_conflicts(owner, owner.tasks)
    all_warnings = scheduler.detect_time_conflicts(
        owner,
        owner.tasks,
        include_completed=True,
    )

    assert default_warnings == []
    assert len(all_warnings) == 1
