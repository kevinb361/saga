---
name: ops-grill-me
description: "Pressure-test a vague goal, plan, or decision through bounded hard questions, then return a concise operator handoff. Use only when the operator explicitly asks to be questioned or challenged."
disable-model-invocation: true
argument-hint: "[goal, plan, or decision]"
---

# ops-grill-me

Turn fuzzy intent into something an operator can act on. Be direct and skeptical without becoming theatrical, hostile, or an endless interview.

## Process

1. **Inspect before asking.** Read the supplied material and the smallest relevant set of local guidance, current state, documentation, configuration, or prior decisions available through read-only tools. Do not ask the operator for facts that are already discoverable. If there is no inspectable context, say what is missing rather than pretending it was checked.

2. **Reflect the current shape.** State the apparent goal in one sentence, then name the assumptions, contradictions, or undefined terms most likely to change the answer. Distinguish observed facts from your inference.

3. **Ask one bounded round.** Ask at most five high-value questions at a time. Prefer questions that eliminate a branch or expose a real trade-off:
   - What outcome must be true when this is done?
   - What must not change or break?
   - Which failure is acceptable, and which is not?
   - What evidence would settle this decision?
   - What are we assuming because it is convenient rather than verified?

   Do not ask for biography, generic background, or exhaustive preference lists. After each answer, briefly update the model of the problem. Run another round only when the answer opened a material branch. Stop after three rounds unless the operator explicitly asks to continue.

4. **Pressure-test the emerging answer.** Challenge happy-path thinking: operational burden, dependencies, blast radius, rollback, degraded behavior, ownership, hidden recurring work, and the cost of doing nothing. Offer a concrete counterexample when one exists. Do not manufacture objections merely to sound rigorous.

5. **Return the handoff.** End with exactly these headings:
   - **Goal** — one observable outcome.
   - **Constraints** — hard limits and must-not-break conditions.
   - **Decisions** — choices actually settled during the exchange.
   - **Unknowns** — unresolved questions that can change the plan.
   - **Next action** — the smallest sensible next move and its proof condition.

## Mutation boundary

This skill is read-only by default. Explicitly invoking `ops-grill-me` authorizes questioning and inspection, not file edits, commands that change state, task creation, deployment, or documentation writes. If the operator asks to preserve the handoff, confirm the destination and use the appropriate documentation or project-state workflow.

## Stop conditions

Stop and return the best honest handoff when the goal is actionable, the operator says enough, further questions would not change the next action, or required evidence is unavailable. Never fill an unknown with a confident guess.
