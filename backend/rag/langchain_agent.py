"""LangChain Orchestration Agent for RAG-grounded Underwriting Synthesis.

Combines ChromaDB vector retrieval with prompt augmentation and Pydantic schema validation.
Ensures every generated executive summary and KRI is directly cited and grounded.
"""

from typing import List, Dict, Any, Tuple
from backend.schemas import (
    InputRiskPayload,
    NormalizedRiskProfile,
    UnderwritingSynthesisReport,
    GuidelineBreach,
    RetrievedGuideline,
)
from backend.rag.chroma_manager import ChromaGuidelineManager
from backend.rag.langchain_retriever import LangChainGuidelineRetriever


class LangChainRAGAgent:
    """Orchestrates LangChain RAG pipeline for grounded underwriting synthesis."""

    def __init__(self, chroma_manager: ChromaGuidelineManager):
        self.chroma_manager = chroma_manager
        self.retriever = LangChainGuidelineRetriever(chroma_manager)

    def retrieve_grounding_context(
        self,
        payload: InputRiskPayload,
        normalized: NormalizedRiskProfile
    ) -> Tuple[List[RetrievedGuideline], List[GuidelineBreach], str]:
        """Retrieves domain guidelines, isolates breaches, and formats LLM context prompt."""
        retrieved, breaches = self.retriever.retrieve_guidelines_for_profile(payload, normalized)

        # Build prompt context block
        lines = [
            "### RETRIEVED CORPORATE UNDERWRITING GUIDELINES (GROUND TRUTH RULES):",
            "You MUST ground your executive summary and verdict strictly in these retrieved policy clauses:"
        ]

        for r in retrieved:
            lines.append(f"\n- **[{r.rule_id}] {r.title}** (Manual: {r.manual}, Match Confidence: {r.relevance_score * 100:.1f}%)")
            lines.append(f"  {r.excerpt}")

        if breaches:
            lines.append("\n### IDENTIFIED CORPORATE GUIDELINE BREACHES:")
            for b in breaches:
                lines.append(f"- **[{b.rule_id}] {b.title}** ({b.severity} SEVERITY):")
                lines.append(f"  * Corporate Standard: {b.corporate_threshold}")
                lines.append(f"  * Applicant Observed: {b.applicant_observed}")
                lines.append(f"  * Required Mitigation: {b.actionable_mitigation}")

        context_prompt = "\n".join(lines)
        return retrieved, breaches, context_prompt
