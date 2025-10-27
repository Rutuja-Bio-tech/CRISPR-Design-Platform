"""Feature extraction for guide RNAs."""

from typing import Dict, Any
import math


class FeatureExtractor:
    """Extracts features from guide sequences."""

    @staticmethod
    def calculate_gc_content(sequence: str) -> float:
        """Calculate GC content percentage."""
        if not sequence:
            return 0.0
        gc_count = sequence.count('G') + sequence.count('C')
        return (gc_count / len(sequence)) * 100

    @staticmethod
    def thermodynamic_stability(sequence: str) -> float:
        """Simple thermodynamic proxy (placeholder)."""
        # Placeholder: count AT vs GC pairs
        at_count = sequence.count('A') + sequence.count('T')
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count - at_count  # Higher GC more stable

    @staticmethod
    def contextual_weight(position: int, sequence_length: int) -> float:
        """Contextual weight based on position."""
        # Weight towards middle of sequence
        center = sequence_length / 2
        distance = abs(position - center)
        return 1 / (1 + distance / 10)

    def extract_features(self, guide_seq: str, pam_seq: str, locus: int, seq_len: int) -> Dict[str, Any]:
        """Extract all features for a guide."""
        return {
            'gc_content': self.calculate_gc_content(guide_seq),
            'thermodynamic': self.thermodynamic_stability(guide_seq),
            'context_weight': self.contextual_weight(locus, seq_len),
            'guide_length': len(guide_seq),
            'pam_gc': self.calculate_gc_content(pam_seq),
        }