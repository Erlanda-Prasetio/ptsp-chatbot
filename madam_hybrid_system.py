"""Madam Hybrid RAG system with four-phase fallback pipeline.

This variant extends the existing Hybrid RAG logic by inserting a MADAM debate
stage between the enhanced vector search and the internet fallback. The debate
stage coordinates multi-agent reasoning over the retrieved documents before
falling back to web search.
"""
import importlib.util
import time
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from hybrid_rag import HybridRAGSystem  # type: ignore
from hybrid_rag import SmartEnhancedRAG, EnhancedInternetSearch, query_llm  # type: ignore

try:
    _MADAM_MODULE_PATH = Path(__file__).resolve().parent / "testing" / "madam-rag" / "run_madam_rag.py"
    _MADAM_SPEC = importlib.util.spec_from_file_location("madam_rag_debate", str(_MADAM_MODULE_PATH))
    _MADAM_MODULE = importlib.util.module_from_spec(_MADAM_SPEC) if _MADAM_SPEC else None
    if _MADAM_SPEC and _MADAM_SPEC.loader and _MADAM_MODULE:
        _MADAM_SPEC.loader.exec_module(_MADAM_MODULE)
        multi_agent_debate = getattr(_MADAM_MODULE, "multi_agent_debate")  # type: ignore
    else:
        raise ImportError("Unable to load MADAM debate module specification")
except Exception as exc:  # pragma: no cover - defensive import guard
    multi_agent_debate = None  # type: ignore
    print(f"⚠️  MADAM debate module unavailable: {exc}")


class _MadamDebateGenerator:
    """Adapter that reuses query_llm to satisfy the MADAM generator interface."""

    def __call__(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 256,
        top_p: Optional[float] = None,
        do_sample: bool = False,
    ) -> List[Dict[str, Any]]:
        prompt = "\n".join(msg.get("content", "") for msg in messages)
        result = query_llm(prompt, "")
        if isinstance(result, dict):
            text = result.get("text", "")
            model = result.get("model", "unknown")
            usage = result.get("usage", {})
        else:
            text = str(result)
            model = "unknown"
            usage = {}
        return [
            {
                "generated_text": [
                    {"role": "user", "content": prompt},
                    {
                        "role": "assistant",
                        "content": text,
                        "model": model,
                        "usage": usage,
                    },
                ]
            }
        ]


class MadamHybridRAGSystem(HybridRAGSystem):
    """Hybrid system with MADAM multi-agent debate as an additional fallback."""

    def __init__(self, debate_rounds: int = 3, debate_top_k: int = 4):
        print("🚀 Initializing Madam Hybrid RAG System...")
        super().__init__()
        self.rag_system = SmartEnhancedRAG()
        self.internet_search = EnhancedInternetSearch()
        self.debate_rounds = debate_rounds
        self.debate_top_k = debate_top_k
        self.vector_quality_threshold = 0.75
        self.enhanced_quality_threshold = 0.60
        self.debate_generator = _MadamDebateGenerator()
        self.debate_available = multi_agent_debate is not None
        self.debate_timeout = 8.0
        self.total_timeout = self.vector_timeout + self.enhanced_timeout + self.debate_timeout + self.internet_timeout
        print(
            "✅ Madam Hybrid RAG System ready with phases: vector → enhanced → MADAM debate → internet"
        )
        print(
            f"⏱️  Timeouts: Vector({self.vector_timeout}s) + Enhanced({self.enhanced_timeout}s) + "
            f"Debate({self.debate_timeout}s) + Internet({self.internet_timeout}s) = {self.total_timeout}s"
        )

    def ask_with_fallback(self, question: str, k: int = 12) -> Dict[str, Any]:
        start_time = time.time()
        phase_times: Dict[str, str] = {}
        phase_log: List[Dict[str, Any]] = []

        vector_result, vector_quality, vector_reason, vector_elapsed = self._run_vector_phase(question, k)
        phase_times["vector_only"] = f"{vector_elapsed:.2f}s"
        phase_log.append(
            {
                "phase": "vector_only",
                "quality": vector_quality,
                "reason": vector_reason,
            }
        )
        if vector_result and vector_quality >= self.vector_quality_threshold:
            return self._finalize_result(
                vector_result,
                method="vector_only",
                quality_score=vector_quality,
                phase_times=phase_times,
                phase_log=phase_log,
                start_time=start_time,
            )

        enhanced_data = self._run_enhanced_phase(question, k)
        (
            enhanced_result,
            enhanced_quality,
            enhanced_reason,
            enhanced_elapsed,
            expanded_query,
            debate_documents,
        ) = enhanced_data
        phase_times["enhanced_vector"] = f"{enhanced_elapsed:.2f}s"
        phase_log.append(
            {
                "phase": "enhanced_vector",
                "quality": enhanced_quality,
                "reason": enhanced_reason,
                "expanded_query": expanded_query,
            }
        )
        if enhanced_result and enhanced_quality >= self.enhanced_quality_threshold:
            return self._finalize_result(
                enhanced_result,
                method="enhanced_vector",
                quality_score=enhanced_quality,
                phase_times=phase_times,
                phase_log=phase_log,
                start_time=start_time,
                extra_features={"expanded_query": expanded_query},
            )

        debate_result = self._run_madam_debate_phase(
            question,
            debate_documents,
            enhanced_result,
            phase_times,
            phase_log,
            start_time,
            enhanced_quality,
        )
        if debate_result:
            return debate_result

        # 45 second gap after MADAM Debate (heavy phase with multiple LLM calls)
        print("⏳ 45s gap after MADAM Debate phase (API recovery for debate calls)...")
        time.sleep(45)

        internet_result = self._run_internet_phase(question, phase_times, phase_log, start_time)
        if internet_result:
            return internet_result

        return self._fallback_response(question, {k: float(v[:-1]) for k, v in phase_times.items() if v.endswith("s")})

    def _run_vector_phase(
        self, question: str, k: int
    ) -> Tuple[Optional[Dict[str, Any]], float, str, float]:
        start = time.time()
        try:
            result = self.rag_system.ask(question, k=k)
            quality, reason = self.assess_result_quality(result)
            elapsed = time.time() - start
            return result, quality, reason, elapsed
        except Exception as exc:
            elapsed = time.time() - start
            print(f"❌ Vector phase error: {exc}")
            return None, 0.0, "phase_error", elapsed

    def _run_enhanced_phase(
        self, question: str, k: int
    ) -> Tuple[Optional[Dict[str, Any]], float, str, float, str, List[str]]:
        start = time.time()
        expanded_query = self.expand_query_for_retry(question)
        documents: List[str] = []
        try:
            result = self.rag_system.ask(expanded_query, k=k * 2)
            quality, reason = self.assess_result_quality(result)
            documents = self._extract_documents_for_debate(result)
            elapsed = time.time() - start
            return result, quality, reason, elapsed, expanded_query, documents
        except Exception as exc:
            elapsed = time.time() - start
            print(f"❌ Enhanced phase error: {exc}")
            return None, 0.0, "phase_error", elapsed, expanded_query, documents

    def _run_madam_debate_phase(
        self,
        question: str,
        documents: List[str],
        base_result: Optional[Dict[str, Any]],
        phase_times: Dict[str, str],
        phase_log: List[Dict[str, Any]],
        start_time: float,
        base_quality: float,
    ) -> Optional[Dict[str, Any]]:
        if not self.debate_available:
            print("⚠️  MADAM debate skipped: module unavailable")
            phase_log.append({"phase": "madam_debate", "skipped": True})
            return None
        if not documents:
            print("⚠️  MADAM debate skipped: no documents available")
            phase_log.append({"phase": "madam_debate", "skipped": True, "reason": "no_documents"})
            return None

        debate_start = time.time()
        try:
            records = multi_agent_debate(  # type: ignore
                question,
                documents[: self.debate_top_k],
                self.debate_generator,
                num_rounds=self.debate_rounds,
            )
        except Exception as exc:
            elapsed = time.time() - debate_start
            phase_times["madam_debate"] = f"{elapsed:.2f}s"
            print(f"❌ MADAM debate failed: {exc}")
            phase_log.append({"phase": "madam_debate", "error": str(exc)})
            return None

        elapsed = time.time() - debate_start
        phase_times["madam_debate"] = f"{elapsed:.2f}s"
        final_aggregation = records.get("final_aggregation", "") if isinstance(records, dict) else ""
        if not final_aggregation or "unknown" in final_aggregation.lower():
            print("⚠️  MADAM debate produced unknown answer")
            phase_log.append(
                {
                    "phase": "madam_debate",
                    "result": "unknown",
                    "aggregation": final_aggregation,
                }
            )
            return None

        formatted_answer = self._format_debate_output(final_aggregation)
        if base_result:
            response = {
                "answer": formatted_answer,
                "sources": base_result.get("sources", []),
                "total_sources": base_result.get("total_sources", len(base_result.get("sources", []))),
                "enhanced_features": dict(base_result.get("enhanced_features", {})),
            }
        else:
            response = {
                "answer": formatted_answer,
                "sources": [],
                "total_sources": 0,
                "enhanced_features": {},
            }

        debate_quality = max(base_quality, 0.65)
        response = self._finalize_result(
            response,
            method="madam_debate",
            quality_score=debate_quality,
            phase_times=phase_times,
            phase_log=phase_log + [
                {
                    "phase": "madam_debate",
                    "quality": debate_quality,
                    "aggregation_preview": final_aggregation[:2000],
                }
            ],
            start_time=start_time,
            extra_features={
                "madam_debate": {
                    "documents_used": len(documents[: self.debate_top_k]),
                    "rounds": self.debate_rounds,
                    "final_aggregation": final_aggregation,
                }
            },
        )
        return response

    def _run_internet_phase(
        self,
        question: str,
        phase_times: Dict[str, str],
        phase_log: List[Dict[str, Any]],
        start_time: float,
    ) -> Optional[Dict[str, Any]]:
        internet_start = time.time()
        try:
            internet_results = self.internet_search.search_multiple_engines(question)
            elapsed = time.time() - internet_start
            phase_times["internet_fallback"] = f"{elapsed:.2f}s"
            if not internet_results:
                print("❌ No internet results found")
                phase_log.append({"phase": "internet_fallback", "result": "no_results"})
                return None

            internet_context = self.internet_search.format_internet_context(internet_results)
            llm_result = query_llm(question, internet_context)
            internet_answer = llm_result["text"] if isinstance(llm_result, dict) else llm_result
            response = {
                "answer": internet_answer,
                "sources": [
                    {
                        "text": item.get("content", ""),
                        "metadata": {
                            "source": item.get("url", ""),
                            "title": item.get("title", ""),
                            "relevance_score": item.get("relevance_score", 0),
                        },
                    }
                    for item in internet_results
                ],
                "total_sources": len(internet_results),
                "enhanced_features": {
                    "internet_engines": ["duckduckgo"]
                    + (["serper"] if self.internet_search.serper_key else []),
                    "model": llm_result.get("model", "unknown") if isinstance(llm_result, dict) else "unknown",
                    "usage": llm_result.get("usage", {}) if isinstance(llm_result, dict) else {},
                },
            }
            response = self._finalize_result(
                response,
                method="internet_fallback",
                quality_score=0.55,
                phase_times=phase_times,
                phase_log=phase_log + [
                    {
                        "phase": "internet_fallback",
                        "quality": 0.55,
                        "sources": len(internet_results),
                    }
                ],
                start_time=start_time,
            )
            return response
        except Exception as exc:
            elapsed = time.time() - internet_start
            phase_times["internet_fallback"] = f"{elapsed:.2f}s"
            print(f"❌ Internet fallback failed: {exc}")
            phase_log.append({"phase": "internet_fallback", "error": str(exc)})
            return None

    def _extract_documents_for_debate(self, result: Optional[Dict[str, Any]]) -> List[str]:
        if not result:
            return []
        documents: List[str] = []
        sources = result.get("sources", []) or []
        for source in sources:
            text = self._source_to_text(source)
            if text:
                documents.append(text)
            if len(documents) >= self.debate_top_k:
                break
        return documents

    def _source_to_text(self, source: Dict[str, Any]) -> Optional[str]:
        metadata = source.get("metadata", {}) or {}
        text_candidates = [
            metadata.get("text"),
            metadata.get("content"),
            metadata.get("raw_text"),
            source.get("content_preview"),
            source.get("text"),
        ]
        for candidate in text_candidates:
            if candidate:
                return str(candidate)
        path = source.get("path") or metadata.get("source")
        store = getattr(self.rag_system, "store", None)
        if not store or not hasattr(store, "meta") or not hasattr(store, "texts"):
            return None
        if path:
            for meta, text in zip(store.meta, store.texts):
                if meta.get("source") == path:
                    return str(text)
        return None

    def _format_debate_output(self, aggregation: str) -> str:
        cleaned = aggregation.strip()
        if not cleaned:
            return cleaned
        answer_match = re.search(r"All Correct Answers:\s*(\[[^\]]*\])", cleaned, re.IGNORECASE)
        explanation_match = re.search(r"Explanation:\s*(.*)", cleaned, re.IGNORECASE | re.DOTALL)
        if answer_match or explanation_match:
            answers = answer_match.group(1) if answer_match else "[]"
            explanation = explanation_match.group(1).strip() if explanation_match else ""
            return f"Jawaban akhir MADAM-RAG: {answers}\n\nPenjelasan: {explanation}"
        return cleaned

    def _finalize_result(
        self,
        result: Dict[str, Any],
        *,
        method: str,
        quality_score: float,
        phase_times: Dict[str, str],
        phase_log: List[Dict[str, Any]],
        start_time: float,
        extra_features: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        enhanced_features = result.setdefault("enhanced_features", {})
        enhanced_features.update(
            {
                "search_method": method,
                "quality_score": round(quality_score, 3),
                "phase_times": phase_times,
                "phase_log": phase_log,
                "response_time": f"{time.time() - start_time:.2f}s",
                "system_variant": "system_3_madam",
            }
        )
        if extra_features:
            enhanced_features.update(extra_features)
        if "total_sources" not in result:
            result["total_sources"] = len(result.get("sources", []))
        return result
