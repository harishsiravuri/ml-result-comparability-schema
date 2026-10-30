"""Re-run the release checks over comparability_certificates.jsonl.

Usage:  python validate.py
Needs:  pip install jsonschema  (draft 2020-12 support, jsonschema >= 4)

Checks, in order:
  1. every record validates against schemas/comparability_certificate.schema.json;
  2. no record carries the three excerpt-bearing field names
     (evidence_quote, rationale, note), searched recursively; the format stores
     source references, not excerpt text;
  3. status reconstruction, computed INDEPENDENTLY here: implied_status is
     rebuilt from each record's per_facet rows, normalizations_applied, and
     judge_cause (the logic mirrors the builder in the dataset repository,
     src/certificates/certificate.py), then compared with the stored
     implied_status, the stored status, and the stored self_consistent flag;
  4. record counts by source.

Expected output on v1.0.0:
  records: 9471  by source: {'census_pair': 3058, 'leaderboard_pair': 6413}
  schema-invalid: 0
  excerpt-bearing fields found: 0
  rebuilt implied_status differs from stored: 0
  stored self_consistent flag inconsistent with the two statuses: 0
  status == implied_status: 9412 (99.4%); reconstruction disagreements: 59
"""

from __future__ import annotations

import json
from collections import Counter

from jsonschema import Draft202012Validator

CERTS = "comparability_certificates.jsonl"
SCHEMA = "schemas/comparability_certificate.schema.json"
TEXT_KEYS = {"evidence_quote", "rationale", "note"}


def keys_of(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from keys_of(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from keys_of(v)


def rebuild_implied(rows, normalizations, judge_cause):
    """Rebuild implied_status from the stored rows.

    Mirrors the builder: an extraction-artifact cause maps to excluded;
    otherwise any un-normalized recorded-and-different row is incompatible;
    otherwise, if every extracted row is recorded-and-same or normalized,
    comparable; otherwise unknown.
    """
    if judge_cause == "extraction_artifact":
        return "excluded"
    normalized = {n["facet"] for n in normalizations}
    if any(r["relation"] == "observed-different" and r["facet"] not in normalized
           for r in rows):
        return "incompatible"
    extracted = [r for r in rows if r["source"] == "extracted"]
    if extracted and all(r["relation"] == "observed-same" or r["facet"] in normalized
                         for r in extracted):
        return "comparable"
    return "unknown"


def main() -> None:
    validator = Draft202012Validator(json.load(open(SCHEMA)))
    n = invalid = leaks = rebuilt_bad = flag_bad = agree = disagree = 0
    by_source: Counter = Counter()
    for line in open(CERTS):
        if not line.strip():
            continue
        n += 1
        record = json.loads(line)
        by_source[record.get("source")] += 1
        if any(True for _ in validator.iter_errors(record)):
            invalid += 1
        if TEXT_KEYS & set(keys_of(record)):
            leaks += 1
        rebuilt = rebuild_implied(record["per_facet"],
                                  record["normalizations_applied"],
                                  record["judge_cause"])
        if rebuilt != record["implied_status"]:
            rebuilt_bad += 1
        same = record["status"] == record["implied_status"]
        if record["self_consistent"] != same:
            flag_bad += 1
        if same:
            agree += 1
        else:
            disagree += 1
    print(f"records: {n}  by source: {dict(by_source)}")
    print(f"schema-invalid: {invalid}")
    print(f"excerpt-bearing fields found: {leaks}")
    print(f"rebuilt implied_status differs from stored: {rebuilt_bad}")
    print(f"stored self_consistent flag inconsistent with the two statuses: {flag_bad}")
    print(f"status == implied_status: {agree} "
          f"({100 * agree / n:.1f}%); reconstruction disagreements: {disagree}")


if __name__ == "__main__":
    main()
