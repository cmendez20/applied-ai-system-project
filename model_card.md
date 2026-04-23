# Reflection

I am most satisfied with shipping a working final project that satisfies the rubric's needs.
If I had another iteration, I would redesign the UI & UX on the streamlit UI.
The most important thing I learned about working with AI on this project is how important it is
to come up with a great plan before implementation with AI.

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
