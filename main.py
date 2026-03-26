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
            f"time: {task.time} | "
            f"{task.duration_in_minutes} min | "
            f"freq: {task.frequency} | priority: {task.priority} | {status}"
        )


def print_warnings(warnings: list[str]) -> None:
    print("\n=== Conflict Warnings ===")
    if not warnings:
        print("No time conflicts detected.")
        return

    for warning in warnings:
        print(warning)


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
            time="08:30",
        )
    )
    owner.add_task(
        Task(
            description="Feed breakfast",
            duration_in_minutes=10,
            frequency="daily",
            priority=4,
            pet_id="p2",
            time="07:30",
        )
    )
    owner.add_task(
        Task(
            description="Brush fur",
            duration_in_minutes=15,
            frequency="weekly",
            priority=2,
            pet_id="p1",
            time="18:00",
        )
    )
    owner.add_task(
        Task(
            description="Clean litter box",
            duration_in_minutes=12,
            frequency="daily",
            priority=3,
            pet_id="p2",
            time="07:00",
            is_completed=True,
        )
    )
    owner.add_task(
        Task(
            description="Evening walk",
            duration_in_minutes=25,
            frequency="daily",
            priority=3,
            pet_id="p1",
            time="19:00",
        )
    )
    owner.add_task(
        Task(
            description="Give medication",
            duration_in_minutes=5,
            frequency="daily",
            priority=5,
            pet_id="p1",
            time="07:30",
        )
    )

    scheduler = Scheduler()

    print("\n=== Added Tasks (Input Order) ===")
    print_schedule(owner, owner.tasks)

    print("\n=== Sorted by Time ===")
    tasks_sorted_by_time = scheduler.sort_by_time(owner.get_tasks_for_pets())
    print_schedule(owner, tasks_sorted_by_time)
    warnings = scheduler.detect_time_conflicts(owner, tasks_sorted_by_time)
    print_warnings(warnings)

    print("\n=== Priority Schedule with Time Tie-breaker ===")
    todays_schedule = scheduler.generate_schedule_for_owner(
        owner,
        use_time_tiebreaker=True,
    )
    print_schedule(owner, todays_schedule)

    print("\n=== Filtered: Completed Tasks ===")
    completed_tasks = owner.filter_tasks(is_completed=True)
    print_schedule(owner, completed_tasks)

    print("\n=== Filtered: Pending Tasks for Mochi ===")
    mochi_pending_tasks = owner.filter_tasks(is_completed=False, pet_name="Mochi")
    print_schedule(owner, mochi_pending_tasks)


if __name__ == "__main__":
    main()
