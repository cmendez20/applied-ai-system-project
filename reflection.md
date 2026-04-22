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

I used copilot in agent mode for design brainstorming, debugging, and code refactoring. 
Having copliot review and make suggestions to simplify or improve my code were the most helpful. 

**b. Judgment and verification**

When I initially created my UML design, the AI wanted to change my Owner class to "User."
I had to reject the AI suggestion and restate my intent. I made sure to verify
the changes AI made by creating & passing tests for each new feature. 

---

## 4. Testing and Verification

**a. What you tested**

What behaviors I tested:
  - Task completion status changes (mark_complete / mark_completed).
  - Task assignment to pets (adding a task increases the pet’s task list).
  - Chronological sorting by HH:MM (sort_by_time).
  - Recurrence creation when completing tasks (daily -> +1 day, weekly -> +7 days).
  - Non-recurring completion behavior (once does not create a new task).
  - Conflict detection for duplicate times (including cross-pet conflicts).
  - Conflict detection default behavior (ignores completed tasks unless explicitly included).
  - Empty-owner scheduling behavior (pet exists, no tasks -> empty schedule).
  - UI helper logic for conflict messaging, completion feedback, and due-date filtering.

Why these tests were important
  - They cover the core scheduling engine from input -> decision -> output.
  - They validate both “happy path” workflows and failure-prone edge logic.
  - They protect user trust: recurrence, ordering, and conflicts are the most visible behaviors in planning apps.
  - They verify non-crashing warning behavior (important for good UX).


**b. Confidence**

I am pretty confident that the scheduler works correctly since the current automated suite passes 
and covers key algorithms and several edge cases.

Edge cases I’d test next with more time:
  - Time parsing boundaries: 00:00, 23:59, invalid formats.
  - Same-time conflicts for the same pet vs different pets in separate assertions.
  - Recurrence across month/year boundaries (e.g., Dec 31 -> Jan 1).
  - Time-budget selection quality (greedy scheduling leaves/uses expected minutes).
  - Duplicate pet names with different IDs (pet-name filtering behavior).
  - Multi-day due-date scenarios (today-only filters in schedule + completion flow).

---

## 5. Reflection

**a. What went well**

I am most satisfied with shipping a working final project that satisfies the user's needs.

**b. What you would improve**

If I had another iteration, I would redesign the UI & UX on the streamlit UI.

**c. Key takeaway**

The one important thing I learned about working with AI on this project is how important it is
to come up with a great plan before implementation with AI.

---

## 6. Project 4 Responsible AI Addendum

**a. Limitations and potential biases**

The AI planner in this project is deterministic and rule-based, which is good for reproducibility,
but it still has limits. It optimizes using a fixed priority-first heuristic, so it may under-value
context that is hard to represent as a numeric priority (for example, stress level of a pet,
caregiver fatigue, or travel/setup overhead between tasks).

There is also potential bias in user-provided priorities. If a user consistently marks one class of
tasks as low priority, the system may repeatedly defer them even when they matter for long-term
health outcomes. In other words, the planner is only as fair as the inputs and scoring policy.

**b. Misuse risks and prevention steps**

One misuse risk is over-trusting the schedule as if it were medical advice. Another is using the
tool to justify neglecting tasks because they were not selected under a tight budget.

To reduce misuse, I designed guardrails and messaging that keep the human in control:
- conflict checks are warnings, not silent failures
- planner trace is visible so decisions can be inspected
- confidence is surfaced as a heuristic, not a guarantee
- users can run baseline scheduler mode and compare outputs

In future iterations, I would add stronger UI disclaimers (especially for medication tasks), and
explicitly require user confirmation when high-priority health tasks are skipped.

**c. Testing surprise**

The biggest testing surprise was how useful trace-based assertions were. Initially I focused on
final schedule outputs only, but validating each pipeline stage (`interpret`, `select`, `draft`,
`self_check`, `revise`) caught issues faster and made failures easier to diagnose.

I also found that deterministic fixtures with fixed times/priorities made tests much easier to
maintain than broad randomized scenarios.

**d. One helpful AI suggestion and one flawed AI suggestion**

Helpful AI suggestion:
- Add a dedicated planner output dataclass (`final_schedule`, `trace`, `confidence`, `warnings`).
  This improved interface clarity and made app integration and testing cleaner.

Flawed AI suggestion:
- Rename or reshape core domain concepts (for example, replacing `Owner` with a different user
  model) too early in the project. I rejected this because it did not match existing project scope
  and would have created unnecessary churn.

This contrast reinforced a key practice for me: use AI for acceleration, but keep architecture and
scope decisions aligned to explicit project requirements.
