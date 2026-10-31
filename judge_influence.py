"""Measure how model input changes the detailed outcome (typed_outcome).

Usage:  python judge_influence.py [--src PATH]
        PATH is the src/ directory of a clone of
        github.com/harishsiravuri/ml-result-comparability (default:
        ../ml-result-comparability/src). The detailed-outcome rules are
        imported from that clone, not duplicated here. The v1.0.0 data
        release contains no src/ directory: use the repository's main
        branch at commit 7e8da59 or later (the rule files are unchanged
        since they were first packaged, commit cc50a55).

Procedure, per released determination:
  1. Sanity: recompute the detailed outcome from ALL stored rows plus the
     judge cause, with the missing-condition list derived from the extracted
     rows minus the asserted conditions (the builder's definition), keeping
     the stored conversions. This must reproduce the released typed_outcome.
  2. Extracted-only: recompute from the extracted rows only, with no judge
     cause, the missing-condition list derived from the extracted rows, and
     the same stored conversions.
  3. Count the determinations where step 2 differs from the released value,
     split into excluded outcomes (the extraction-artifact cause) and changes
     from asserted condition rows.

Expected output on v1.0.0:
  records: 9471  sanity mismatches: 0
  detailed outcome changed after removing model input: 278
    changes with the excluded outcome: 106
    changes from asserted condition rows: 172
"""

from __future__ import annotations

import argparse
import json
import sys

CERTS = "comparability_certificates.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="../ml-result-comparability/src")
    args = parser.parse_args()
    sys.path.insert(0, args.src)
    from certificates.typed_outcomes import (  # noqa: E402
        missing_dimensions_for,
        typed_outcome,
    )

    n = sanity_bad = changed = excluded = asserted = 0
    for line in open(CERTS):
        if not line.strip():
            continue
        n += 1
        c = json.loads(line)
        rows = c["per_facet"]
        norms = c["normalizations_applied"]
        cause = c["judge_cause"]
        extracted = [r for r in rows if r["source"] == "extracted"]
        asserted_facets = {r["facet"] for r in rows
                           if r["source"] == "asserted_by_judge"}
        missing_all = [d for d in missing_dimensions_for(extracted)
                       if d not in asserted_facets]
        t_all = typed_outcome(rows, norms, missing_all, cause)["typed_outcome"]
        if t_all != c["typed_outcome"]:
            sanity_bad += 1
        t_ex = typed_outcome(extracted, norms,
                             missing_dimensions_for(extracted),
                             None)["typed_outcome"]
        if t_ex != c["typed_outcome"]:
            changed += 1
            if c["typed_outcome"] == "excluded_not_a_genuine_pair":
                excluded += 1
            else:
                asserted += 1
    print(f"records: {n}  sanity mismatches: {sanity_bad}")
    print(f"detailed outcome changed after removing model input: {changed}")
    print(f"  changes with the excluded outcome: {excluded}")
    print(f"  changes from asserted condition rows: {asserted}")


if __name__ == "__main__":
    main()
