classDiagram
    class User {
        +String owner_name
        +addPet(pet: Pet)
        +addTask(task: Task)
    }

    class Pet {
        +String pet_name
        +String species
    }

    class Task {
        +String task_title
        +int duration_in_minutes
        +int priority
    }

    class Scheduler {
        +generateSchedule(user: User, tasks: List~Task~): List~Task~
    }

    User "1" --> "1..*" Pet : owns
    User "1" --> "0..*" Task : manages
    Scheduler ..> Task : orders
    Scheduler ..> User : uses constraints
