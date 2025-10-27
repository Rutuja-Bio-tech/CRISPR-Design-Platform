#!/usr/bin/env python3
"""Demo script for CRISPR guide design."""

import argparse
import sys
import os

# Add crispr_rl to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from crispr_rl.utils.config import Config
from crispr_rl.data.fetchers import SequenceFetcher
from crispr_rl.features.pam_scanner import PAMScanner
from crispr_rl.features.extractor import FeatureExtractor
from crispr_rl.scoring.scorer import GuideScorer
from crispr_rl.rl.optimizer import RLOptimizer
from crispr_rl.rl.reranker import ParetoReranker


def main():
    parser = argparse.ArgumentParser(description="CRISPR Guide Design Demo")
    parser.add_argument("--gene_id", required=True, help="Gene ID to design guides for")
    parser.add_argument("--region_start", type=int, default=0, help="Region start position")
    parser.add_argument("--region_end", type=int, default=None, help="Region end position")
    parser.add_argument("--top_k", type=int, default=10, help="Number of top guides to return")
    args = parser.parse_args()

    # Initialize components
    config = Config()
    fetcher = SequenceFetcher(config)
    scanner = PAMScanner(config)
    extractor = FeatureExtractor()
    scorer = GuideScorer(config)
    optimizer = RLOptimizer(config, scorer)
    reranker = ParetoReranker()

    print(f"Designing CRISPR guides for gene: {args.gene_id}")

    # Fetch sequence
    sequence = fetcher.fetch_sequence(args.gene_id)
    if not sequence:
        print(f"Error: Could not fetch sequence for {args.gene_id}")
        return 1

    print(f"Sequence length: {len(sequence)} bp")

    # Scan PAM sites
    pam_sites = scanner.find_pam_sites(sequence, args.region_start, args.region_end)
    print(f"Found {len(pam_sites)} PAM sites")

    if not pam_sites:
        print("No PAM sites found in the specified region")
        return 1

    # Extract features and score
    guides = []
    for site in pam_sites:
        features = extractor.extract_features(
            site['guide_sequence'], site['pam_sequence'], site['locus'], len(sequence)
        )
        scores = scorer.score_guide(features)
        guide = {
            **site,
            **features,
            **scores,
            'candidate_id': f"{args.gene_id}_{site['locus']}"
        }
        guides.append(guide)

    # RL optimization
    optimized = optimizer.optimize_guides(guides.copy(), top_k=min(20, len(guides)))
    # Rerank for diversity
    final_guides = reranker.rerank(optimized, top_k=args.top_k)

    # Display results
    print(f"\nTop {len(final_guides)} CRISPR Guide Candidates:")
    print("-" * 80)
    print(f"{'Rank':<4} {'Guide Sequence':<20} {'PAM':<4} {'Locus':<6} {'GC%':<5} {'On-target':<10} {'Off-target':<10} {'Composite':<10}")
    print("-" * 80)

    for i, guide in enumerate(final_guides, 1):
        print(f"{i:<4} {guide['guide_sequence']:<20} {guide['pam_sequence']:<4} {guide['locus']:<6} "
              f"{guide['gc_content']:<5.1f} {guide['on_target_score']:<10.2f} "
              f"{guide['off_target_penalty']:<10.2f} {guide['composite_score']:<10.2f}")

    print(f"\nDeterministic seed: {config.seed}")
    print("Results are reproducible with the same seed and inputs.")

    return 0


if __name__ == "__main__":
    sys.exit(main())