"""Pareto-aware reranker for guide diversity."""

from typing import List, Dict, Any
import numpy as np


class ParetoReranker:
    """Reranks guides for diversity using Pareto front."""

    @staticmethod
    def dominates(a: Dict[str, float], b: Dict[str, float]) -> bool:
        """Check if a dominates b (higher scores, lower penalties)."""
        a_on = a.get('on_target_score', 0)
        a_off = a.get('off_target_penalty', 0)
        b_on = b.get('on_target_score', 0)
        b_off = b.get('off_target_penalty', 0)
        return a_on >= b_on and a_off <= b_off and (a_on > b_on or a_off < b_off)

    def pareto_front(self, guides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract Pareto front."""
        front = []
        for guide in guides:
            dominated = False
            front[:] = [f for f in front if not self.dominates(guide, f)]
            if not any(self.dominates(f, guide) for f in front):
                front.append(guide)
        return front

    def rerank(self, guides: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """Rerank for diversity."""
        if len(guides) <= top_k:
            return guides
        front = self.pareto_front(guides)
        if len(front) >= top_k:
            return front[:top_k]
        # Add remaining guides sorted by composite score
        remaining = [g for g in guides if g not in front]
        remaining.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
        front.extend(remaining[:top_k - len(front)])
        return front