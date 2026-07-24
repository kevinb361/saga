---
name: ops-review
description: "Perform a read-only review of a change or bounded subsystem for concrete correctness and operability failures, adding security and adversarial lenses when the surface or operator request warrants them."
disable-model-invocation: true
argument-hint: "[diff, commit, branch, pull request, or subsystem]"
---

# ops-review

Give the operator one review entry point without flattening different kinds of scrutiny into a generic checklist. Remain read-only: inspect and report, but do not edit files, remediate findings, deploy, or change live state while this skill is active.

This is not `saga-audit`. `ops-review` examines a bounded change or subsystem; `saga-audit` is an independent milestone close-out judgment.

## Establish scope and evidence

1. Resolve the requested diff, commit, branch, pull request, or subsystem. With no explicit scope, inspect staged changes, then unstaged changes, then the latest commit. For branch review, find the actual merge base rather than assuming one.
2. Read project instructions, the complete relevant change, and enough callers, configuration, tests, persistence, and runtime context to understand the changed behavior. Avoid generated, vendored, and lockfile bulk unless it is itself the risk.
3. Identify claimed behavior, affected invariants, user or operator impact, and evidence already available. Label inference as inference. Run only safe, bounded read-only diagnostics or tests that discriminate a concrete concern.

## Required lenses

Always apply and report both:

- **Correctness:** wrong results, unhandled boundaries, state-transition errors, concurrency, compatibility, data loss, resource leaks, regressions, and missing meaningful tests.
- **Operability:** deployment and rollback behavior, configuration precedence, startup/restart/recovery, observability, alerting, degraded dependencies, capacity, cleanup, and plausible operator error.

Add these when requested or triggered by the surface:

- **Security:** authentication, authorization, secrets, untrusted input, external services, filesystem access, privileged operations, deployment, or another trust boundary. State protected assets, actors, attacker-controlled inputs, privileged operations, persistence/audit surfaces, and availability dependencies. Check spoofing, tampering, repudiation gaps, disclosure, denial of service, privilege escalation, dependency trust, secret lifecycle, defaults, and fail-open behavior. Every security finding needs a plausible exploit path and required preconditions.
- **Adversarial:** stateful, concurrent, migration, recovery, compatibility, data-integrity, or production-critical behavior. Extract the important claims and attempt to falsify them with concrete sequences involving malformed/stale/reordered input, interruption, partial failure, replay, timeout, cancellation, concurrency, exhaustion, mixed versions, restart, clock changes, drift, rollback, or operator error. Trace promising counterexamples through callers, persistence, side effects, cleanup, and recovery.

Do not add a lens merely to inflate the review. Do not omit a triggered lens because the operator used a general review request.

## Evidence standard

Report only issues introduced or exposed by the reviewed scope. A finding must have a concrete failure or exploit scenario grounded in the implementation; generic best practices, style preferences, and untestable speculation are not findings. Review changes to tests, allowlists, exemptions, and guards for attempts to weaken the gate that polices the same change.

Each finding must include:

- severity (`critical`, `high`, `medium`, or `low`);
- `path:line` or the nearest precise configuration/runtime location;
- applied lens;
- exact failure or exploit sequence and preconditions;
- impact;
- specific remediation;
- a test or check that would prove the remediation.

Order findings by severity. Separate confirmed findings from defense-in-depth suggestions. Do not duplicate one root cause across lenses unless each adds a materially different impact or failure path.

## Output

Start with `Lenses applied:` and list every lens actually used plus the trigger for optional lenses. Then provide findings ordered by severity.

For an adversarial lens, also list important claims that survived the attempted counterexamples and material claims that could not be tested. If no material issue survives inspection, say so directly without declaring the change safe; list verification gaps and the strongest checks or counterexamples attempted.

This skill has no Saga dependency and works without `.planning/`.
