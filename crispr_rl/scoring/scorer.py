"""Scoring functions for on-target and off-target efficiency."""

from typing import Dict, Any
import random
from ..utils.config import Config


class GuideScorer:
    """Scores CRISPR guides for efficiency."""

    def __init__(self, config: Config):
        self.config = config
        random.seed(config.seed)

    def score_on_target(self, features: Dict[str, Any]) -> float:
        """Score on-target efficiency (placeholder model)."""
        # Simple model: higher GC and thermodynamic stability better
        gc_score = min(features.get('gc_content', 50) / 50, 1.0)
        thermo_score = min((features.get('thermodynamic', 0) + 10) / 20, 1.0)
        return (gc_score + thermo_score) / 2

    def score_off_target(self, features: Dict[str, Any]) -> float:
        """Score off-target penalty (lower is better)."""
        # Penalty for high GC (more specific) and position weight
        gc_penalty = features.get('gc_content', 50) / 100
        pos_weight = features.get('context_weight', 1.0)
        return gc_penalty * (1 - pos_weight)

    def calculate_reward(self, on_target: float, off_target: float, coverage: float = 1.0) -> float:
        """Calculate composite reward."""
        w = self.config.weights
        return w['on_target'] * on_target - w['off_target'] * off_target + w['coverage'] * coverage

    def score_guide(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Score a single guide."""
        on_target = self.score_on_target(features)
        off_target = self.score_off_target(features)
        reward = self.calculate_reward(on_target, off_target)
        return {
            'on_target_score': on_target,
            'off_target_penalty': off_target,
            'composite_score': reward,
        }