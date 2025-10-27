# CRISPR Design Platform

A full-stack platform for CRISPR guide RNA design using reinforcement learning optimization.

## Features

- **Gene Sequence Fetching**: Retrieve FASTA sequences from UniProt/NCBI
- **PAM Site Detection**: Automatic identification of CRISPR PAM sites
- **Feature Extraction**: GC content, thermodynamic stability, contextual features
- **RL Optimization**: Contextual bandit for guide ranking improvement
- **User Feedback Loop**: Continuous learning from user ratings
- **Interactive Frontend**: Benchling-style sequence viewer and guide designer
- **API Endpoints**: RESTful API for integration

## Architecture

### Backend (FastAPI)
- `/crispr/sequence/{gene_id}` - Fetch gene sequences
- `/crispr/design` - Design and rank CRISPR guides
- `/crispr/feedback` - Submit user feedback for RL training
- `/crispr/config` - Adjust RL weights and parameters
- `/metrics` - Telemetry and performance metrics

### Frontend (Next.js + React)
- Gene ID input and sequence visualization
- Region selection for targeted design
- Interactive guide ranking table
- Star rating feedback system
- Export results (CSV/PDF)

### Core Package (crispr_rl)
```
crispr_rl/
├── data/          # Sequence fetchers
├── features/      # PAM scanning, feature extraction
├── scoring/       # On/off-target scoring
├── rl/            # RL optimizer and reranker
├── api/           # FastAPI handlers
├── utils/         # Config, logging
└── tests/         # Unit tests
```

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Package
```bash
cd crispr_rl
pip install -e .
```

## Usage

### Demo Script
```bash
python demo/run_crispr_design.py --gene_id BRCA1
```

### API Example
```python
import requests

# Fetch sequence
response = requests.get("http://localhost:8000/crispr/sequence/BRCA1")
sequence = response.json()["sequence"]

# Design guides
design = requests.post("http://localhost:8000/crispr/design", json={
    "gene_id": "BRCA1",
    "region_start": 0,
    "region_end": 1000
})
guides = design.json()["guides"]
```

## Configuration

Environment variables:
- `CRISPR_SEED`: Random seed for reproducibility
- `PAM_SEQUENCE`: PAM pattern (default: NGG)
- `GUIDE_LENGTH`: Guide RNA length (default: 20)
- `W1, W2, W3`: RL weights for on-target, off-target, coverage

## Testing

```bash
cd crispr_rl
pytest --cov=crispr_rl
```

## CI/CD

GitHub Actions pipeline includes:
- Multi-Python version testing
- Code coverage reporting
- Linting (flake8, black, isort)
- Package building

## Metrics

- **RL Uplift**: ≥15% improvement over baseline ranking
- **Latency**: <500ms per design request
- **Success Rate**: >95% for valid gene IDs
- **Test Coverage**: >90%

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure CI passes
5. Submit a pull request

## License

MIT License - see LICENSE file for details.