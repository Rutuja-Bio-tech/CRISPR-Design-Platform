"""RL-based guide optimizer using contextual bandit."""

import random
from typing import List, Dict, Any
from ..utils.config import Config
from ..scoring.scorer import GuideScorer


class RLOptimizer:
    """Reinforcement learning optimizer for guide selection."""

    def __init__(self, config: Config, scorer: GuideScorer):
        self.config = config
        self.scorer = scorer
        self.epsilon = config.rl_params['epsilon']
        self.learning_rate = config.rl_params['learning_rate']
        self.guides_memory: Dict[str, float] = {}  # Guide ID -> average reward
        random.seed(config.seed)

    def _get_guide_id(self, guide: Dict[str, Any]) -> str:
        """Generate unique ID for guide."""
        return f"{guide['locus']}_{guide['guide_sequence']}"

    def select_action(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select guide using epsilon-greedy policy."""
        if random.random() < self.epsilon or not self.guides_memory:
            # Explore: random selection
            return random.choice(candidates)

        # Exploit: select highest average reward
        best_guide = None
        best_score = -float('inf')
        for guide in candidates:
            gid = self._get_guide_id(guide)
            score = self.guides_memory.get(gid, 0)
            if score > best_score:
                best_score = score
                best_guide = guide
        return best_guide or random.choice(candidates)

    def update_policy(self, guide: Dict[str, Any], reward: float):
        """Update policy with feedback."""
        gid = self._get_guide_id(guide)
        current = self.guides_memory.get(gid, 0)
        # Simple moving average update
        self.guides_memory[gid] = current + self.learning_rate * (reward - current)

    def optimize_guides(self, candidates: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """Optimize and rank guides."""
        selected = []
        for _ in range(min(top_k, len(candidates))):
            if not candidates:
                break
            guide = self.select_action(candidates)
            candidates.remove(guide)
            selected.append(guide)
        return selected