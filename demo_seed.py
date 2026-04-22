from __future__ import annotations

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task


def available_demo_scenarios() -> list[str]:
    return [
        "normal_day",
        "tight_budget",
        "conflict_heavy",
    ]


def load_demo_scenario(name: str) -> Owner:
    builders = {
        "normal_day": _build_normal_day,
        "tight_budget": _build_tight_budget,
        "conflict_heavy": _build_conflict_heavy,
    }
    builder = builders.get(name)
    if builder is None:
        known = ", ".join(sorted(builders))
        raise ValueError(f"Unknown demo scenario '{name}'. Available: {known}.")
    return builder()


def _base_owner() -> Owner:
    owner = Owner(owner_name="Demo Jordan")
    owner.add_pet(Pet(pet_id="pet-1", pet_name="Mochi", species="dog"))
    owner.add_pet(Pet(pet_id="pet-2", pet_name="Luna", species="cat"))
    return owner


def _build_normal_day() -> Owner:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    owner = _base_owner()

    owner.add_task(
        Task(
            description="Morning walk",
            duration_in_minutes=25,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="07:30",
            priority=5,
        )
    )
    owner.add_task(
        Task(
            description="Feed Luna",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-2",
            due_date=today,
            time="07:45",
            priority=5,
        )
    )
    owner.add_task(
        Task(
            description="Lunch refill",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="12:30",
            priority=3,
        )
    )
    owner.add_task(
        Task(
            description="Evening play",
            duration_in_minutes=20,
            frequency="daily",
            pet_id="pet-2",
            due_date=today,
            time="18:30",
            priority=4,
        )
    )
    owner.add_task(
        Task(
            description="Next-day grooming",
            duration_in_minutes=15,
            frequency="weekly",
            pet_id="pet-1",
            due_date=tomorrow,
            time="11:00",
            priority=2,
        )
    )
    return owner


def _build_tight_budget() -> Owner:
    today = date.today()
    owner = _base_owner()

    owner.add_task(
        Task(
            description="Give medication",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-2",
            due_date=today,
            time="07:00",
            priority=5,
        )
    )
    owner.add_task(
        Task(
            description="Quick potty break",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="07:20",
            priority=4,
        )
    )
    owner.add_task(
        Task(
            description="Long park walk",
            duration_in_minutes=40,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="08:00",
            priority=3,
        )
    )
    owner.add_task(
        Task(
            description="Full grooming",
            duration_in_minutes=30,
            frequency="weekly",
            pet_id="pet-2",
            due_date=today,
            time="10:00",
            priority=2,
        )
    )
    return owner


def _build_conflict_heavy() -> Owner:
    today = date.today()
    owner = _base_owner()

    owner.add_task(
        Task(
            description="Feed Mochi",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="07:30",
            priority=4,
        )
    )
    owner.add_task(
        Task(
            description="Give Luna medication",
            duration_in_minutes=5,
            frequency="daily",
            pet_id="pet-2",
            due_date=today,
            time="07:30",
            priority=5,
        )
    )
    owner.add_task(
        Task(
            description="Brush Mochi",
            duration_in_minutes=8,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="07:30",
            priority=3,
        )
    )
    owner.add_task(
        Task(
            description="Walk Mochi",
            duration_in_minutes=20,
            frequency="daily",
            pet_id="pet-1",
            due_date=today,
            time="08:00",
            priority=4,
        )
    )
    owner.add_task(
        Task(
            description="Clean litter box",
            duration_in_minutes=10,
            frequency="daily",
            pet_id="pet-2",
            due_date=today,
            time="08:00",
            priority=3,
        )
    )
    return owner
