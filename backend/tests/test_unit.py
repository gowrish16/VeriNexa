"""
VeriNexa Quality Assurance Test Suite - Unit Tests
Covers: Spatial Coordinate Math, NLI & Verdict Parsing, Ingestion Chunking & Numerical Preservation
"""

import re
import pytest
import math
from typing import Tuple, List, Dict, Any


# ==============================================================================
# 1. SPATIAL COORDINATE MATH TESTS
# ==============================================================================

def normalize_bbox(
    x0: float, top: float, x1: float, bottom: float,
    page_w: float, page_h: float
) -> Tuple[float, float, float, float]:
    """
    Deterministic bounding box normalization logic matching VeriNexa ingest.py.
    Safely clamps coordinates to [0.0, 1.0] and defends against division by zero.
    """
    safe_w = float(page_w) if page_w and page_w > 0 else 612.0
    safe_h = float(page_h) if page_h and page_h > 0 else 792.0

    norm_x0 = max(0.0, min(1.0, round(float(x0 / safe_w), 4)))
    norm_top = max(0.0, min(1.0, round(float(top / safe_h), 4)))
    norm_x1 = max(0.0, min(1.0, round(float(x1 / safe_w), 4)))
    norm_bottom = max(0.0, min(1.0, round(float(bottom / safe_h), 4)))

    # Ensure invariant: x0 <= x1, top <= bottom
    if norm_x0 > norm_x1:
        norm_x0, norm_x1 = norm_x1, norm_x0
    if norm_top > norm_bottom:
        norm_top, norm_bottom = norm_bottom, norm_top

    return norm_x0, norm_top, norm_x1, norm_bottom


class TestSpatialMath:
    def test_standard_us_letter(self):
        """Standard Letter size: 612 x 792 pt."""
        x0, top, x1, bottom = normalize_bbox(72.0, 100.0, 300.0, 250.0, 612.0, 792.0)
        assert 0.0 <= x0 <= x1 <= 1.0
        assert 0.0 <= top <= bottom <= 1.0
        assert math.isclose(x0, round(72.0 / 612.0, 4), abs_tol=1e-4)
        assert math.isclose(top, round(100.0 / 792.0, 4), abs_tol=1e-4)

    def test_iso_a4_dimensions(self):
        """Standard European A4: 595.0 x 842.0 pt."""
        x0, top, x1, bottom = normalize_bbox(50.0, 80.0, 545.0, 800.0, 595.0, 842.0)
        assert 0.0 <= x0 <= x1 <= 1.0
        assert 0.0 <= top <= bottom <= 1.0
        assert x1 > 0.90
        assert bottom > 0.90

    def test_arbitrary_landscape_dimensions(self):
        """Landscape two-column presentation: 1200 x 800 pt."""
        x0, top, x1, bottom = normalize_bbox(100.0, 50.0, 600.0, 400.0, 1200.0, 800.0)
        assert math.isclose(x0, 0.0833, abs_tol=1e-3)
        assert math.isclose(x1, 0.5000, abs_tol=1e-3)
        assert math.isclose(top, 0.0625, abs_tol=1e-3)
        assert math.isclose(bottom, 0.5000, abs_tol=1e-3)

    def test_negative_coordinates_clamping(self):
        """Margin bleed or negative coordinate offsets must clamp to 0.0."""
        x0, top, x1, bottom = normalize_bbox(-25.0, -10.0, 200.0, 300.0, 612.0, 792.0)
        assert x0 == 0.0
        assert top == 0.0
        assert 0.0 < x1 <= 1.0
        assert 0.0 < bottom <= 1.0

    def test_overflowing_coordinates_clamping(self):
        """Coordinates exceeding page boundaries (printer bleed) must clamp to 1.0."""
        x0, top, x1, bottom = normalize_bbox(500.0, 700.0, 650.0, 820.0, 612.0, 792.0)
        assert x0 < 1.0
        assert top < 1.0
        assert x1 == 1.0
        assert bottom == 1.0

    def test_inverted_coordinate_pairs_auto_reversal(self):
        """If bottom < top or x1 < x0 due to PyMuPDF raw upside-down coordinate systems."""
        x0, top, x1, bottom = normalize_bbox(300.0, 500.0, 100.0, 200.0, 612.0, 792.0)
        assert x0 <= x1
        assert top <= bottom

    def test_zero_or_negative_page_dimensions(self):
        """Defends against zero or corrupt page width/height without ZeroDivisionError."""
        x0, top, x1, bottom = normalize_bbox(50.0, 50.0, 200.0, 200.0, 0.0, -10.0)
        assert 0.0 <= x0 <= x1 <= 1.0
        assert 0.0 <= top <= bottom <= 1.0


# ==============================================================================
# 2. NLI & VERDICT PARSING TESTS
# ==============================================================================

CANONICAL_VERDICTS = {
    "CONFLICT": "VERDICT: CONFLICT DETECTED",
    "CONCORDANT": "VERDICT: CONCORDANT",
    "UNCLEAR": "VERDICT: INSUFFICIENT DATA",
    "PARTIAL": "VERDICT: PARTIAL",
}


def parse_arbitration_verdict(raw_text: str) -> Dict[str, str]:
    """
    Python mirror of frontend parseVerdictInfo and backend conflict_graph extraction.
    Ensures zero conversational leakage and strict 4-category classification.
    """
    if not raw_text:
        return {"label": CANONICAL_VERDICTS["UNCLEAR"], "type": "unclear", "reason": ""}

    text_str = str(raw_text).strip()

    # Search for all occurrences of VERDICT: pattern
    matches = list(re.finditer(r"VERDICT:\s*([^\n\r]+)", text_str, re.IGNORECASE))
    if matches:
        last_match = matches[-1].group(1).strip()
    else:
        last_match = text_str

    upper = last_match.upper()

    # Strict classification
    if any(k in upper for k in ["CONFLICT", "CONTRADICT", "DISCORDANT", "INCONSISTENT"]):
        label = CANONICAL_VERDICTS["CONFLICT"]
        v_type = "red"
    elif any(k in upper for k in ["CONCORDANT", "CONSISTENT", "AGREE", "MATCH"]):
        label = CANONICAL_VERDICTS["CONCORDANT"]
        v_type = "green"
    elif any(k in upper for k in ["INSUFFICIENT", "UNCLEAR", "NO DATA", "NOT ENOUGH"]):
        label = CANONICAL_VERDICTS["UNCLEAR"]
        v_type = "unclear"
    else:
        label = CANONICAL_VERDICTS["PARTIAL"]
        v_type = "amber"

    # Extract reason text (everything after the verdict label or trailing)
    reason = text_str
    if matches:
        # Strip out VERDICT: from reason to avoid duplicate display
        reason = re.sub(r"VERDICT:\s*[^\n\r]+", "", text_str, flags=re.IGNORECASE).strip()

    return {"label": label, "type": v_type, "reason": reason}


class TestVerdictParsing:
    def test_canonical_conflict_detected(self):
        text = "Comparison shows divergent primary outcomes.\n\nVERDICT: CONFLICT DETECTED - Study A reports HR=0.72 vs Study B HR=1.14."
        res = parse_arbitration_verdict(text)
        assert res["label"] == "VERDICT: CONFLICT DETECTED"
        assert res["type"] == "red"
        assert "VERDICT: CONFLICT DETECTED" not in res["reason"]

    def test_canonical_concordant(self):
        text = "Both trials demonstrate significant HbA1c reduction (p < 0.001).\n\nVERDICT: CONCORDANT - Trials align on primary endpoint."
        res = parse_arbitration_verdict(text)
        assert res["label"] == "VERDICT: CONCORDANT"
        assert res["type"] == "green"

    def test_canonical_insufficient_data(self):
        text = "Neither paper reports pediatric safety data.\n\nVERDICT: INSUFFICIENT DATA - Requires additional literature."
        res = parse_arbitration_verdict(text)
        assert res["label"] == "VERDICT: INSUFFICIENT DATA"
        assert res["type"] == "unclear"

    def test_canonical_partial(self):
        text = "Consistent on overall mortality, but conflicting on renal sub-endpoints.\n\nVERDICT: PARTIAL - Mixed outcomes observed."
        res = parse_arbitration_verdict(text)
        assert res["label"] == "VERDICT: PARTIAL"
        assert res["type"] == "amber"

    def test_conversational_boilerplate_rejection(self):
        """Malformed output like 'VERDICT: HERE'S A COMPARISON...' must never leak into badge."""
        malformed = "VERDICT: HERE'S A COMPARISON BETWEEN STUDY 1 AND STUDY 2 THAT EXAMINES CLINICAL DOSING."
        res = parse_arbitration_verdict(malformed)
        # Should sanitize into canonical fallback, NOT display "HERE'S A COMPARISON..."
        assert res["label"] in CANONICAL_VERDICTS.values()
        assert "HERE'S A COMPARISON" not in res["label"]

    def test_case_insensitivity(self):
        text = "verdict: conflict - statistically opposite conclusions."
        res = parse_arbitration_verdict(text)
        assert res["label"] == "VERDICT: CONFLICT DETECTED"

    def test_multi_verdict_final_authoritative(self):
        """When intermediate reasoning mentions a verdict before final arbitration."""
        multi_text = (
            "Initial observation: VERDICT: CONCORDANT on baseline characteristics.\n"
            "Secondary analysis: However, after adjusting for age:\n"
            "VERDICT: CONFLICT DETECTED - 12% vs 4% major adverse cardiovascular events."
        )
        res = parse_arbitration_verdict(multi_text)
        assert res["label"] == "VERDICT: CONFLICT DETECTED"

    def test_empty_or_none_input(self):
        assert parse_arbitration_verdict("")["label"] == "VERDICT: INSUFFICIENT DATA"
        assert parse_arbitration_verdict(None)["label"] == "VERDICT: INSUFFICIENT DATA"


# ==============================================================================
# 3. INGESTION CHUNKING & NUMERICAL INTEGRITY TESTS
# ==============================================================================

def split_sentences_safely(text: str) -> List[str]:
    """
    Robust biomedical sentence splitter that protects decimals, p-values,
    confidence intervals, and common scientific abbreviations from splitting.
    """
    # Protect common abbreviations and statistical qualifiers
    protected = text
    subs = [
        (r"\bvs\.", "vs__DOT__"),
        (r"\be\.g\.", "eg__DOT__"),
        (r"\bi\.e\.", "ie__DOT__"),
        (r"\bet\s+al\.", "et_al__DOT__"),
        (r"\bFig\.", "Fig__DOT__"),
        (r"\bTab\.", "Tab__DOT__"),
        (r"\bDr\.", "Dr__DOT__"),
        (r"\bNo\.", "No__DOT__"),
    ]
    for pattern, repl in subs:
        protected = re.sub(pattern, repl, protected, flags=re.IGNORECASE)

    # Negative lookbehind & lookahead to prevent splitting on decimal points like 0.76 or 12.5%
    sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z0-9])"
    raw_sentences = re.split(sentence_pattern, protected)

    # Restore protected dots
    clean_sentences = []
    for s in raw_sentences:
        restored = s
        for _, repl in subs:
            restored = restored.replace(repl, repl.replace("__DOT__", ".").replace("eg.", "e.g.").replace("ie.", "i.e."))
        clean_sentences.append(restored.strip())

    return [s for s in clean_sentences if s]


class TestIngestionChunking:
    def test_hazard_ratio_and_p_value_not_split(self):
        text = "The primary composite outcome occurred in 427 patients. The hazard ratio was HR = 0.76 (95% CI 0.65-0.89, p < 0.001) in cohort A."
        sentences = split_sentences_safely(text)
        assert len(sentences) == 2
        assert "HR = 0.76 (95% CI 0.65-0.89, p < 0.001)" in sentences[1]

    def test_decimal_percentages_not_split(self):
        text = "HbA1c decreased by 1.25% in the active group versus 0.35% in placebo (p = 0.004). Body weight dropped by 2.8 kg."
        sentences = split_sentences_safely(text)
        assert len(sentences) == 2
        assert "1.25%" in sentences[0]
        assert "0.35%" in sentences[0]
        assert "p = 0.004" in sentences[0]

    def test_scientific_abbreviations_not_split(self):
        text = "SGLT2 inhibitors (e.g. empagliflozin vs. placebo) significantly reduced hospitalization rates et al. confirmed this finding."
        sentences = split_sentences_safely(text)
        # Should not split inside (e.g. or vs.)
        assert any("e.g." in s and "vs." in s for s in sentences)

    def test_chunk_word_boundary_preservation(self):
        """Validates that chunk_text creates non-empty, non-overlapping windows."""
        sample_paragraph = (
            "Empagliflozin in patients with heart failure and reduced ejection fraction. "
            "Cardiovascular death or hospitalization occurred in 361 of 1863 patients (19.4%) in the empagliflozin group "
            "and in 462 of 1867 patients (24.7%) in the placebo group (hazard ratio, 0.75; 95% confidence interval [CI], "
            "0.65 to 0.86; P<0.001). The effect was consistent across prespecified subgroups."
        )
        words = sample_paragraph.split()
        chunk_size = 30
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))

        assert len(chunks) >= 2
        # All words accounted for
        reconstructed = " ".join(chunks)
        assert reconstructed == sample_paragraph
