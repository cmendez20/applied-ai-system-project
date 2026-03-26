# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Three core actions a user should be able to perform:
  - Input their and their pet's basic info
  - Ability to add pet care tasks (what needs to happen, how long it takes, priority)
  - Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Briefly describe your initial UML design.
  - There should a model for a user, their pet, and a task. 
- What classes did you include, and what responsibilities did you assign to each?
  - User class which has an attribute of "owner_name"
  - Pet class which has an attribute of "pet_name" and "species"
  - Task class with attributes of task_title, duration_in_minutes, and priority.
  - Scheduler class with a method to generate the schedule.

**b. Design changes**

My design did change after I had copilot review my initial pawpal system skeleton. I added a relationship between Task & Pet so that a task could belong to a specific pet. Then, I updated my scheduler class so that it only used a single source of truth for the tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler currently considers the following constraints:
 - priority (higher first)
 - duration_in_minutes (shorter first after priority)
 - optional time tie-breaker (HH:MM) when priorities tie
 - completion status (include_completed false by default)
 - available_minutes budget (greedy fit within total time)
- Outside core ordering, it also support:
 - filtering by pet name/completion status
 - conflict detection warnings when two tasks share the same time
The constraint importance was chosen because I prioritized priority + limited time first because that matches a pet owner’s immediate need.

**b. Tradeoffs**

One tradeoff is that the scheduler uses a simple greedy strategy (priority-first with optional time tie-break), so it may not produce a globally optimal plan for all combinations of durations/times/conflicts.

However it is reasonable here for the project since t is fast, predictable, and easy to explain to users.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
