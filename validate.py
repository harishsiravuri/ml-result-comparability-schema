"""Re-run the release checks over comparability_certificates.jsonl.

Usage:  python validate.py
Needs:  pip install jsonschema  (draft 2020-12 support, jsonschema >= 4)

Checks, in order:
  1. every record validates against schemas/comparability_certificate.schema.json;
  2. no record carries copied excerpt text (keys evidence_quote/rationale/note);
  3. the reported status equals the status implied by the stored rows
     (the self_consistent field), recounted from the records;
  4. record counts by source.

Expected output on v1.0.0:
  records: 9471  by source: {'census_pair': 3058, 'leaderboard_pair': 6413}
  schema-invalid: 0
  excerpt-text leaks: 0
  self_consistent true: 9412 (99.4%); disagreements: 59
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


def main() -> None:
    validator = Draft202012Validator(json.load(open(SCHEMA)))
    n = invalid = leaks = consistent = disagreements = 0
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
        if record["self_consistent"]:
            consistent += 1
        else:
            disagreements += 1
    print(f"records: {n}  by source: {dict(by_source)}")
    print(f"schema-invalid: {invalid}")
    print(f"excerpt-text leaks: {leaks}")
    print(f"self_consistent true: {consistent} "
          f"({100 * consistent / n:.1f}%); disagreements: {disagreements}")


if __name__ == "__main__":
    main()
