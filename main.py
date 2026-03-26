from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(owner: Owner, schedule: list[Task]) -> None:
    print("\n=== Today's Schedule ===")
    print(f"Owner: {owner.owner_name}")
    print(f"Total tasks scheduled: {len(schedule)}")
    print("-" * 56)

    if not schedule:
        print("No tasks scheduled today.")
        return

    for index, task in enumerate(schedule, start=1):
        pet = owner.get_pet(task.pet_id)
        pet_label = pet.pet_name if pet else f"Unknown pet ({task.pet_id})"
        status = "Done" if task.is_completed else "Pending"
        print(
            f"{index:>2}. [{pet_label}] {task.description} | "
            f"{task.duration_in_minutes} min | "
            f"freq: {task.frequency} | priority: {task.priority} | {status}"
        )


def main() -> None:
    owner = Owner(owner_name="Jordan")

    dog = Pet(pet_id="p1", pet_name="Mochi", species="dog")
    cat = Pet(pet_id="p2", pet_name="Luna", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    owner.add_task(
        Task(
            description="Morning walk",
            duration_in_minutes=30,
            frequency="daily",
            priority=3,
            pet_id="p1",
        )
    )
    owner.add_task(
        Task(
            description="Feed breakfast",
            duration_in_minutes=10,
            frequency="daily",
            priority=4,
            pet_id="p2",
        )
    )
    owner.add_task(
        Task(
            description="Brush fur",
            duration_in_minutes=15,
            frequency="weekly",
            priority=2,
            pet_id="p1",
        )
    )

    scheduler = Scheduler()
    todays_schedule = scheduler.generate_schedule_for_owner(owner)
    print_schedule(owner, todays_schedule)


if __name__ == "__main__":
    main()
