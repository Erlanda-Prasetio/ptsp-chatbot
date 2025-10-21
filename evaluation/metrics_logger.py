"""
Metrics Logger for RAG System Evaluation
Captures: Accuracy, Precision, Recall, F1, Confident Wrong, Response Time, Token Usage, Model Name
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import os


class MetricsLogger:
    """
    Logger to capture evaluation metrics for RAG systems.
    
    Metrics captured:
    - accuracy: Correctness of answer (0 or 1, calculated later in batch)
    - precision: Relevance of retrieved chunks (TP / (TP + FP))
    - recall: Coverage of relevant chunks (TP / (TP + FN))
    - f1_score: Harmonic mean of precision and recall
    - confident_wrong: False positives with high confidence (>0.8)
    - response_time: Time to generate response (seconds)
    - token_usage: Tokens consumed (prompt + completion)
    - model_name: LLM model used
    """
    
    def __init__(self, log_dir: str = "evaluation/logs", experiment_name: str = None):
        """
        Initialize metrics logger.
        
        Args:
            log_dir: Directory to save logs
            experiment_name: Name of experiment (e.g., "baseline", "baseline_updated_data", "madam_rag")
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.experiment_name = experiment_name or f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_file = self.log_dir / f"{self.experiment_name}.jsonl"
        
        self.current_query_data = {}
        self.start_time = None
        
    def start_query(self, query_id: str, query_text: str, ground_truth: Optional[str] = None):
        """
        Start logging for a new query.
        
        Args:
            query_id: Unique identifier for the query
            query_text: The user query
            ground_truth: Expected correct answer (for accuracy calculation)
        """
        self.current_query_data = {
            "query_id": query_id,
            "query_text": query_text,
            "ground_truth": ground_truth,
            "timestamp": datetime.now().isoformat(),
            "experiment_name": self.experiment_name,
        }
        self.start_time = time.time()
        
    def log_retrieval(self, 
                     retrieved_chunks: List[Dict], 
                     relevant_chunk_ids: Optional[List[str]] = None):
        """
        Log retrieval results for precision/recall calculation.
        
        Args:
            retrieved_chunks: List of retrieved chunks with metadata
                Format: [{"chunk_id": "...", "similarity": 0.85, "text": "..."}]
            relevant_chunk_ids: Ground truth relevant chunk IDs (for precision/recall)
        """
        retrieved_ids = [chunk.get("chunk_id") or chunk.get("id") for chunk in retrieved_chunks]
        
        # Calculate precision and recall if ground truth provided
        precision = None
        recall = None
        f1_score = None
        
        if relevant_chunk_ids:
            retrieved_set = set(retrieved_ids)
            relevant_set = set(relevant_chunk_ids)
            
            true_positive = len(retrieved_set & relevant_set)
            false_positive = len(retrieved_set - relevant_set)
            false_negative = len(relevant_set - retrieved_set)
            
            # Precision: TP / (TP + FP)
            precision = true_positive / len(retrieved_set) if retrieved_set else 0.0
            
            # Recall: TP / (TP + FN)
            recall = true_positive / len(relevant_set) if relevant_set else 0.0
            
            # F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
            if precision + recall > 0:
                f1_score = 2 * (precision * recall) / (precision + recall)
            else:
                f1_score = 0.0
        
        self.current_query_data["retrieval"] = {
            "retrieved_chunk_ids": retrieved_ids,
            "num_retrieved": len(retrieved_ids),
            "relevant_chunk_ids": relevant_chunk_ids,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "chunks": [
                {
                    "chunk_id": chunk.get("chunk_id") or chunk.get("id"),
                    "similarity": chunk.get("similarity") or chunk.get("score"),
                    "text_preview": chunk.get("text", "")[:200]  # First 200 chars
                }
                for chunk in retrieved_chunks
            ]
        }
        
    def log_response(self, 
                    response_text: str,
                    model_name: str,
                    token_usage: Optional[Dict[str, int]] = None,
                    confidence_score: Optional[float] = None,
                    is_correct: Optional[bool] = None):
        """
        Log the final response and metrics.
        
        Args:
            response_text: Generated answer
            model_name: LLM model used (e.g., "mistralai/mistral-small")
            token_usage: Token counts {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
            confidence_score: System's confidence in answer (0.0-1.0)
            is_correct: Whether answer is correct (None if not evaluated yet)
        """
        end_time = time.time()
        response_time = end_time - self.start_time if self.start_time else None
        
        # Detect confident wrong (false positive with high confidence)
        confident_wrong = False
        if is_correct is not None and confidence_score is not None:
            confident_wrong = (not is_correct) and (confidence_score > 0.8)
        
        self.current_query_data["response"] = {
            "text": response_text,
            "model_name": model_name,
            "confidence_score": confidence_score,
            "is_correct": is_correct,
            "confident_wrong": confident_wrong,
            "response_time_seconds": response_time,
            "token_usage": token_usage or {
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None
            }
        }
        
        # Write to log file
        self._write_log()
        
    def log_madam_debate(self,
                        agent_responses: List[Dict],
                        aggregated_response: str,
                        num_rounds: int,
                        converged: bool):
        """
        Log MADAM-RAG specific metrics.
        
        Args:
            agent_responses: List of agent responses per round
                Format: [{"agent_id": "vector_1", "response": "...", "confidence": 0.85}]
            aggregated_response: Final aggregated answer
            num_rounds: Number of debate rounds
            converged: Whether agents converged
        """
        self.current_query_data["madam_debate"] = {
            "num_rounds": num_rounds,
            "converged": converged,
            "num_agents": len(agent_responses),
            "agent_responses": agent_responses,
            "aggregated_response": aggregated_response
        }
        
    def _write_log(self):
        """Write current query data to JSONL file."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.current_query_data, ensure_ascii=False) + "\n")
        
        # Reset for next query
        self.current_query_data = {}
        self.start_time = None
        
    def load_logs(self) -> List[Dict]:
        """
        Load all logs from current experiment.
        
        Returns:
            List of query result dictionaries
        """
        if not self.log_file.exists():
            return []
        
        logs = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line))
        return logs
    
    def calculate_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Calculate aggregate metrics across all queries.
        
        Returns:
            Dictionary with aggregate metrics
        """
        logs = self.load_logs()
        
        if not logs:
            return {}
        
        # Extract metrics
        accuracies = [log["response"]["is_correct"] for log in logs if log["response"].get("is_correct") is not None]
        precisions = [log["retrieval"]["precision"] for log in logs if log.get("retrieval", {}).get("precision") is not None]
        recalls = [log["retrieval"]["recall"] for log in logs if log.get("retrieval", {}).get("recall") is not None]
        f1_scores = [log["retrieval"]["f1_score"] for log in logs if log.get("retrieval", {}).get("f1_score") is not None]
        confident_wrongs = [log["response"]["confident_wrong"] for log in logs if log["response"].get("confident_wrong") is not None]
        response_times = [log["response"]["response_time_seconds"] for log in logs if log["response"].get("response_time_seconds") is not None]
        token_totals = [log["response"]["token_usage"]["total_tokens"] for log in logs if log["response"].get("token_usage", {}).get("total_tokens") is not None]
        
        return {
            "experiment_name": self.experiment_name,
            "total_queries": len(logs),
            "accuracy": sum(accuracies) / len(accuracies) if accuracies else None,
            "avg_precision": sum(precisions) / len(precisions) if precisions else None,
            "avg_recall": sum(recalls) / len(recalls) if recalls else None,
            "avg_f1_score": sum(f1_scores) / len(f1_scores) if f1_scores else None,
            "confident_wrong_rate": sum(confident_wrongs) / len(confident_wrongs) if confident_wrongs else None,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else None,
            "avg_token_usage": sum(token_totals) / len(token_totals) if token_totals else None,
            "total_tokens": sum(token_totals) if token_totals else None,
        }


# Example usage
if __name__ == "__main__":
    # Initialize logger
    logger = MetricsLogger(experiment_name="baseline_test")
    
    # Start query
    logger.start_query(
        query_id="Q001",
        query_text="Apa syarat membuat izin usaha UMKM?",
        ground_truth="Syarat membuat izin usaha UMKM meliputi KTP, NPWP, dan surat keterangan domisili usaha."
    )
    
    # Log retrieval (with ground truth chunk IDs for precision/recall)
    logger.log_retrieval(
        retrieved_chunks=[
            {"chunk_id": "chunk_123", "similarity": 0.89, "text": "Untuk membuat izin usaha UMKM..."},
            {"chunk_id": "chunk_456", "similarity": 0.85, "text": "Syarat perizinan meliputi..."},
            {"chunk_id": "chunk_789", "similarity": 0.72, "text": "Dokumen yang diperlukan..."}
        ],
        relevant_chunk_ids=["chunk_123", "chunk_456"]  # Ground truth
    )
    
    # Log response
    logger.log_response(
        response_text="Untuk membuat izin usaha UMKM, Anda memerlukan KTP, NPWP, dan surat domisili.",
        model_name="mistralai/mistral-small-3.2-24b-instruct",
        token_usage={"prompt_tokens": 850, "completion_tokens": 120, "total_tokens": 970},
        confidence_score=0.92,
        is_correct=True
    )
    
    # Calculate aggregate metrics
    metrics = logger.calculate_aggregate_metrics()
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
