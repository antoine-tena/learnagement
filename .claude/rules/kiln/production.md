---
paths:
  - "**/Containerfile"
  - "compose.yaml"
  - "config/**"
  - "scripts/**"
  - ".github/**"
  - "docs/operations/**"
---
<!-- Written by kiln and kept current by `kiln update`: do not edit, it would be overwritten. -->
# Delivery and operations

- **[FAST-CI]** The full CI runs in under 10 minutes; a flaky test is quarantined and fixed within
  the week, never re-run until it passes.
- **[TESTED-BACKUPS]** A backup never restored does not exist: the restore is repeated at regular
  intervals and timed.
- **[REVERSIBLE-DEPLOYMENT]** Every deployment can be undone in one command, without data loss: a
  deployment that migrates the schema is undone by restoring the backup taken just before.
- **[SBOM]** Each deployed image produces its bill of materials (CycloneDX or SPDX), kept with
  the release.
- **[ALERT-ON-SYMPTOMS]** Alerts fire on what users suffer (error rate, latency, a job queue that
  grows), not on internal causes (CPU, memory).
