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

## Status

`PREREG.md` (predictions H1-H4, definitions, grading rules) is published here before the
feature-gate pages are downloaded or counted. `job.py` lists the feature-gates folder of
kubernetes/website at one pinned commit, reads every page and computes the statistics.
`test_k8s_gates.py` checks the parser and the arithmetic against hand-built fixtures.
Results, including `gates.json` (one row per gate), will be added under `results/` after one
run in a sealed container.

## Run it

    python -m unittest -v
    python job.py --data-dir ./data --out-dir ./out --allow-net

Standard library only, Python 3.10 or newer.

Part of a series of lifecycle studies of standards and proposal processes by MV2 of Munim,
Inc.: IETF RFCs (rfc-obsolescence-survival, rfc-errata-hfdu-graveyard), Python PEPs
(pep-lifecycle-census), W3C specifications (w3c-spec-lifecycle) and OpenJDK JEPs
(jep-lifecycle-census), all under github.com/munimtechnologies.

-- MV2, Munim, Inc.
