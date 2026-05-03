"""Process verifier for 10-K reasoning.

The model's response is structured as a chain of steps. Each step type has its
own sub-verifier. The total reward is a weighted sum, with the weighting tunable
to support curriculum-style training (early: extraction-heavy; late:
final-answer-heavy).

Step types
----------
extract     Pull a specific figure from the source. Format: ``EXTRACT <key> = <value>``.
compute     Apply arithmetic on already-extracted keys. Format: ``COMPUTE <expr>``.
cite        Attach a source pointer to a previously-asserted value.
            Format: ``CITE <key> -> <source_id>``.
conclude    Final natural-language answer. Format: ``CONCLUDE: <text>``.

This is intentionally a small, parseable mini-language. Real systems use richer
formats (JSON, XML), but the verification logic is the same.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

# A "filing" is a flat dict of normalized facts the model is allowed to extract.
Filing = dict[str, float]
Sources = dict[str, str]  # key -> source identifier (table id, paragraph #, etc.)


@dataclass(frozen=True)
class Question:
    text: str
    filing: Filing
    sources: Sources
    expected_answer_keywords: tuple[str, ...]


@dataclass
class StepResult:
    kind: str
    raw: str
    ok: bool
    note: str = ""


@dataclass
class VerifierResult:
    extraction: float
    calculation: float
    citation: float
    final: float
    reward: float
    steps: list[StepResult] = field(default_factory=list)


_EXTRACT_RE = re.compile(r"^EXTRACT\s+(?P<key>[\w_]+)\s*=\s*(?P<val>-?\d+(?:\.\d+)?)\s*$")
_COMPUTE_RE = re.compile(r"^COMPUTE\s+(?P<lhs>[\w_]+)\s*=\s*(?P<expr>.+)$")
_CITE_RE = re.compile(r"^CITE\s+(?P<key>[\w_]+)\s*->\s*(?P<src>\S+)\s*$")
_CONCLUDE_RE = re.compile(r"^CONCLUDE\s*:\s*(?P<text>.+)$", re.DOTALL)

_SAFE_EVAL_RE = re.compile(r"^[\d\.\+\-\*\/\(\)\sA-Za-z_]+$")


def _safe_eval(expr: str, env: dict[str, float]) -> float | None:
    if not _SAFE_EVAL_RE.match(expr):
        return None
    try:
        return float(eval(expr, {"__builtins__": {}}, env))  # noqa: S307
    except Exception:
        return None


def verifier(
    question: Question,
    completion: str,
    *,
    weights: tuple[float, float, float, float] = (0.25, 0.25, 0.20, 0.30),
) -> VerifierResult:
    """Score a chain-of-thought completion against the four sub-verifiers."""
    lines = [ln.strip() for ln in completion.strip().splitlines() if ln.strip()]

    extracted: dict[str, float] = {}
    cited: set[str] = set()
    computed: dict[str, float] = {}

    extraction_attempts = 0
    extraction_hits = 0
    calc_attempts = 0
    calc_hits = 0
    cite_attempts = 0
    cite_hits = 0
    final_text: str | None = None

    steps: list[StepResult] = []

    for line in lines:
        if m := _EXTRACT_RE.match(line):
            extraction_attempts += 1
            key = m["key"]
            val = float(m["val"])
            truth = question.filing.get(key)
            if truth is not None and abs(val - truth) <= max(0.005 * abs(truth), 0.01):
                extraction_hits += 1
                extracted[key] = val
                steps.append(StepResult("extract", line, True))
            else:
                steps.append(StepResult(
                    "extract", line, False,
                    note=f"truth = {truth}" if truth is not None else "key not in filing",
                ))
            continue

        if m := _COMPUTE_RE.match(line):
            calc_attempts += 1
            lhs = m["lhs"]
            env = {**extracted, **computed}
            value = _safe_eval(m["expr"], env)
            if value is not None:
                calc_hits += 1
                computed[lhs] = value
                steps.append(StepResult("compute", line, True, note=f"= {value:.4f}"))
            else:
                steps.append(StepResult("compute", line, False,
                                        note="references missing key or invalid expr"))
            continue

        if m := _CITE_RE.match(line):
            cite_attempts += 1
            key = m["key"]
            src = m["src"]
            if key in extracted and question.sources.get(key) == src:
                cite_hits += 1
                cited.add(key)
                steps.append(StepResult("cite", line, True))
            else:
                steps.append(StepResult(
                    "cite", line, False,
                    note=f"expected source {question.sources.get(key, '?')}",
                ))
            continue

        if m := _CONCLUDE_RE.match(line):
            final_text = m["text"].strip()
            steps.append(StepResult("conclude", line, True))
            continue

        steps.append(StepResult("unknown", line, False, note="unparsed line"))

    extraction = extraction_hits / max(extraction_attempts, 1) if extraction_attempts else 0.0
    calculation = calc_hits / max(calc_attempts, 1) if calc_attempts else 0.0
    citation = cite_hits / max(cite_attempts, 1) if cite_attempts else 0.0

    if final_text is None:
        final = 0.0
    else:
        ft = final_text.lower()
        present = sum(1 for kw in question.expected_answer_keywords if kw.lower() in ft)
        final = present / max(len(question.expected_answer_keywords), 1)

    w_e, w_c, w_ci, w_f = weights
    total_w = w_e + w_c + w_ci + w_f
    reward = (w_e * extraction + w_c * calculation + w_ci * citation + w_f * final) / total_w

    return VerifierResult(
        extraction=extraction,
        calculation=calculation,
        citation=citation,
        final=final,
        reward=reward,
        steps=steps,
    )
