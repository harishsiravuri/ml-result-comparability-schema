# Comparability Certificates and Schema

Machine-readable schema artifacts for the cross-paper result-comparability resource:
protocol-qualified result records, comparability certificates, and query-conditioned
comparability templates. This repository is the schema companion to the dataset release
at [`ml-result-comparability`](https://github.com/harishsiravuri/ml-result-comparability)
(Zenodo concept DOI [10.5281/zenodo.21715275](https://doi.org/10.5281/zenodo.21715275)).

The format is specified in the short paper "A Schema for Comparing Results Across
ML Papers" (Siravuri and Alhoori). The dataset, the protocol-partitioned leaderboards, and the
census findings are presented in the companion resource paper "Cross-Paper Result
Comparability: A Dataset, Protocol-Partitioned Leaderboards, and a Census",
accepted and presented at the AI4SciSci 2026 workshop (JCDL 2026); proceedings
to appear.

## Contents

- `comparability_certificates.jsonl` -- 9,471 comparability certificates: all 3,058
  released census candidate pairs, plus 6,413 leaderboard pairs covering the top-10
  entries of each of the 215 multi-protocol leaderboards. One JSON object per line.
  Each certificate records the query template, the two records with their observed
  protocols, per-facet relations (observed-same, observed-different, or missing),
  the normalizations applied, a four-way status in which `unknown` is a first-class
  outcome, a six-way typed outcome, and two auditability fields (`implied_status`,
  `self_consistent`). Provenance is pointer-only: arXiv identifier, source location,
  and value. No excerpt text is redistributed.
- `schemas/comparability_certificate.schema.json` -- the certificate schema
  (JSON Schema, draft 2020-12).
- `schemas/query_templates.json` -- the versioned registry of the four query
  templates (`Q_any`, `Q_official`, `Q_trend`, `Q_threshold`) with their
  must-agree facets and the shared status semantics
  (robust / conditional / insufficient).
- `validation/certificates_summary.json` -- the validation summary: counts by source,
  status, and typed outcome, and the self-consistency audit.

## Validation

Run `python validate.py` (needs `jsonschema` >= 4) to re-run the checks over the
released file, including an independent rebuild of `implied_status` from each
record's rows. Run `python judge_influence.py --src <path-to-ml-result-comparability>/src`
to measure how model input changes the detailed outcome (278 of 9,471 on v1.0.0).
Expected outputs are in the scripts' docstrings.


All 9,471 certificates validate against the schema with zero failures. A
recursive search finds none of the excerpt-bearing field names (evidence_quote,
rationale, note) in any certificate. The status
reconstruction audit (`status` equals the status implied by `per_facet` plus
`normalizations_applied`) passes on 99.4% (9,412 of 9,471); the 59 divergences are
flagged by `self_consistent` and logged by kind in the summary. The certificates
are emitted deterministically by `scripts/build_certificates.py` in the dataset
repository, from the released candidate and leaderboard files.

## Licenses

The certificate data (`comparability_certificates.jsonl`) derives from the dataset
release and is CC-BY-SA 4.0, inheriting the Papers with Code terms. The schema and
registry files under `schemas/` and the validation summary are MIT. See LICENSES.md.

## Citation

Please cite the companion resource paper and the dataset release; machine-readable
metadata is in `CITATION.cff`.

> Siravuri, H. V. & Alhoori, H. (2026). Cross-Paper Result Comparability: A Dataset,
> Protocol-Partitioned Leaderboards, and a Census. The 3rd International Workshop on
> Artificial Intelligence for the Science of Science (AI4SciSci 2026), co-located with
> ACM/IEEE JCDL 2026. Accepted and presented; proceedings to appear.
