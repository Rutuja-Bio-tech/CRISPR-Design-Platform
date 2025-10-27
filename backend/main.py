"""FastAPI backend for CRISPR design platform."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import time

# Add crispr_rl to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from crispr_rl.utils.config import Config
from crispr_rl.data.fetchers import SequenceFetcher
from crispr_rl.features.pam_scanner import PAMScanner
from crispr_rl.features.extractor import FeatureExtractor
from crispr_rl.scoring.scorer import GuideScorer
from crispr_rl.rl.optimizer import RLOptimizer
from crispr_rl.rl.reranker import ParetoReranker
from crispr_rl.rl.feedback_manager import FeedbackManager
from crispr_rl.utils.metrics import metrics_collector

app = FastAPI(title="CRISPR Design API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
config = Config()
fetcher = SequenceFetcher(config)
scanner = PAMScanner(config)
extractor = FeatureExtractor()
scorer = GuideScorer(config)
optimizer = RLOptimizer(config, scorer)
reranker = ParetoReranker()
feedback_manager = FeedbackManager()

# Pydantic models
class DesignRequest(BaseModel):
    gene_id: str
    region_start: Optional[int] = 0
    region_end: Optional[int] = None

class FeedbackRequest(BaseModel):
    candidate_id: str
    rating: float  # 1-5
    notes: Optional[str] = None

class ConfigUpdate(BaseModel):
    weights: Optional[Dict[str, float]] = None
    rl_params: Optional[Dict[str, float]] = None

@app.get("/crispr/sequence/{gene_id}")
async def get_sequence(gene_id: str):
    """Fetch FASTA sequence for gene."""
    gene_id = gene_id.strip()
    print(f"Fetching sequence for gene_id: '{gene_id}'")
    start_time = time.time()
    try:
        sequence = fetcher.fetch_sequence(gene_id)
        print(f"Sequence fetched: {sequence is not None}, length: {len(sequence) if sequence else 0}")
        if not sequence:
            print("No sequence found, raising 404")
            metrics_collector.record_request("/crispr/sequence", time.time() - start_time, False)
            raise HTTPException(status_code=404, detail="Gene sequence not found")
        duration = time.time() - start_time
        metrics_collector.record_request("/crispr/sequence", duration, True)
        return {"gene_id": gene_id, "sequence": sequence, "length": len(sequence)}
    except HTTPException:
        raise  # Re-raise HTTPExceptions (like 404) without wrapping
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        duration = time.time() - start_time
        metrics_collector.record_request("/crispr/sequence", duration, False)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crispr/design")
async def design_guides(request: DesignRequest):
    """Design CRISPR guides for gene region."""
    start_time = time.time()
    try:
        print(f"Starting guide design for gene {request.gene_id}")
        sequence = fetcher.fetch_sequence(request.gene_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Gene sequence not found")
        print(f"Fetched sequence of length {len(sequence)}")

        # Scan PAM sites
        pam_sites = scanner.find_pam_sites(sequence, request.region_start, request.region_end)
        print(f"Found {len(pam_sites)} PAM sites")

        # Extract features and score
        guides = []
        for i, site in enumerate(pam_sites[:5]):  # Limit for debugging
            print(f"Processing site {i+1}/{len(pam_sites)} at locus {site['locus']}")
            features = extractor.extract_features(
                site['guide_sequence'], site['pam_sequence'], site['locus'], len(sequence)
            )
            scores = scorer.score_guide(features)
            guide = {
                **site,
                **features,
                **scores,
                'candidate_id': f"{request.gene_id}_{site['locus']}"
            }
            guides.append(guide)

        print(f"Extracted features for {len(guides)} guides")

        # RL optimization
        optimized = optimizer.optimize_guides(guides.copy(), top_k=min(20, len(guides)))
        print(f"Optimized to {len(optimized)} guides")

        # Rerank for diversity
        final_guides = reranker.rerank(optimized, top_k=min(10, len(optimized)))
        print(f"Final guides: {len(final_guides)}")

        duration = time.time() - start_time
        metrics_collector.record_design(request.gene_id, len(pam_sites), len(final_guides), duration)
        metrics_collector.record_request("/crispr/design", duration, True)

        return {
            "gene_id": request.gene_id,
            "region": {"start": request.region_start, "end": request.region_end or len(sequence)},
            "total_sites": len(pam_sites),
            "guides": final_guides
        }
    except Exception as e:
        import traceback
        print(f"Error in design_guides: {str(e)}")
        print(traceback.format_exc())
        duration = time.time() - start_time
        metrics_collector.record_request("/crispr/design", duration, False)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crispr/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for RL learning."""
    feedback_manager.add_feedback(request.candidate_id, request.rating, request.notes)
    metrics_collector.record_feedback(request.rating)
    # Update RL policy with feedback
    dummy_guide = {'locus': 0, 'guide_sequence': 'dummy'}
    optimizer.update_policy(dummy_guide, request.rating / 5.0)  # Normalize to 0-1
    return {"status": "feedback_received"}

@app.get("/crispr/config")
async def get_config():
    """Get current configuration."""
    return config.to_dict()

@app.post("/crispr/config")
async def update_config(request: ConfigUpdate):
    """Update configuration."""
    if request.weights:
        config.weights.update(request.weights)
    if request.rl_params:
        config.rl_params.update(request.rl_params)
    return config.to_dict()

@app.get("/metrics")
async def get_metrics():
    """Get telemetry metrics."""
    return metrics_collector.get_summary()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)