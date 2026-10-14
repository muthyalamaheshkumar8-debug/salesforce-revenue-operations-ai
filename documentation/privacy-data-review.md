# Privacy-aware business data and document QA

Portfolio implementation by **Muthyala Mahesh Kumar**. Required skills: **PII, Data Privacy, Document Review, Data Analysis, Quality Assurance**.

This extension adds an offline Python CSV reviewer to the existing revenue analytics project. The CRM analysis uses the bundled historical, fictional Maven sample. Document-review examples are explicitly synthetic. No real sensitive documents, customer records, model submissions or employer results are claimed.

## Run the review

Requires Python 3.10+ and the standard library; no API keys or extra packages.

```bash
python python/privacy_review.py data/cleaned/opportunities.csv --profile crm --as-of 2026-10-14 --output data/private/crm-review.json
python python/privacy_review.py data/examples/privacy_review/documents.csv --profile documents --category invoice --as-of 2026-10-14 --output data/private/documents-review.json
python -m unittest discover -s tests/revenue -p 'test_privacy_review.py' -v
```

Use the current review date for your own batch. The historical CRM dates remain historical. Output must be a new file: existing evidence is never overwritten. Exit code **0** means no automated findings, **2** means findings need review, and **1** means input/configuration/output failure. Even code 0 does not approve a record for AI training.

The reviewer streams CSV rows. It uses a temporary on-disk SQLite index of SHA-256 identifier digests for duplicate detection, then removes that temporary directory. Python memory holds only the issue sample and current row, although the temporary index grows with unique IDs and individual fields remain bounded by Python's CSV field-size limit. Source fingerprints use chunked reads and are rechecked to detect source changes during a run. This is a batch CLI, not a distributed production platform or a claim of enterprise-scale experience.

Default output includes the first 2,000 findings. **Counts always cover the entire file.** Use `--sample-offset 2000`, then `4000`, etc., with new output paths to inspect successive pages. `--sample-limit` accepts 1–10,000. Keep source, profile, category scope, rule version and date fixed between pages. The report includes source/rule fingerprints, row numbers, issue codes and recommendations. Counts are findings, not distinct affected records; `rows_with_findings` counts affected rows separately. Later duplicate occurrences are flagged; compare all occurrences privately before deciding which record to retain.

## Checks and boundaries

| Requirement | Implemented evidence | Human verification still needed |
| --- | --- | --- |
| Business data accuracy and completeness | Required fields, duplicate IDs, finite/nonnegative amounts, allowed stages, valid dates and date order | Compare source evidence, relationships and business meaning; plausible values can still be wrong |
| Document review and relevance | Required text/category, explicit allowed category list, authorization marker and retention date review | Read the authorized document and check its content and assignment purpose; category checks are metadata rules |
| PII and sensitive data | Email, phone and SSN-like pattern candidates; presence flags for explicitly named identifier columns | Names, addresses, indirect identifiers, sensitive context and missed or falsely flagged patterns |
| Data privacy | Offline processing, no model/API calls, reports omit raw values, IDs, text, filenames and unknown header names | Authorized access, collection purpose, environment security and applicable policy review |
| QA findings and resolution | Reproducible codes, recommendations, source/row traceability and rerun verification | Data owner confirms the correct source value; corrections occur in a separate controlled working copy |
| AI training feedback | Report-bound structured decisions; training export remains held | Authorized downstream approval and any training-data governance process are external |
| QA standards | Versioned rules, acceptance criteria and automated regression cases | Standards changes need assignment-owner review and a documented rationale |
| Stakeholder communication | Local status-update template and structured feedback records | Real stakeholder collaboration and remote delivery experience are not established by a template |

Missing open opportunity amounts/dates are known source gaps, rather than proven mistakes. The fictional CRM `rep` column contains names, so every populated `rep` generates a sensitive-column review flag. That shows field minimization needs; it does not establish an actual privacy violation. A pattern match is a candidate, never a verified identity. The code does not redact source documents or claim complete PII removal.

Report fingerprints and row positions enable linkage to a restricted source and should also be access controlled. Hashes are not encryption or a guarantee of anonymity. The `data/private/` directory is Git-ignored; it is still ordinary local storage, not a secure vault. Use authorized local copies, an appropriately protected device/workspace and approved retention procedures. No regulatory compliance certification is asserted.

## Review, correction and feedback procedure

1. Confirm the assignment scope and permission to process its records. Use synthetic examples for public demonstrations.
2. Run the appropriate profile. Review total counts and all finding pages before declaring review coverage complete.
3. Use the report row number to locate the record inside the restricted source. Never paste its raw contents into public issues, reports or model prompts.
4. Verify suspected issues with authorized source evidence. Classify each as `confirmed`, `false_positive` or `needs_information`. Never infer a missing financial value or authorization from context.
5. Ask the data owner to correct confirmed errors in a new controlled copy; retain original evidence according to the assignment's policy. Rerun and compare new counts/source fingerprints. This tool does not alter records or mark errors resolved automatically.
6. Provide aggregate findings and recommended actions. Keep unresolved PII, authorization, retention and accuracy questions open. The tool never exports documents to a model or releases a training dataset.
7. Review recurring false positives or missed cases before changing standards. Add a regression fixture, document the reason, increment `RULE_VERSION`, and rerun checks; retain both versions of the review evidence.

To record feedback, create a local JSON file with the exact report ID and an issue ID from that report. The placeholders below must be replaced locally:

```json
{
  "report_id": "COPY_REPORT_ID",
  "decisions": [
    {
      "issue_id": "COPY_ISSUE_ID",
      "decision": "needs_information",
      "reason": "insufficient_evidence"
    }
  ]
}
```

Allowed reasons: `source_verified`, `correction_required`, `privacy_review_required`, `out_of_scope`, `false_positive`, `insufficient_evidence`. A false-positive decision must use the matching reason. Free text, unknown fields, duplicate/unknown issues and feedback for another report are rejected. This reduces accidental disclosure through reviewer notes. The reasons are reviewer assertions, not proof of a correction. Reviewer identity is **not authenticated** by this CLI.

Rerun with the same configuration and `--feedback data/private/feedback.json --output data/private/review-with-feedback.json`. The output lists reviewed, pending sampled and unsampled finding counts; training export stays held regardless of decisions. The category list and sample page form part of report identity. Retain feedback separately because this CLI does not implement a multiuser case database or immutable audit ledger.

## Stakeholder update template

> Reviewed [row count] records in an authorized batch using rules [version]. Found [count] findings affecting [row count] records. Main categories: [aggregate codes/counts]. Source accuracy and possible PII require the owner's review. Recommended next steps: confirm missing fields, validate flagged candidates locally, correct verified errors in a controlled copy, and rerun checks. Training export remains held. Owner: [assigned role]; next review: [agreed date]. No source PII is included in this update.

## Verification

The delivered review was run on all **8,800** bundled CRM rows and all **5** synthetic document rows. Exact deterministic counters can be regenerated with the commands above. The tests cover value-free output, duplicates, missing/invalid fields, malformed/empty CSVs, privacy/relevance flags, 5,000-row bounded sampling, pagination, report-bound feedback, reproducibility and source overwrite prevention. This verifies implemented behavior on these cases, not legal compliance, complete detection or production throughput.

CRM findings: **6,103** missing-field flags (1,425 missing accounts, 2,089 missing amounts, 2,089 missing close dates and 500 missing creation dates) and **8,800** sensitive-column flags for the fictional representative names. The document fixture produces **7** findings: two PII pattern candidates and one each for unconfirmed authorization, retention review, missing text, duplicate ID and out-of-scope category. The [committed synthetic example report](../data/examples/privacy_review/review-example.json) shows the actual report format without source values. No production throughput benchmark was performed.

Verification on 2026-10-14: **28 Python tests** (including 12 new reviewer tests) and **13 JavaScript tests** passed. Full Python regression checks used an isolated environment with FastAPI 0.143.1, HTTPX 0.28.1, LangChain Core 1.6.10 and LangChain OpenAI 1.7.2. The existing dependency lockfile was not changed. This CLI itself uses only the standard library. The synthetic feedback path was also exercised through the command line; output remained held for training.

## Interview introduction

“I am Muthyala Mahesh Kumar, a Computer Science and Engineering graduate. My Salesforce Revenue Operations AI portfolio project analyzes 8,800 fictional CRM opportunities using Python, SQL and a reporting dashboard. I added an offline review tool for missing fields, duplicate records, invalid values, document-review checks and possible PII. Its reports omit source values and provide traceable findings and recommendations. I also built CampusGuard to demonstrate role-based access, encrypted storage, masked emails and privacy review. These projects demonstrate my approach to data analysis, document review and quality assurance. I verify findings against evidence and keep unresolved issues visible for human review.”

## Resume project wording

**Privacy-aware Business Data & Document QA — Python, SQL, Data Analysis, PII Screening**

- Extended a portfolio CRM analytics project with streaming CSV review, duplicate detection, required-field checks, value/date validation and privacy-safe issue reports; exercised the review on 8,800 fictional business records.
- Implemented synthetic document-review examples covering completeness, category scope, authorization/retention flags and email/phone/SSN-like candidate screening.
- Added versioned QA rules, regression tests, structured review feedback and a documented source-verification/correction procedure; held all training exports for external human approval.

Describe this as project work. It does not establish professional PII-handling experience, regulatory expertise, production deployment of this reviewer, or stakeholder/remote-work history.
