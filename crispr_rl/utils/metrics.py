"""Metrics and telemetry utilities."""

import time
from typing import Dict, Any
from collections import defaultdict
import threading


class MetricsCollector:
    """Collects and reports system metrics."""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()

    def record_request(self, endpoint: str, duration: float, success: bool = True):
        """Record API request metrics."""
        with self.lock:
            self.metrics['requests'].append({
                'endpoint': endpoint,
                'duration': duration,
                'success': success,
                'timestamp': time.time()
            })

    def record_design(self, gene_id: str, num_sites: int, num_guides: int, duration: float):
        """Record guide design metrics."""
        with self.lock:
            self.metrics['designs'].append({
                'gene_id': gene_id,
                'num_sites': num_sites,
                'num_guides': num_guides,
                'duration': duration,
                'timestamp': time.time()
            })

    def record_feedback(self, rating: float):
        """Record user feedback metrics."""
        with self.lock:
            self.metrics['feedback'].append({
                'rating': rating,
                'timestamp': time.time()
            })

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self.lock:
            total_requests = len(self.metrics['requests'])
            successful_requests = sum(1 for r in self.metrics['requests'] if r['success'])
            avg_latency = sum(r['duration'] for r in self.metrics['requests']) / max(total_requests, 1)

            total_designs = len(self.metrics['designs'])
            avg_sites = sum(d['num_sites'] for d in self.metrics['designs']) / max(total_designs, 1)
            avg_guides = sum(d['num_guides'] for d in self.metrics['designs']) / max(total_designs, 1)

            total_feedback = len(self.metrics['feedback'])
            avg_rating = sum(f['rating'] for f in self.metrics['feedback']) / max(total_feedback, 1)

            return {
                "total_requests": total_requests,
                "success_rate": successful_requests / max(total_requests, 1),
                "avg_latency": avg_latency,
                "total_designs": total_designs,
                "avg_sites_per_design": avg_sites,
                "avg_guides_per_design": avg_guides,
                "total_feedback": total_feedback,
                "avg_rating": avg_rating,
                "rl_uplift": 0.15,  # Placeholder - would be calculated from A/B testing
            }


# Global metrics instance
metrics_collector = MetricsCollector()