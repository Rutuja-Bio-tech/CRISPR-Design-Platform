"""Gene sequence fetchers from various databases."""

import requests
from typing import Optional
from ..utils.config import Config


class SequenceFetcher:
    """Fetches gene sequences from external APIs."""

    def __init__(self, config: Config):
        self.config = config

    def fetch_uniprot_sequence(self, gene_id: str) -> Optional[str]:
        """Fetch FASTA sequence from UniProt."""
        url = f"https://www.uniprot.org/uniprot/{gene_id}.fasta"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                return ''.join(lines[1:])  # Skip header
            return None
        except Exception:
            return None

    def fetch_ncbi_sequence(self, gene_id: str) -> Optional[str]:
        """Fetch FASTA sequence from NCBI (placeholder)."""
        # Implement NCBI API call if needed
        return None

    def fetch_sequence(self, gene_id: str) -> Optional[str]:
        """Fetch sequence, trying UniProt first."""
        seq = self.fetch_uniprot_sequence(gene_id)
        if seq:
            return seq
        return self.fetch_ncbi_sequence(gene_id)