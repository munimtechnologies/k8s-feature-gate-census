# k8s-feature-gate-census

A pre-registered census of Kubernetes feature gates from the public Kubernetes
documentation source: how many releases gates spend in alpha and beta, how often they reach
stable, and whether the 2020 "prevent permabeta" policy (KEP-1635), the move to three
releases a year (KEP-2572) and "beta APIs off by default" (KEP-3136) show up in the record.
It also checks KEP-2572's unsourced claim that only 5% of features go from alpha to GA in
the minimum three releases.

By MV2 of Munim, Inc. (mv2@munimtech.com). The work was made with AI agents working in his
name. Code: Apache-2.0. Results and text: CC BY 4.0. The Kubernetes documentation it reads is
CC BY 4.0, (c) The Kubernetes Authors.

## Results, run 1 (graded against PREREG.md)

`PREREG.md` was committed on 2026-10-30 (UTC), before any page was downloaded. The job ran
once on 2026-10-31 in a sealed container (tests passed first) and read all 490 feature-gate
pages of kubernetes/website at commit a4a91ac (489 have stages; the folder listing was not
truncated). The newest release in the docs is 1.37 (V = 37). Today 97 gates are beta, 52
alpha, 94 stable, 14 deprecated, and 232 pages are kept for removed gates. Two predictions
held and two failed.

- **H1 FAILED: fast graduation is about twice as common as KEP-2572 says.** Of 68 gates
  first alpha in 1.10-1.18 that later reached stable, 8 (11.8%) reached stable at most two
  releases after alpha (rule: at most 10%). That is 9.4% of all 85 gates in the cohort.
  KEP-2572 gives 5% with no source. Across every release, 29 of 242 gates that went from
  alpha to stable (12.0%) did it in two releases or fewer; the median is 5 releases.
  The census counts gates, not KEPs, so this is an approximate replication.
- **H2 HELD: beta gates graduate faster since "prevent permabeta".** Of gates first beta in
  1.20-1.32, 66.5% (119 of 179) reached stable within four releases, against 43.3% (29 of
  67) for 1.10-1.18 (rule: at least 0.10 higher; it is 0.23 higher). Confounder stated in
  advance: since 1.22 a release lasts about four months instead of three, so four releases
  is more calendar time.
- **H3 HELD, by 0.004.** 21.1% (31 of 147) of gates first beta in 1.24-1.33 were off by
  default in beta, against 10.7% (11 of 103) for 1.14-1.23 (rule: at least 0.10 higher; it
  is 0.104 higher). The per-release counts do not look like a step at 1.24, when KEP-3136
  turned new beta APIs off (exploratory, after grading): 9 of 72 (12.5%) for 1.24-1.29, 22
  of 75 (29.3%) for 1.30-1.33, then 11 of 86 (12.8%) for 1.34-1.37. Read this as a bump in
  1.30-1.33, not as evidence that KEP-3136 changed gate defaults.
- **H4 FAILED: permabeta is rarer than predicted.** Of the 97 gates now in beta, 13 (13.4%)
  entered beta in 1.29 or earlier, eight or more releases before 1.37 (rule: at least 25%).
  The oldest are RotateKubeletServerCertificate (beta since 1.12), StorageVersionHash (1.15)
  and APIResponseCompression (1.16).

How blind: H2 was blind; H1, H3 and H4 were partly informed (labelled in `PREREG.md`).

Descriptives (no predictions): gates enter as alpha (400), beta (75), stable (4) or
deprecated (10). From beta to stable takes a median of 3 releases (270 gates). 48 gates were
removed without ever reaching stable. The oldest gates still in alpha are QOSReserved (since
1.11) and CustomCPUCFSQuotaPeriod (since 1.12). No page shows a stage order that runs
backwards, but the page format keeps one interval per stage, so it could not show one.

Spot checks against the live pages on 2026-10-31: RotateKubeletServerCertificate (alpha
1.7-1.11, beta from 1.12, on by default, not removed) and QOSReserved (alpha from 1.11, not
removed) match `gates.json`.

## Limits

The documentation is a summary, not the code: it keeps one interval per stage. Gates removed
before the per-gate pages existed may be missing, so early releases are thin (1 to 13 first
alphas per release for 1.3-1.9). Release counts are not calendar time. This census covers
gates, not KEPs. A companion study, munimtechnologies/kep-record-audit, compares these pages
with the KEPs' own milestones.

## Files

- `PREREG.md`: predictions H1-H4, definitions, grading rules (published before any data).
- `job.py`, `test_k8s_gates.py`: the code and its hand-built fixture tests.
- `results/run1-summary.json`: the graded output, with every descriptive.
- `results/gates.json`: one row per gate.

## Run it

    python -m unittest -v
    python job.py --data-dir ./data --out-dir ./out --allow-net

Standard library only, Python 3.10 or newer.

Part of a series of lifecycle studies of standards and proposal processes by MV2 of Munim,
Inc.: IETF RFCs (rfc-obsolescence-survival, rfc-errata-hfdu-graveyard), Python PEPs
(pep-lifecycle-census), W3C specifications (w3c-spec-lifecycle), OpenJDK JEPs
(jep-lifecycle-census) and Kubernetes KEP records (kep-record-audit), all under
github.com/munimtechnologies.

-- MV2, Munim, Inc.
