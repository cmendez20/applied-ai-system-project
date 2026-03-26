from __future__ import annotations

from dataclasses import dataclass, field
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
    is_completed: bool = False
    priority: int = 1

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Task description cannot be empty.")
        if self.duration_in_minutes <= 0:
            raise ValueError("Task duration_in_minutes must be greater than 0.")
        if self.priority < 1:
            raise ValueError("Task priority must be at least 1.")
        if not self.frequency.strip():
            raise ValueError("Task frequency cannot be empty.")
        if not self.pet_id.strip():
            raise ValueError("Task pet_id cannot be empty.")

    def mark_completed(self) -> None:
        """Mark this task as complete."""
        self.is_completed = True

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


class Scheduler:
    def generate_schedule(
        self,
        tasks: List[Task],
        available_minutes: int | None = None,
        include_completed: bool = False,
    ) -> List[Task]:
        """Return tasks ordered by priority, duration, and description.

        Ordering rules:
        1) Higher priority first.
        2) For equal priority, shorter tasks first.
        3) For ties, alphabetical by description.
        """
        candidate_tasks = (
            tasks
            if include_completed
            else [task for task in tasks if not task.is_completed]
        )

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

    def generate_schedule_for_owner(
        self,
        owner: Owner,
        available_minutes: int | None = None,
        include_completed: bool = False,
    ) -> List[Task]:
        """Get owner tasks, then return an ordered schedule."""
        tasks = owner.get_tasks_for_pets()
        return self.generate_schedule(
            tasks,
            available_minutes=available_minutes,
            include_completed=include_completed,
        )
