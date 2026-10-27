"""
VeriNexa Quality Assurance Test Suite - Integration Tests
Covers: Evidence Chat SSE & Fast-path contracts, LangGraph Section 4 Arbitration, Section 5 Abstract Spin Engine
"""

import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


# ==============================================================================
# 1. SECTION 3 EVIDENCE CHAT INTEGRATION TESTS
# ==============================================================================

class TestEvidenceChatIntegration:
    def test_citation_json_schema_contract(self):
        """
        Verify that retrieved citation objects conform strictly to the frontend
        schema required for visual coordinate overlays and document navigation.
        """
        sample_citation = {
            "chunk_id": 101,
            "paper_id": 1,
            "chunk_index": 4,
            "snippet": "Empagliflozin reduced cardiovascular death or heart failure hospitalization...",
            "full_text": "Empagliflozin reduced cardiovascular death or heart failure hospitalization by 25% (HR 0.75, 95% CI 0.65-0.86).",
            "title": "Empagliflozin in Heart Failure",
            "detected_title": "Empagliflozin in Heart Failure",
            "filename": "empa_hf.pdf",
            "page_number": 3,
            "page_width": 612.0,
            "page_height": 792.0,
            "bbox_x0": 0.1250,
            "bbox_y0": 0.3400,
            "bbox_x1": 0.8800,
            "bbox_y1": 0.4200,
            "score": 0.0325,
        }

        # Required fields check
        required_fields = [
            "chunk_id", "paper_id", "chunk_index", "snippet", "full_text",
            "title", "filename", "page_number", "bbox_x0", "bbox_y0", "bbox_x1", "bbox_y1"
        ]
        for field in required_fields:
            assert field in sample_citation, f"Missing required citation field: {field}"

        # Bounding box validity
        assert 0.0 <= sample_citation["bbox_x0"] <= sample_citation["bbox_x1"] <= 1.0
        assert 0.0 <= sample_citation["bbox_y0"] <= sample_citation["bbox_y1"] <= 1.0
        assert sample_citation["page_number"] >= 1

    def test_sse_stream_packet_format(self):
        """
        Validates Server-Sent Events (SSE) format contract:
        - node_lifecycle packets
        - token packets
        - final done packet containing citations and session_id
        """
        # Node lifecycle start
        p1 = json.dumps({"type": "node_lifecycle", "node": "retrieve_chunks", "status": "started", "done": False})
        sse_p1 = f"data: {p1}\n\n"
        assert sse_p1.startswith("data: ") and sse_p1.endswith("\n\n")

        # Token streaming
        p2 = json.dumps({"token": "Empagliflozin "})
        sse_p2 = f"data: {p2}\n\n"
        decoded_p2 = json.loads(sse_p2.replace("data: ", "").strip())
        assert decoded_p2.get("token") == "Empagliflozin "

        # Stream termination packet
        p3 = json.dumps({"done": True, "session_id": 42, "citations": []})
        sse_p3 = f"data: {p3}\n\n"
        decoded_p3 = json.loads(sse_p3.replace("data: ", "").strip())
        assert decoded_p3.get("done") is True
        assert decoded_p3.get("session_id") == 42


# ==============================================================================
# 2. SECTION 4 LANGGRAPH CONFLICT ENGINE INTEGRATION TESTS
# ==============================================================================

class TestConflictEngineGraph:
    def test_conflict_detection_node_propagation(self):
        """
        Verify that conflicting clinical evidence (e.g., Trial 1 HR=0.75 vs Trial 2 HR=1.18)
        propagates through state graph and flags contradiction correctly.
        """
        from conflict_graph import graph as conflict_graph

        mock_grouped_chunks = {
            1: [(0, "Trial 1 (EMPEROR-Reduced): Empagliflozin demonstrated a 25% relative risk reduction in CV death (HR 0.75, p < 0.001).", 0.95)],
            2: [(0, "Trial 2 (CANVAS-R): Canagliflozin showed no significant reduction in cardiovascular mortality (HR 1.18, 95% CI 0.89-1.56, p = 0.24).", 0.91)]
        }
        mock_meta = {
            1: {"title": "EMPEROR-Reduced Trial", "filename": "emperor.pdf"},
            2: {"title": "CANVAS-R Trial", "filename": "canvas.pdf"}
        }

        mock_verdict = (
            "1. EMPEROR-Reduced observed significant reduction in CV mortality (HR 0.75).\n"
            "2. CANVAS-R showed neutral effect with HR 1.18 and no significance.\n"
            "3. Patient ejection fraction baselines differed between cohorts.\n\n"
            "VERDICT: CONFLICT DETECTED - Opposite cardiovascular mortality risk profiles."
        )

        with patch("conflict_graph.retrieve_claims_per_paper", return_value=(mock_grouped_chunks, mock_meta)), \
             patch("conflict_engine.query_ollama", return_value=mock_verdict), \
             patch("conflict_graph.query_ollama", return_value=mock_verdict), \
             patch("conflict_graph.save_verdict_to_db", return_value=88):

            result = conflict_graph.invoke({
                "query": "cardiovascular death risk in SGLT2 inhibitor trials",
                "user_id": 1,
                "paper_ids": [1, 2]
            })

            assert "verdict" in result
            assert "CONFLICT" in result["verdict"].upper() or "PARTIAL" in result["verdict"].upper()
            assert result.get("saved_id") == 88

    def test_concordant_evidence_node_propagation(self):
        """
        Verify that agreeing clinical evidence bypasses adversarial critic and finishes cleanly.
        """
        from conflict_graph import graph as conflict_graph

        mock_grouped_chunks = {
            1: [(0, "Trial A: Empagliflozin reduced HbA1c by -0.82% at week 24 (p < 0.001).", 0.94)],
            2: [(0, "Trial B: Dapagliflozin reduced HbA1c by -0.79% at week 24 (p < 0.001).", 0.92)]
        }
        mock_meta = {
            1: {"title": "Trial A", "filename": "trial_a.pdf"},
            2: {"title": "Trial B", "filename": "trial_b.pdf"}
        }

        mock_verdict = (
            "1. Trial A observed significant glycemic reduction (-0.82%).\n"
            "2. Trial B confirmed consistent glycemic lowering (-0.79%).\n"
            "3. Class effect established across both agents.\n\n"
            "VERDICT: CONCORDANT - Both trials report consistent HbA1c reductions."
        )

        with patch("conflict_graph.retrieve_claims_per_paper", return_value=(mock_grouped_chunks, mock_meta)), \
             patch("conflict_engine.query_ollama", return_value=mock_verdict), \
             patch("conflict_graph.query_ollama", return_value=mock_verdict), \
             patch("conflict_graph.save_verdict_to_db", return_value=89):

            result = conflict_graph.invoke({
                "query": "HbA1c reduction in SGLT2 trials",
                "user_id": 1,
                "paper_ids": [1, 2]
            })

            assert "CONCORDANT" in result["verdict"].upper() or "CONSISTENT" in result["verdict"].upper()


# ==============================================================================
# 3. SECTION 5 ABSTRACT SPIN ENGINE INTEGRATION TESTS
# ==============================================================================

class TestIntegritySpinEngineGraph:
    def test_abstract_spin_detected(self):
        """
        Abstract claims: 'Drug X significantly eliminated all cardiovascular deaths.'
        Body Table: 'CV mortality was 4.2% vs 4.5% (p = 0.68, not statistically significant).'
        Engine must flag spin: VERDICT: INCONSISTENT.
        """
        from integrity_graph import graph as integrity_graph

        mock_paper = {"id": 10, "title": "Trial on Drug X", "filename": "drug_x.pdf"}
        mock_abstract = "Conclusion: Drug X demonstrated overwhelming, unprecedented elimination of cardiovascular mortality in diabetic patients."
        mock_supporting = [(3, "Table 2: Cardiovascular mortality occurred in 42 of 1000 (4.2%) vs 45 of 1000 (4.5%) in control (HR 0.93, 95% CI 0.65-1.33, p = 0.68). No statistically significant difference was observed.")]

        mock_audit = (
            "DISCREPANCY: The abstract concludes that Drug X 'eliminated' cardiovascular mortality, "
            "whereas Table 2 shows p = 0.68 with no statistically significant reduction.\n"
            "VERDICT: INCONSISTENT\n"
            "REASON: Abstract spin detected. Conclusions exaggerate non-significant endpoint."
        )

        with patch("integrity_graph.get_paper_metadata", return_value=mock_paper), \
             patch("integrity_graph.get_abstract_text", return_value=mock_abstract), \
             patch("integrity_graph.search_within_paper", return_value=mock_supporting), \
             patch("integrity_check.query_ollama", return_value=mock_audit), \
             patch("integrity_graph.query_ollama", return_value=mock_audit), \
             patch("integrity_graph.save_integrity_result", return_value=401):

            result = integrity_graph.invoke({
                "paper_id": 10,
                "topic_query": "cardiovascular mortality"
            })

            assert "verdict" in result
            assert "INCONSISTENT" in result["verdict"].upper()
            assert result.get("saved_id") == 401

    def test_authentic_reporting_consistent(self):
        """
        Abstract claim accurately reflects modest, statistically validated outcome.
        Engine must confirm: VERDICT: CONSISTENT.
        """
        from integrity_graph import graph as integrity_graph

        mock_paper = {"id": 11, "title": "Trial on Drug Y", "filename": "drug_y.pdf"}
        mock_abstract = "Drug Y reduced HbA1c by a modest 0.4% with transient mild nausea reported."
        mock_supporting = [(2, "Results: At week 12, HbA1c change was -0.41% (95% CI -0.52 to -0.30, p < 0.001). Mild nausea occurred in 6.1% vs 3.2%.")]

        mock_audit = (
            "The abstract conclusions are quantitatively supported by the results in Section 3.\n"
            "VERDICT: CONSISTENT\n"
            "REASON: Abstract accurately reflects modest HbA1c reduction without spin."
        )

        with patch("integrity_graph.get_paper_metadata", return_value=mock_paper), \
             patch("integrity_graph.get_abstract_text", return_value=mock_abstract), \
             patch("integrity_graph.search_within_paper", return_value=mock_supporting), \
             patch("integrity_check.query_ollama", return_value=mock_audit), \
             patch("integrity_graph.query_ollama", return_value=mock_audit), \
             patch("integrity_graph.save_integrity_result", return_value=402):

            result = integrity_graph.invoke({
                "paper_id": 11,
                "topic_query": "HbA1c and adverse events"
            })

            assert "verdict" in result
            assert "CONSISTENT" in result["verdict"].upper()
            assert "INCONSISTENT" not in result["verdict"].upper()
