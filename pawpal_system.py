from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List


@dataclass
class Pet:
    pet_id: str
    pet_name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        if task.pet_id != self.pet_id:
            raise ValueError(
                f"Task pet_id '{task.pet_id}' does not match pet '{self.pet_id}'."
            )
        self.tasks.append(task)


@dataclass
class Task:
    description: str
    duration_in_minutes: int
    frequency: str
    pet_id: str
    due_date: date = field(default_factory=date.today)
    time: str = "00:00"
    is_completed: bool = False
    priority: int = 1

    def __post_init__(self) -> None:
        """Validate required task fields and value constraints."""
        if not self.description.strip():
            raise ValueError("Task description cannot be empty.")
        if self.duration_in_minutes <= 0:
            raise ValueError("Task duration_in_minutes must be greater than 0.")
        if self.priority < 1:
            raise ValueError("Task priority must be at least 1.")
        self.frequency = self.frequency.strip().lower()
        if not self.frequency:
            raise ValueError("Task frequency cannot be empty.")
        if not self.pet_id.strip():
            raise ValueError("Task pet_id cannot be empty.")
        time_parts = self.time.split(":")
        if len(time_parts) != 2 or not all(part.isdigit() for part in time_parts):
            raise ValueError("Task time must be in HH:MM format.")
        hours, minutes = map(int, time_parts)
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError("Task time must be a valid 24-hour value in HH:MM format.")

    def mark_completed(self) -> None:
        """Mark this task as complete."""
        self.is_completed = True

    def next_due_date(self) -> date | None:
        """Return the next due date for recurring tasks, if applicable."""
        if self.frequency == "daily":
            return self.due_date + timedelta(days=1)
        if self.frequency == "weekly":
            return self.due_date + timedelta(weeks=1)
        return None

    def mark_complete(self) -> None:
        """Backward-compatible alias for marking a task complete."""
        self.mark_completed()

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.is_completed = False


@dataclass
class Owner:
    owner_name: str
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if any(existing.pet_id == pet.pet_id for existing in self.pets):
            raise ValueError(f"Pet with id '{pet.pet_id}' already exists.")
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a task to this owner's task list and the matching pet."""
        pet = self.get_pet(task.pet_id)
        if pet is None:
            raise ValueError(
                f"Cannot add task for pet_id '{task.pet_id}': pet not found for owner."
            )

        self.tasks.append(task)
        pet.add_task(task)

    def get_pet(self, pet_id: str) -> Pet | None:
        """Return the pet matching pet_id, if present."""
        return next((pet for pet in self.pets if pet.pet_id == pet_id), None)

    def get_tasks_for_pets(self) -> List[Task]:
        """Return all owner tasks that belong to currently registered pets."""
        pet_ids = {pet.pet_id for pet in self.pets}
        return [task for task in self.tasks if task.pet_id in pet_ids]

    def filter_tasks(
        self,
        is_completed: bool | None = None,
        pet_name: str | None = None,
    ) -> List[Task]:
        """Filter tasks by completion status and/or pet name."""
        tasks = self.get_tasks_for_pets()

        if is_completed is not None:
            tasks = [task for task in tasks if task.is_completed == is_completed]

        if pet_name is not None:
            matching_pet_ids = {
                pet.pet_id
                for pet in self.pets
                if pet.pet_name.casefold() == pet_name.casefold()
            }
            tasks = [task for task in tasks if task.pet_id in matching_pet_ids]

        return tasks


class Scheduler:
    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by their HH:MM time value."""
        return sorted(
            tasks,
            key=lambda task: tuple(map(int, task.time.split(":"))),
        )

    def generate_schedule(
        self,
        tasks: List[Task],
        available_minutes: int | None = None,
        include_completed: bool = False,
        use_time_tiebreaker: bool = False,
    ) -> List[Task]:
        """Return tasks ordered by priority, with optional time tie-breaking."""
        candidate_tasks = (
            tasks
            if include_completed
            else [task for task in tasks if not task.is_completed]
        )

        if use_time_tiebreaker:
            ordered_tasks = sorted(
                candidate_tasks,
                key=lambda task: (
                    -task.priority,
                    tuple(map(int, task.time.split(":"))),
                    task.duration_in_minutes,
                    task.description,
                ),
            )
        else:
            ordered_tasks = sorted(
                candidate_tasks,
                key=lambda task: (
                    -task.priority,
                    task.duration_in_minutes,
                    task.description,
                ),
            )

        if available_minutes is None:
            return ordered_tasks
        if available_minutes < 0:
            raise ValueError("available_minutes cannot be negative.")

        scheduled: List[Task] = []
        used_minutes = 0
        for task in ordered_tasks:
            if used_minutes + task.duration_in_minutes > available_minutes:
                continue
            scheduled.append(task)
            used_minutes += task.duration_in_minutes
        return scheduled

    def detect_time_conflicts(
        self,
        owner: Owner,
        tasks: List[Task],
        include_completed: bool = False,
    ) -> List[str]:
        """Return warning messages when multiple tasks share the same scheduled time."""
        candidate_tasks = (
            tasks
            if include_completed
            else [task for task in tasks if not task.is_completed]
        )

        tasks_by_time: dict[str, List[Task]] = {}
        for task in candidate_tasks:
            tasks_by_time.setdefault(task.time, []).append(task)

        warnings: List[str] = []
        for time, grouped_tasks in sorted(tasks_by_time.items()):
            if len(grouped_tasks) < 2:
                continue

            pet_names = [
                owner.get_pet(task.pet_id).pet_name
                if owner.get_pet(task.pet_id) is not None
                else task.pet_id
                for task in grouped_tasks
            ]
            unique_pet_names = set(pet_names)
            task_labels = ", ".join(task.description for task in grouped_tasks)

            if len(unique_pet_names) == 1:
                pet_name = next(iter(unique_pet_names))
                warnings.append(
                    f"Warning: time conflict at {time} for {pet_name} ({task_labels})."
                )
            else:
                pets = ", ".join(sorted(unique_pet_names))
                warnings.append(
                    f"Warning: time conflict at {time} across pets [{pets}] ({task_labels})."
                )

        return warnings

    def generate_schedule_for_owner(
        self,
        owner: Owner,
        available_minutes: int | None = None,
        include_completed: bool = False,
        use_time_tiebreaker: bool = False,
    ) -> List[Task]:
        """Get owner tasks, then return an ordered schedule."""
        tasks = owner.get_tasks_for_pets()
        return self.generate_schedule(
            tasks,
            available_minutes=available_minutes,
            include_completed=include_completed,
            use_time_tiebreaker=use_time_tiebreaker,
        )

    def mark_task_complete(self, owner: Owner, task: Task) -> Task | None:
        """Mark a task complete and create the next recurring task when needed."""
        if task.is_completed:
            return None

        task.mark_completed()
        next_due_date = task.next_due_date()
        if next_due_date is None:
            return None

        next_task = Task(
            description=task.description,
            duration_in_minutes=task.duration_in_minutes,
            frequency=task.frequency,
            pet_id=task.pet_id,
            due_date=next_due_date,
            time=task.time,
            priority=task.priority,
        )
        owner.add_task(next_task)
        return next_task
