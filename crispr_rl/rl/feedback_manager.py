"""Feedback management for RL retraining."""

import json
import os
from typing import List, Dict, Any
from datetime import datetime


class FeedbackManager:
    """Manages user feedback for RL model updates."""

    def __init__(self, feedback_file: str = "feedback_log.json"):
        self.feedback_file = feedback_file
        self.feedbacks: List[Dict[str, Any]] = []
        self.load_feedbacks()

    def load_feedbacks(self):
        """Load existing feedbacks."""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r') as f:
                self.feedbacks = json.load(f)

    def save_feedbacks(self):
        """Save feedbacks to file."""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedbacks, f, indent=2)

    def add_feedback(self, candidate_id: str, rating: float, notes: str = ""):
        """Add new feedback."""
        feedback = {
            "candidate_id": candidate_id,
            "rating": rating,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }
        self.feedbacks.append(feedback)
        self.save_feedbacks()

    def get_recent_feedbacks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent feedbacks for retraining."""
        return self.feedbacks[-limit:]

    def get_average_rating(self, candidate_id: str) -> float:
        """Get average rating for a candidate."""
        ratings = [f['rating'] for f in self.feedbacks if f['candidate_id'] == candidate_id]
        return sum(ratings) / len(ratings) if ratings else 0.0