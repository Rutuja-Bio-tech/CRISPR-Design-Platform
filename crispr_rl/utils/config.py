"""Configuration utilities."""

import os
from typing import Dict, Any


class Config:
    """Configuration class for CRISPR RL."""

    def __init__(self):
        self.seed = int(os.getenv("CRISPR_SEED", "42"))
        self.pam_sequence = os.getenv("PAM_SEQUENCE", "NGG")
        self.guide_length = int(os.getenv("GUIDE_LENGTH", "20"))
        self.weights = {
            "on_target": float(os.getenv("W1", "0.5")),
            "off_target": float(os.getenv("W2", "0.3")),
            "coverage": float(os.getenv("W3", "0.2")),
        }
        self.rl_params = {
            "epsilon": float(os.getenv("RL_EPSILON", "0.1")),
            "learning_rate": float(os.getenv("RL_LR", "0.01")),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "seed": self.seed,
            "pam_sequence": self.pam_sequence,
            "guide_length": self.guide_length,
            "weights": self.weights,
            "rl_params": self.rl_params,
        }