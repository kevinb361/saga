---
name: ops-upgrade
description: "Plan and execute upgrades for application dependencies, OS packages, containers, services, runtimes, collections, or toolchains with authoritative research, staged compatibility checks, rollback, risk gates, and post-upgrade health proof."
disable-model-invocation: false
argument-hint: "[component, system, or desired version]"
---

# ops-upgrade

Upgrade the system the operator actually has, not an imagined clean install. Preserve the native management path, keep unrelated cleanup out, and verify both the selected version and useful health.

## Process

1. **Inventory the current state.** Identify the target and owner, installed and desired versions, source repository or managed hosts, package/image/service manager, lockfiles or pinning, configuration source of truth, runtime constraints, dependent services, canonical gate, and available health signals. Distinguish direct from transitive dependencies and locally built from vendor-managed artifacts.

2. **Classify the upgrade.** State which class applies: application dependencies, OS packages, containers, services, runtimes, collections, or toolchains. Separate security-critical updates, patches/minors, coupled families, runtime changes, and majors. Do not bundle unrelated classes merely because one command can update them together.

3. **Research authoritative sources.** Read upstream or vendor release notes, migration guides, security advisories, compatibility matrices, image provenance, and deprecation/removal notices for every skipped major and relevant intermediate release. Record required configuration or data migrations, changed defaults, minimum dependencies, downgrade limits, and known issues. Search snippets and version numbers alone are not release-note evidence.

4. **Establish baseline and rollback.** Capture current resolved versions, configuration/rendered state, health, and the exact reproduction or smoke check. Define the rollback artifact and procedure before mutation: lockfile or manifest revert, previous package version/repository snapshot, prior image digest, service configuration backup, VM/filesystem snapshot, or vendor-supported downgrade. State where rollback stops being safe, especially after schema or data migration.

5. **Plan coherent stages.** Upgrade one risk tier or tightly coupled family at a time. Put prerequisite runtimes and format migrations before consumers; keep runtime and toolchain majors separate unless the compatibility matrix requires them together. For each stage name the expected files/hosts, compatibility checks, health proof, rollback trigger, and observation window.

6. **Gate mutation explicitly.** Classify each stage as `inspect-only`, `repo-only`, `live-mutation`, or `destructive`. Repository edits may proceed under the operator's upgrade request. Before live or destructive action, disclose target, blast radius, downtime or traffic effect, rollback/recovery path, and post-change evidence; stop unless that bounded mutation is explicitly approved. A request to assess or plan an upgrade is not permission to refresh indexes, pull images, restart services, alter repositories, or change managed hosts.

7. **Execute the approved stage.** Use the system's native manager and authoritative source. Preserve lockfile discipline and exact image digests or repository pins where the project uses them. Inspect the resolved transaction or diff before acceptance. Do not disable tests, guards, signature checks, or dependency constraints to force resolution. On failure, investigate before retrying or widening scope.

8. **Verify after every stage.** Prove the installed or resolved version from the actual runtime/graph, then run focused compatibility checks and the canonical gate. For live systems, also verify service health, logs, dependencies, representative traffic or function, persistence across the relevant reload/restart boundary, and absence of a new alert or crash loop. A successful installer exit is not health proof; a changed manifest is not resolved-version proof.

9. **Close or roll back.** Compare against the baseline and declared success criteria. Roll back when a trigger fires rather than stacking speculative fixes. Report versions before/after, sources reviewed, stages completed, verification evidence, health observation window, rollback state, deferred majors, and remaining risk.

## Safety boundary

Default to inspection and planning when scope, approval, backup, or health evidence is unclear. Never claim a vulnerability is fixed without verifying the resolved dependency graph or deployed runtime. Never claim a live upgrade is complete without post-upgrade health verification.

This skill has no Saga dependency and works without `.planning/`.
