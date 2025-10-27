"""Tests for scoring functions."""

import unittest
from ..scoring.scorer import GuideScorer
from ..utils.config import Config


class TestGuideScorer(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.scorer = GuideScorer(self.config)

    def test_on_target_scoring(self):
        features = {'gc_content': 50, 'thermodynamic': 5}
        score = self.scorer.score_on_target(features)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1)

    def test_off_target_scoring(self):
        features = {'gc_content': 50, 'context_weight': 0.8}
        penalty = self.scorer.score_off_target(features)
        self.assertGreaterEqual(penalty, 0)

    def test_composite_reward(self):
        on_target = 0.8
        off_target = 0.2
        coverage = 1.0
        reward = self.scorer.calculate_reward(on_target, off_target, coverage)
        expected = (0.5 * 0.8) - (0.3 * 0.2) + (0.2 * 1.0)
        self.assertAlmostEqual(reward, expected)

    def test_guide_scoring(self):
        features = {
            'gc_content': 60,
            'thermodynamic': 8,
            'context_weight': 0.9
        }
        scores = self.scorer.score_guide(features)
        self.assertIn('on_target_score', scores)
        self.assertIn('off_target_penalty', scores)
        self.assertIn('composite_score', scores)


if __name__ == '__main__':
    unittest.main()