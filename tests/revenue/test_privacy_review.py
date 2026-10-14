import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("privacy_review", ROOT / "python/privacy_review.py")
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


class PrivacyReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "input.csv"

    def write(self, rows, fields=None):
        with self.path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields or qa.SCHEMAS["documents"])
            writer.writeheader()
            writer.writerows(rows)

    def document(self, **kwargs):
        return {"document_id": "D1", "document_text": "Synthetic invoice, ten units.",
                "category": "invoice", "consent": "true", "retention_date": "2030-01-01", **kwargs}

    def run_review(self, **kwargs):
        return qa.review(self.path, "documents", "2026-10-14", ["invoice"], **kwargs)

    def test_clean_batch_still_requires_human_review(self):
        self.write([self.document()])
        report = self.run_review()
        self.assertEqual(report["issue_count"], 0)
        self.assertEqual(report["training_export"], "held")

    def test_report_has_no_source_values_or_unknown_headers(self):
        self.write([self.document(document_id="SECRET-CUSTOMER", document_text="person@example.invalid +1 (202) 555-0199", **{"secret@example.invalid": "hidden"})], qa.SCHEMAS["documents"] + ["secret@example.invalid"])
        report = self.run_review()
        rendered = json.dumps(report)
        for secret in ["SECRET-CUSTOMER", "person@example.invalid", "secret@example.invalid", "555-0199"]:
            self.assertNotIn(secret, rendered)
        self.assertEqual(report["counts_by_code"]["pii_candidate"], 2)

    def test_document_privacy_completeness_and_relevance(self):
        self.write([self.document(document_text="", consent="false", retention_date="2020-01-01", category="other")])
        report = self.run_review()
        for code in ["missing_value", "consent_unconfirmed", "retention_review", "out_of_scope"]:
            self.assertEqual(report["counts_by_code"][code], 1)

    def test_duplicate_identifiers_are_flagged(self):
        self.write([self.document(), self.document()])
        self.assertEqual(self.run_review()["counts_by_code"]["duplicate_id"], 1)

    def test_counts_continue_past_sample_limit(self):
        self.write([self.document(document_id=str(i), consent="false") for i in range(5000)])
        report = self.run_review(sample_limit=3)
        self.assertEqual(report["rows_reviewed"], 5000)
        self.assertEqual(report["rows_with_findings"], 5000)
        self.assertEqual(report["issue_count"], 5000)
        self.assertEqual(len(report["findings"]), 3)
        self.assertTrue(report["samples_truncated"])

    def test_invalid_dates_and_numbers_in_crm(self):
        row = dict(zip(qa.SCHEMAS["crm"], ["O1", "A1", "R1", "East", "Closed Won", "NaN", "2017-02-01", "2017-01-01"]))
        self.write([row], qa.SCHEMAS["crm"])
        report = qa.review(self.path, "crm", "2026-10-14")
        self.assertEqual(report["counts_by_code"]["invalid_value"], 1)
        self.assertEqual(report["counts_by_code"]["date_order"], 1)

    def test_all_findings_can_be_paged_without_losing_counts(self):
        self.write([self.document(document_id=str(i), consent="false") for i in range(7)])
        pages = [self.run_review(sample_limit=3, sample_offset=i) for i in [0, 3, 6]]
        self.assertTrue(all(page["issue_count"] == 7 for page in pages))
        self.assertEqual([item["row"] for page in pages for item in page["findings"]], list(range(1, 8)))

    def test_missing_headers_duplicate_headers_and_empty_rows(self):
        for text in ["document_id\nD1\n", "document_id,document_id\nD1,D2\n"]:
            self.path.write_text(text)
            with self.assertRaises(ValueError):
                self.run_review()
        self.write([])
        self.assertEqual(self.run_review()["counts_by_code"]["empty_dataset"], 1)

    def test_malformed_row_is_flagged(self):
        self.path.write_text(",".join(qa.SCHEMAS["documents"]) + "\nD1,short\n")
        self.assertEqual(self.run_review()["counts_by_code"]["malformed_row"], 1)

    def test_feedback_is_report_bound_and_does_not_release_training(self):
        self.write([self.document(consent="false")])
        report = self.run_review()
        decision = {"issue_id": report["findings"][0]["issue_id"], "decision": "confirmed", "reason": "privacy_review_required"}
        payload = {"report_id": report["report_id"], "decisions": [decision]}
        result = qa.validate_feedback(report, payload)
        self.assertEqual(result["sampled_findings_pending"], 0)
        self.assertEqual(result["training_export"], "held")
        for bad in [{**payload, "report_id": "stale"}, {**payload, "decisions": [decision, decision]},
                    {**payload, "decisions": [{**decision, "notes": "private text"}]},
                    {**payload, "decisions": [{**decision, "issue_id": "unknown"}]}]:
            with self.assertRaises(ValueError):
                qa.validate_feedback(report, bad)

    def test_reports_are_deterministic_and_source_bound(self):
        self.write([self.document()])
        first = self.run_review()
        self.assertEqual(first["report_id"], self.run_review()["report_id"])
        self.write([self.document(consent="false")])
        self.assertNotEqual(first["report_id"], self.run_review()["report_id"])

    def test_cli_exit_codes_and_source_overwrite_guard(self):
        self.write([self.document(consent="false")])
        base = [sys.executable, str(ROOT / "python/privacy_review.py"), str(self.path), "--profile", "documents", "--as-of", "2026-10-14", "--output"]
        result = subprocess.run(base + [str(Path(self.temp.name) / "report.json")], capture_output=True)
        self.assertEqual(result.returncode, 2)
        original = self.path.read_bytes()
        self.assertEqual(subprocess.run(base + [str(self.path)], capture_output=True).returncode, 1)
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual(subprocess.run(base + [str(Path(self.temp.name) / "report.json")], capture_output=True).returncode, 1)


if __name__ == "__main__":
    unittest.main()
