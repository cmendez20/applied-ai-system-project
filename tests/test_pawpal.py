from pawpal_system import Pet, Task


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
