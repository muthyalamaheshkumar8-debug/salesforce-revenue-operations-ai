"""Offline, streaming CSV review. Never sends records to a model or external API."""
import argparse
import csv
import hashlib
import json
import math
import sqlite3
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

RULE_VERSION = "1.0.0"
STAGES = {"Prospecting", "Engaging", "Qualification", "Needs Analysis", "Proposal",
          "Negotiation", "Closed Won", "Closed Lost"}
SCHEMAS = {
    "crm": ["opportunity_id", "account_id", "rep_id", "region", "stage", "amount",
            "created_date", "close_date"],
    "documents": ["document_id", "document_text", "category", "consent", "retention_date"],
}
# Pattern hits are candidates, not identity verification. Names/addresses need human review.
import re
PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)"),
    "ssn_like": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
}
SENSITIVE_COLUMNS = {"name", "full_name", "email", "phone", "address", "ssn",
                     "aadhaar", "pan", "rep", "contact_name", "date_of_birth"}
GUIDANCE = {
    "missing_value": "Ask the data owner to verify the missing field; do not guess a value.",
    "duplicate_id": "Compare duplicate source records privately and obtain an owner decision.",
    "invalid_value": "Verify the field against the source and rerun validation after correction.",
    "date_order": "Verify the source dates before accepting the record.",
    "pii_candidate": "Restrict access; inspect the candidate locally and redact if required.",
    "sensitive_column": "Review necessity and authorization; minimize identifiers in derived data.",
    "consent_unconfirmed": "Hold the document until its processing authorization is verified.",
    "retention_review": "Ask the responsible owner to confirm retention or approved disposal.",
    "out_of_scope": "Ask the assignment owner whether this document belongs in the review batch.",
    "empty_dataset": "Provide a non-empty review batch with the required headers.",
    "malformed_row": "Correct the source row structure and rerun the review.",
}
REASONS = {"source_verified", "correction_required", "privacy_review_required",
           "out_of_scope", "false_positive", "insufficient_evidence"}


def fingerprint(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def review(path, profile, as_of, allowed_categories=(), sample_limit=2000, sample_offset=0):
    """Counts cover the entire file; only a bounded issue sample is exported.

    Temporary SQLite keeps hashed duplicate keys off the Python heap. Storage is O(unique
    IDs); no raw identifiers are written there. Reports omit values, headers and filenames.
    """
    if profile not in SCHEMAS or not 1 <= sample_limit <= 10000 or sample_offset < 0:
        raise ValueError("Invalid review configuration")
    as_of = date.fromisoformat(as_of)
    source_sha = fingerprint(path)
    counts, samples, affected = Counter(), [], 0
    rows = 0

    def flag(row_number, code, field):
        counts[code] += 1
        if sum(counts.values()) > sample_offset and len(samples) < sample_limit:
            # IDs are tied to source/rules/row/field; no source identifier is exposed.
            issue_id = hashlib.sha256(
                f"{source_sha}:{RULE_VERSION}:{row_number}:{code}:{field}".encode()
            ).hexdigest()[:24]
            samples.append({"issue_id": issue_id, "row": row_number, "code": code,
                            "field": field, "recommendation": GUIDANCE[code]})

    with tempfile.TemporaryDirectory(prefix="privacy-qa-") as directory:
        with sqlite3.connect(str(Path(directory) / "keys.sqlite")) as keys:
            keys.execute("CREATE TABLE seen (digest TEXT PRIMARY KEY)")
            with Path(path).open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                headers = reader.fieldnames or []
                if len(set(headers)) != len(headers) or not set(SCHEMAS[profile]) <= set(headers):
                    raise ValueError("CSV must have unique headers and all profile-required fields")
                id_field = "opportunity_id" if profile == "crm" else "document_id"
                for rows, record in enumerate(reader, 1):
                    before = sum(counts.values())
                    if None in record or any(value is None for value in record.values()):
                        flag(rows, "malformed_row", "row")
                        affected += 1
                        continue
                    record = {key: value.strip() for key, value in record.items()}
                    required = [id_field, "rep_id", "region", "stage", "created_date"] if profile == "crm" else [id_field, "document_text", "category"]
                    for field in required:
                        if not record[field]:
                            flag(rows, "missing_value", field)
                    if record[id_field]:
                        digest = hashlib.sha256(record[id_field].encode()).hexdigest()
                        try:
                            keys.execute("INSERT INTO seen VALUES (?)", (digest,))
                        except sqlite3.IntegrityError:
                            flag(rows, "duplicate_id", id_field)
                    if profile == "crm":
                        if not record["account_id"]:
                            flag(rows, "missing_value", "account_id")
                        if record["stage"] not in STAGES:
                            flag(rows, "invalid_value", "stage")
                        if not record["amount"]:
                            flag(rows, "missing_value", "amount")
                        else:
                            try:
                                number = float(record["amount"])
                                if not math.isfinite(number) or number < 0:
                                    raise ValueError()
                            except ValueError:
                                flag(rows, "invalid_value", "amount")
                        parsed = {}
                        for field in ["created_date", "close_date"]:
                            value = record[field]
                            if value:
                                try:
                                    parsed[field] = date.fromisoformat(value)
                                except ValueError:
                                    flag(rows, "invalid_value", field)
                            elif field == "close_date":
                                # Open expected dates remain absent, rather than invented.
                                flag(rows, "missing_value", field)
                        if len(parsed) == 2 and parsed["close_date"] < parsed["created_date"]:
                            flag(rows, "date_order", "close_date")
                    else:
                        if record["consent"].lower() != "true":
                            flag(rows, "consent_unconfirmed", "consent")
                        try:
                            if date.fromisoformat(record["retention_date"]) < as_of:
                                flag(rows, "retention_review", "retention_date")
                        except ValueError:
                            flag(rows, "retention_review", "retention_date")
                        if allowed_categories and record["category"] not in allowed_categories:
                            flag(rows, "out_of_scope", "category")
                    for position, (field, value) in enumerate(record.items(), 1):
                        # Never echo an unknown column name; it might itself contain PII.
                        safe_field = field if field in SCHEMAS[profile] else f"column_{position}"
                        if value and field.lower() in SENSITIVE_COLUMNS:
                            flag(rows, "sensitive_column", safe_field)
                        # Date fields are validated separately; avoid treating dates as phones.
                        if value and not field.endswith("date"):
                            for pattern_name, pattern in PATTERNS.items():
                                if pattern.search(value):
                                    flag(rows, "pii_candidate", safe_field + ":" + pattern_name)
                    if sum(counts.values()) != before:
                        affected += 1
    if not rows:
        flag(0, "empty_dataset", "dataset")
    if fingerprint(path) != source_sha:
        raise ValueError("Source changed during review; rerun on a stable local copy")
    total = sum(counts.values())
    report = {
        "rule_version": RULE_VERSION, "profile": profile, "as_of": as_of.isoformat(),
        "source_sha256": source_sha, "rows_reviewed": rows, "rows_with_findings": affected,
        "issue_count": total, "counts_by_code": dict(sorted(counts.items())),
        "sample_limit": sample_limit, "sample_offset": sample_offset,
        "samples_truncated": total > len(samples),
        "scope_sha256": hashlib.sha256(json.dumps(sorted(set(allowed_categories))).encode()).hexdigest(),
        "findings": samples, "review_status": "needs_human_review",
        "training_export": "held", "external_model_called": False,
        "limitations": ["Pattern screening is incomplete and may produce false positives.",
                        "Names, addresses, context, authorization and legal compliance require human review.",
                        "Accuracy requires comparison with authorized source evidence; rules alone cannot establish truth.",
                        "Source rows are never changed. Findings require owner verification and a rerun."],
    }
    report["report_id"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return report


def validate_feedback(report, feedback):
    """Structured local feedback only; no free-text excerpts or training payloads."""
    if set(feedback) != {"report_id", "decisions"} or feedback["report_id"] != report["report_id"]:
        raise ValueError("Feedback must reference this exact report")
    known = {item["issue_id"] for item in report["findings"]}
    if not isinstance(feedback["decisions"], list):
        raise ValueError("Feedback decisions must be a list")
    seen, decisions = set(), []
    for item in feedback["decisions"]:
        if not isinstance(item, dict) or set(item) != {"issue_id", "decision", "reason"}:
            raise ValueError("Use structured issue_id, decision and reason fields only")
        if item["issue_id"] not in known or item["issue_id"] in seen:
            raise ValueError("Unknown or duplicate feedback issue")
        if item["decision"] not in {"confirmed", "false_positive", "needs_information"} or item["reason"] not in REASONS:
            raise ValueError("Unsupported decision or reason")
        if (item["decision"] == "false_positive") != (item["reason"] == "false_positive"):
            raise ValueError("False-positive decision and reason must agree")
        seen.add(item["issue_id"])
        decisions.append(item)
    return {"report_id": report["report_id"], "decisions": decisions,
            "sampled_findings_reviewed": len(seen), "sampled_findings_pending": len(known - seen),
            "unsampled_findings": report["issue_count"] - len(known),
            "training_export": "held", "reviewer_identity_verified": False,
            "notice": "Local self-attested feedback; no resolution, approval or AI training is asserted."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--profile", choices=SCHEMAS, required=True)
    parser.add_argument("--as-of", required=True, help="Explicit YYYY-MM-DD retention review date")
    parser.add_argument("--category", action="append", default=[], help="Allowed document category; repeatable")
    parser.add_argument("--sample-limit", type=int, default=2000)
    parser.add_argument("--sample-offset", type=int, default=0, help="Skip this many findings, with full-file counts retained")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--feedback", type=Path, help="Validate structured feedback against this rerun")
    args = parser.parse_args()
    try:
        if args.output.resolve() in {args.source.resolve(), args.feedback.resolve() if args.feedback else None}:
            raise ValueError("Output must not overwrite a source or feedback file")
        report = review(args.source, args.profile, args.as_of, args.category, args.sample_limit, args.sample_offset)
        if args.feedback:
            report["feedback"] = validate_feedback(report, json.loads(args.feedback.read_text(encoding="utf-8")))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive create avoids overwriting evidence. Private permissions where supported.
        import os
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(json.dumps({"rows_reviewed": report["rows_reviewed"], "issue_count": report["issue_count"],
                          "training_export": "held"}))
        return 2 if report["issue_count"] else 0
    except (OSError, ValueError, csv.Error, TypeError, KeyError):
        # Parser/provider errors can contain input. Do not print them or local filenames.
        print("Review failed. Check input format, profile, feedback and unused output path locally.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
