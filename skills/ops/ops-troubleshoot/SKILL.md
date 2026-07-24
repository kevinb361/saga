---
name: ops-troubleshoot
description: "Diagnose difficult or recurring code, configuration, service, host, or network failures with read-only evidence, falsifiable hypotheses, bounded remediation, and fresh verification."
disable-model-invocation: false
argument-hint: "[symptom, system, or failing check]"
---

# ops-troubleshoot

Find the cause instead of accumulating retries and folklore. Start from observable reality, change as little as possible, and prove that the original symptom—not merely a nearby test—has recovered.

## Process

1. **Define the failure.** Restate the exact symptom, affected scope, onset or last-known-good point, reproduction path, and what healthy means. Separate direct observations from reports and inference. If the symptom cannot yet be reproduced, define the safest observable proxy before changing anything.

2. **Classify risk before commands.** Label proposed actions `inspect-only`, `repo-only`, `live-mutation`, or `destructive`. Inspection is not permission to restart, deploy, edit live configuration, clear state, fail over traffic, or power-cycle equipment. For live or destructive work, state the target, blast radius, rollback or recovery path, and evidence expected; stop unless the operator has approved that bounded mutation.

3. **Gather read-only evidence first.** Inspect the smallest relevant path across the actual failure domains:
   - **Code:** failing test or request, traceback, recent diff, call path, inputs, and dependency boundary.
   - **Configuration:** effective values, precedence, syntax, rendered output, and drift from the known-good source.
   - **Service:** current health, status, logs in a narrow time window, dependencies, listeners, and recent restarts.
   - **Host:** resource pressure, filesystem, process, clock, kernel, package/runtime version, and relevant system events.
   - **Network:** name resolution, route, address/port reachability, policy or firewall path, latency/loss, and both endpoints when available.

   Prefer bounded native tools and live readback over assumptions or stale documentation. Preserve timestamps, exact errors, versions, and commands needed to compare before and after.

4. **Build a ranked hypothesis ledger.** Keep no more than three active hypotheses. For each, record:
   - evidence for it;
   - evidence against it;
   - the cheapest safe discriminator;
   - the result that would falsify it.

   Rank by fit to evidence, not familiarity. Do not repeat a failed command unchanged, shotgun unrelated fixes, or treat correlation as cause.

5. **Test one discriminator at a time.** Run the smallest read-only test that separates the top hypotheses. Update the ledger from the observed result before choosing the next test. If evidence contradicts the working theory, discard or demote it rather than defending it.

6. **Apply the smallest coherent remediation.** Explain the causal chain the change addresses. Prefer the authoritative source over an emergency live edit, preserve rollback material, and avoid opportunistic cleanup. Reclassify risk if the proposed fix crosses from repository work into a live system. Never weaken a guard, test, alert, or security control merely to make the gate green.

7. **Verify freshly.** Re-run the original reproduction or observe the original live-health signal after the change. Also check the nearest regression surface, dependent health, and persistence across the relevant reload or restart boundary. A command exit code alone is not proof when users, traffic, or a service health signal exposed the failure.

8. **Report the outcome.** State root cause and confidence, evidence that ruled out alternatives, exact remediation, verification performed, remaining uncertainty, rollback state, and any follow-up that is genuinely separate work.

## Stop and escalate

Stop speculative retries when evidence is unavailable, the next discriminator is destructive or broader than approved, two coherent remediation attempts fail, the blast radius is unclear, or the issue needs vendor/provider access. Return the hypothesis ledger and the exact evidence needed next so another operator does not restart the investigation from zero.

This skill has no Saga dependency and must work in a directory without `.planning/`.
