# Pre-registration: Kubernetes feature-gate stage census, run 1

**By MV2 of Munim, Inc. Prepared with AI agents working in his name.**
**Filed: 2026-10-30 (UTC), before the feature-gate pages were downloaded or counted.**
Code: Apache-2.0. Text: CC BY 4.0.

## Question

Kubernetes ships new behaviour behind feature gates that move through alpha, beta and
stable (GA) stages, one minor release at a time. How fast do gates actually move between
stages, and did three documented process changes show up in the record?

- **KEP-1635 "Prevent permabeta"** (Kubernetes 1.19, August 2020): beta REST APIs must
  graduate, move to a new beta, or be deprecated within about three releases.
- **KEP-2572** (formal from 1.22): three releases a year instead of four. Its text says,
  with no citation, that "only 5% of Kubernetes features advanced from Alpha to GA in the
  minimum 3 releases".
- **KEP-3136 "Beta APIs off by default"** (1.24): new beta APIs are no longer enabled by
  default. The KEP says it does not change the feature-gate lifecycle (beta gates stay on by
  default), but a gate whose feature needs a new beta API cannot do much while that API is
  off, so the policy could still spill over into gate defaults.

## Data

Every feature-gate page in the Kubernetes documentation source,
`kubernetes/website/content/en/docs/reference/command-line-tools-reference/feature-gates/`,
at the commit that is the tip of `main` when the job runs (the commit hash is recorded).
Each page lists the gate's stages with `defaultValue`, `fromVersion` and `toVersion`, and
pages of removed gates are kept with `removed: true`. The job lists the folder through the
GitHub API and reads each page from raw.githubusercontent.com. Pages whose names start with
`_` are skipped. Before filing, five pages were read by hand to learn the format
(CSIMigration, EphemeralContainers, HPAScaleToZero, CPUManagerPolicyBetaOptions and the
folder listing); no counts were made.

## Definitions

- **Release** = the minor number of a `1.x` version (1.19 -> 19).
- **First alpha / beta / stable release** of a gate = the lowest `fromVersion` among its
  entries of that stage ("GA" counts as stable).
- **Default of the beta stage** = `defaultValue` of the gate's earliest beta entry.
- **V** = the highest release named anywhere in the folder (the newest release the docs
  cover).
- **Current stage** = "removed" for removed gates, otherwise the stage of the entry with the
  highest `fromVersion`.

## Predictions and rules

Labels say how blind each one is.

**H1 (replication of KEP-2572's 5%; partly informed by that sentence).** Among gates whose
first alpha release is 10-18 and that later reached stable, the share that reached stable
no more than 2 releases after first alpha (alpha N, beta N+1, GA N+2: "the minimum 3
releases") is at most 0.10. HELD if share <= 0.10, else FAILED. The share of all such gates
(graduated or not) is also reported.

**H2 (blind: no stage durations were counted).** Gates whose first beta release is 20-32
(after KEP-1635) reached stable within 4 releases of first beta more often than gates whose
first beta release is 10-18 (before it), by at least 0.10. HELD if new >= old + 0.10, else
FAILED; NULL if V < 36 (not every new-cohort gate would have 4 releases of follow-up).
Release 19 is left out as the transition. Known confounder: after 1.22 a release lasts
about 4 months instead of 3, so 4 releases is more calendar time.

**H3 (partly informed: KEP-3136 is about APIs, and says gate defaults do not change; this
tests for spillover).** The share of gates whose beta stage is off by default is at least 0.10 higher for first beta releases 24-33 than for 14-23.
HELD if new >= old + 0.10, else FAILED.

**H4 (partly informed: two long-lived beta gates were seen in a public table).** Of gates
whose current stage is beta, at least 25% entered beta 8 or more releases before V.
HELD if share >= 0.25, else FAILED.

## Descriptives (no predictions)

Entry-stage and current-stage counts; first alpha, beta and stable releases per release;
releases from alpha to stable and from beta to stable; per first-beta release, how many
reached stable within 4 releases and how many were off by default; gates removed without
ever reaching stable; gates whose stage order runs backwards; the 15 oldest current beta and
alpha gates. `gates.json` gives one row per gate.

## Limits

The documentation is a summary, not the code: it keeps one interval per stage, so a gate
sent back from beta to alpha (EphemeralContainers in 1.22) can look like a straight path.
Gates removed before the per-gate pages were created may be missing, so early releases are
thinner; the job reports first-alpha counts per release so this can be seen. Release counts
are not calendar time. This census covers gates, not KEPs: one KEP can add several gates,
and some KEPs add none, so H1 is an approximate replication of KEP-2572's figure, whose
method is not published.

## Nearest prior work

arXiv 2604.15872 ("Feature Toggle Dynamics in Large-Scale Systems", 2026) measures whole
feature-gate lifespans in Kubernetes from `kube_features.go` history (median about 734
days) but reports no per-stage durations and does not test KEP-1635, KEP-2572 or KEP-3136.
A public gist by Davanum Srinivas (November 2025) tabulates each current gate's stage ranges
with stage counts and no further analysis. KEP-2572 states the 5% figure without a source.
Searches on 2026-10-30 found no study of stage-to-stage graduation times by cohort or of
these policies' effect on the feature-gate record.
