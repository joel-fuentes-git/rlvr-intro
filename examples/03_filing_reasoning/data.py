"""Cached question, sample completions, and source data for filing reasoning."""

from __future__ import annotations

# Apple FY2022 / FY2023 / FY2024 services and products revenue (illustrative,
# rounded — not authoritative).
APPLE_FILING = {
    "services_rev_2022": 78.13,
    "services_rev_2023": 85.20,
    "services_rev_2024": 96.17,
    "products_rev_2022": 316.20,
    "products_rev_2023": 298.10,
    "products_rev_2024": 294.85,
}

APPLE_SOURCES = {
    "services_rev_2022": "10K-2022-Tbl3",
    "services_rev_2023": "10K-2023-Tbl3",
    "services_rev_2024": "10K-2024-Tbl3",
    "products_rev_2022": "10K-2022-Tbl3",
    "products_rev_2023": "10K-2023-Tbl3",
    "products_rev_2024": "10K-2024-Tbl3",
}

QUESTION_TEXT = (
    "Apple's services revenue grew at what rate from FY2022 to FY2024, "
    "and how does that compare to its product revenue growth over the same period? "
    "Cite the relevant figures."
)

EXPECTED_KEYWORDS = ("services", "23", "products", "decline", "outpaced")

# A model that produces fluent prose but doesn't follow the chain protocol —
# the outcome verifier might be lenient, but the process verifier is harsh.
COMPLETION_PROSE = (
    "CONCLUDE: Apple's services business has clearly outpaced its products "
    "segment, with services growing strongly while product revenue has declined. "
    "This shift toward higher-margin services is a structural positive."
)

# A model trained against the process verifier: every claim has a step.
COMPLETION_GROUNDED = """\
EXTRACT services_rev_2022 = 78.13
EXTRACT services_rev_2024 = 96.17
EXTRACT products_rev_2022 = 316.20
EXTRACT products_rev_2024 = 294.85
COMPUTE services_growth = (services_rev_2024 - services_rev_2022) / services_rev_2022
COMPUTE products_growth = (products_rev_2024 - products_rev_2022) / products_rev_2022
CITE services_rev_2022 -> 10K-2022-Tbl3
CITE services_rev_2024 -> 10K-2024-Tbl3
CITE products_rev_2022 -> 10K-2022-Tbl3
CITE products_rev_2024 -> 10K-2024-Tbl3
CONCLUDE: Apple's services revenue grew about 23% from FY2022 to FY2024, while products revenue saw a decline of about 7%. Services growth meaningfully outpaced products."""

# A model that hacks the format but lies about the numbers — the extraction
# verifier catches it.
COMPLETION_HACKED = """\
EXTRACT services_rev_2022 = 60.00
EXTRACT services_rev_2024 = 120.00
EXTRACT products_rev_2022 = 320.00
EXTRACT products_rev_2024 = 240.00
COMPUTE services_growth = (services_rev_2024 - services_rev_2022) / services_rev_2022
COMPUTE products_growth = (products_rev_2024 - products_rev_2022) / products_rev_2022
CONCLUDE: Services doubled while products declined 25%. Services has outpaced products."""
