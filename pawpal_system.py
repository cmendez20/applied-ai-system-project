from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    pet_name: str
    species: str


@dataclass
class Task:
    task_title: str
    duration_in_minutes: int
    priority: int


@dataclass
class User:
    owner_name: str
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this user."""
        pass

    def addTask(self, task: Task) -> None:
        """Add a task to this user's task list."""
        pass


class Scheduler:
    def generateSchedule(self, user: User, tasks: List[Task]) -> List[Task]:
        """Generate and return an ordered daily schedule of tasks."""
        pass
