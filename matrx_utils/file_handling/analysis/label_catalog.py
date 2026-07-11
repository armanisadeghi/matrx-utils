"""Starter label catalog — predefined labels users can attach to bbox annotations.

Free-form labels are still allowed (the catalog is a suggestion + autocomplete
source, not a hard constraint). Categories group related labels for the FE
picker and for downstream feeds (e.g. the PD-rating calculator can ask for all
'workers_comp' + 'medical' labels in one shot).

Each entry declares:
  - id              stable identifier (used as the annotation.label value)
  - display_name    human-readable
  - category        bucket
  - description     tooltip / help
  - value_type      text | number | date | enum | code | identifier | currency
  - value_unit      optional unit hint (e.g. "%", "USD")
  - enum_options    when value_type == "enum"
  - examples        one or two examples for the FE picker UI
  - default_redact  bool — does this label *typically* indicate something to redact

Adding a label is a data change. Recipes (analysis_recipes table) can extend
the catalog per user / team without code changes.
"""

from __future__ import annotations

from typing import Any


LABEL_CATALOG: list[dict[str, Any]] = [
    # ── PII / identity ───────────────────────────────────────────────────
    {"id": "applicant_name", "display_name": "Applicant Name",
     "category": "pii", "value_type": "text", "default_redact": True,
     "description": "Full legal name of the applicant / patient.",
     "examples": ["John A. Smith", "Maria Garcia-Lopez"]},
    {"id": "applicant_first_name", "display_name": "Applicant First Name",
     "category": "pii", "value_type": "text", "default_redact": True,
     "description": "First name only.", "examples": ["John"]},
    {"id": "applicant_last_name", "display_name": "Applicant Last Name",
     "category": "pii", "value_type": "text", "default_redact": True,
     "description": "Last name only.", "examples": ["Smith"]},
    {"id": "applicant_dob", "display_name": "Date of Birth",
     "category": "pii", "value_type": "date", "default_redact": True,
     "description": "Applicant's date of birth.", "examples": ["1972-04-12", "04/12/1972"]},
    {"id": "applicant_ssn", "display_name": "Social Security Number",
     "category": "pii", "value_type": "identifier", "default_redact": True,
     "description": "Applicant SSN. Always redact unless the destination is the SSA itself."},
    {"id": "applicant_phone", "display_name": "Phone Number",
     "category": "pii", "value_type": "text", "default_redact": True},
    {"id": "applicant_email", "display_name": "Email Address",
     "category": "pii", "value_type": "text", "default_redact": True},
    {"id": "applicant_address", "display_name": "Mailing Address",
     "category": "pii", "value_type": "text", "default_redact": True},
    {"id": "applicant_employee_id", "display_name": "Employee ID",
     "category": "pii", "value_type": "identifier", "default_redact": True},

    # ── Workers' comp ────────────────────────────────────────────────────
    {"id": "claim_number", "display_name": "Claim Number",
     "category": "workers_comp", "value_type": "identifier", "default_redact": False,
     "description": "WCAB / carrier claim number.", "examples": ["ADJ12345678", "WC-2024-00123"]},
    {"id": "case_number", "display_name": "Case Number",
     "category": "workers_comp", "value_type": "identifier", "default_redact": False,
     "examples": ["ADJ12345678"]},
    {"id": "employer_name", "display_name": "Employer Name",
     "category": "workers_comp", "value_type": "text", "default_redact": False,
     "examples": ["Acme Manufacturing Inc."]},
    {"id": "insurance_carrier", "display_name": "Insurance Carrier",
     "category": "workers_comp", "value_type": "text", "default_redact": False},
    {"id": "date_of_injury", "display_name": "Date of Injury",
     "category": "workers_comp", "value_type": "date", "default_redact": False,
     "description": "DOI — single-event date or first day of a cumulative-trauma window."},
    {"id": "doi_period_start", "display_name": "DOI Period Start (CT)",
     "category": "workers_comp", "value_type": "date", "default_redact": False,
     "description": "Cumulative-trauma start date."},
    {"id": "doi_period_end", "display_name": "DOI Period End (CT)",
     "category": "workers_comp", "value_type": "date", "default_redact": False},
    {"id": "body_part", "display_name": "Body Part",
     "category": "workers_comp", "value_type": "text", "default_redact": False,
     "examples": ["lumbar spine", "right shoulder", "left knee"]},
    {"id": "mechanism_of_injury", "display_name": "Mechanism of Injury",
     "category": "workers_comp", "value_type": "text", "default_redact": False,
     "examples": ["lifting", "fall from height", "repetitive motion"]},
    {"id": "mmi_date", "display_name": "MMI Date",
     "category": "workers_comp", "value_type": "date", "default_redact": False,
     "description": "Date of Maximum Medical Improvement."},
    {"id": "p_and_s_date", "display_name": "P&S Date",
     "category": "workers_comp", "value_type": "date", "default_redact": False,
     "description": "Permanent & Stationary date."},

    # ── Medical / impairment ─────────────────────────────────────────────
    {"id": "treating_provider_name", "display_name": "Treating Provider",
     "category": "medical", "value_type": "text", "default_redact": False},
    {"id": "qme_name", "display_name": "QME Name",
     "category": "medical", "value_type": "text", "default_redact": False,
     "description": "Qualified Medical Evaluator name."},
    {"id": "ame_name", "display_name": "AME Name",
     "category": "medical", "value_type": "text", "default_redact": False,
     "description": "Agreed Medical Evaluator name."},
    {"id": "report_date", "display_name": "Report Date",
     "category": "medical", "value_type": "date", "default_redact": False},
    {"id": "diagnosis", "display_name": "Diagnosis",
     "category": "medical", "value_type": "text", "default_redact": False},
    {"id": "icd10_code", "display_name": "ICD-10 Code",
     "category": "medical", "value_type": "code", "default_redact": False,
     "examples": ["M54.5", "S83.501A"]},
    {"id": "cpt_code", "display_name": "CPT Code",
     "category": "medical", "value_type": "code", "default_redact": False,
     "examples": ["97140", "99213"]},
    {"id": "impairment_code", "display_name": "Impairment Code (AMA Guides)",
     "category": "medical", "value_type": "code", "default_redact": False,
     "description": "AMA Guides 5th Ed. table/figure reference.",
     "examples": ["15.03", "Table 15-5"]},
    {"id": "wpi_percentage", "display_name": "WPI %",
     "category": "medical", "value_type": "number", "value_unit": "%",
     "default_redact": False,
     "description": "Whole Person Impairment percentage."},
    {"id": "apportionment_pct", "display_name": "Apportionment %",
     "category": "medical", "value_type": "number", "value_unit": "%",
     "default_redact": False},
    {"id": "future_medical_recommendation", "display_name": "Future Medical Recommendation",
     "category": "medical", "value_type": "text", "default_redact": False},
    {"id": "work_restrictions", "display_name": "Work Restrictions",
     "category": "medical", "value_type": "text", "default_redact": False},
    {"id": "medication_name", "display_name": "Medication",
     "category": "medical", "value_type": "text", "default_redact": False},

    # ── Legal ────────────────────────────────────────────────────────────
    {"id": "attorney_name", "display_name": "Attorney Name",
     "category": "legal", "value_type": "text", "default_redact": False},
    {"id": "law_firm_name", "display_name": "Law Firm Name",
     "category": "legal", "value_type": "text", "default_redact": False},
    {"id": "judge_name", "display_name": "Judge Name",
     "category": "legal", "value_type": "text", "default_redact": False},
    {"id": "hearing_date", "display_name": "Hearing Date",
     "category": "legal", "value_type": "date", "default_redact": False},
    {"id": "filing_date", "display_name": "Filing Date",
     "category": "legal", "value_type": "date", "default_redact": False},

    # ── Financial ────────────────────────────────────────────────────────
    {"id": "billing_amount", "display_name": "Billing Amount",
     "category": "financial", "value_type": "currency", "value_unit": "USD",
     "default_redact": False},
    {"id": "ttd_rate", "display_name": "TTD Rate",
     "category": "financial", "value_type": "currency", "value_unit": "USD",
     "default_redact": False, "description": "Temporary Total Disability rate."},
    {"id": "average_weekly_wage", "display_name": "Average Weekly Wage",
     "category": "financial", "value_type": "currency", "value_unit": "USD",
     "default_redact": False},

    # ── Document structure (used by repeated-region / classification flows) ─
    {"id": "page_header", "display_name": "Page Header",
     "category": "structure", "value_type": "text", "default_redact": False,
     "description": "Mark a region as a repeating header so the extractor can ignore it."},
    {"id": "page_footer", "display_name": "Page Footer",
     "category": "structure", "value_type": "text", "default_redact": False},
    {"id": "watermark", "display_name": "Watermark",
     "category": "structure", "value_type": "text", "default_redact": False},
    {"id": "signature", "display_name": "Signature",
     "category": "structure", "value_type": "text", "default_redact": False},
    {"id": "table_region", "display_name": "Table",
     "category": "structure", "value_type": "text", "default_redact": False},
]


_CATEGORY_LABELS = {
    "pii":          "Personal Identifying Information",
    "workers_comp": "Workers' Compensation",
    "medical":      "Medical / Impairment",
    "legal":        "Legal",
    "financial":    "Financial",
    "structure":    "Document Structure",
    "custom":       "Custom",
}


def get_label_catalog() -> list[dict[str, Any]]:
    """Return a deep copy. Callers may mutate freely without affecting the master."""
    return [dict(entry) for entry in LABEL_CATALOG]


def get_categories() -> dict[str, str]:
    return dict(_CATEGORY_LABELS)


def get_label(label_id: str) -> dict[str, Any] | None:
    for entry in LABEL_CATALOG:
        if entry["id"] == label_id:
            return dict(entry)
    return None


def normalize_value(label_id: str, raw_text: str) -> dict[str, Any] | None:
    """Best-effort typed normalization based on the label's value_type.

    Returns a {"kind": <value_type>, "value": <typed>, "raw": <raw_text>} dict
    or None when no normalization could be applied. NEVER raises — callers can
    always fall back to raw_text.
    """
    if not raw_text:
        return None
    entry = get_label(label_id)
    if entry is None:
        return {"kind": "text", "value": raw_text.strip(), "raw": raw_text}
    vt = entry.get("value_type", "text")
    raw = raw_text.strip()

    if vt == "text" or vt == "code" or vt == "identifier":
        return {"kind": vt, "value": raw, "raw": raw_text}
    if vt == "number":
        # Strip common units / punctuation and parse.
        import re
        m = re.search(r"-?\d+(?:[.,]\d+)?", raw)
        if not m:
            return {"kind": "number", "value": None, "raw": raw_text}
        try:
            return {"kind": "number", "value": float(m.group(0).replace(",", ".")), "raw": raw_text}
        except ValueError:
            return {"kind": "number", "value": None, "raw": raw_text}
    if vt == "currency":
        import re
        m = re.search(r"-?[\d,]+(?:\.\d+)?", raw)
        if not m:
            return {"kind": "currency", "value": None, "raw": raw_text}
        try:
            return {
                "kind": "currency",
                "value": float(m.group(0).replace(",", "")),
                "unit": entry.get("value_unit", "USD"),
                "raw": raw_text,
            }
        except ValueError:
            return {"kind": "currency", "value": None, "raw": raw_text}
    if vt == "date":
        # Pass the raw — value normalization belongs at consumption time
        # (dateutil etc.) so we don't take a hard dep here.
        return {"kind": "date", "value": raw, "raw": raw_text}
    if vt == "enum":
        opts = entry.get("enum_options") or []
        norm = raw.lower()
        match = next((o for o in opts if o.lower() == norm), None)
        return {"kind": "enum", "value": match, "raw": raw_text, "options": opts}
    return {"kind": "text", "value": raw, "raw": raw_text}


__all__ = [
    "LABEL_CATALOG",
    "get_label_catalog",
    "get_categories",
    "get_label",
    "normalize_value",
]
