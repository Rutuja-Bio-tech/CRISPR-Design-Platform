"""PAM site detection and guide extraction."""

import re
from typing import List, Dict, Tuple
from ..utils.config import Config


class PAMScanner:
    """Scans sequences for PAM sites and extracts guide RNAs."""

    def __init__(self, config: Config):
        self.config = config
        self.pam_pattern = self._build_pam_pattern()

    def _build_pam_pattern(self) -> str:
        """Build regex pattern for PAM sequence."""
        pam = self.config.pam_sequence
        # Replace N with [ATCG]
        pam_regex = pam.replace('N', '[ATCG]')
        return pam_regex

    def find_pam_sites(self, sequence: str, start: int = 0, end: int = None) -> List[Dict]:
        """Find all PAM sites in the sequence within region."""
        if end is None:
            end = len(sequence)
        region = sequence[start:end]
        sites = []
        for match in re.finditer(self.pam_pattern, region):
            pam_start = start + match.start()
            guide_start = pam_start - self.config.guide_length
            if guide_start >= 0:
                guide_seq = sequence[guide_start:pam_start]
                pam_seq = sequence[pam_start:pam_start + len(self.config.pam_sequence)]
                sites.append({
                    'locus': pam_start,
                    'guide_sequence': guide_seq,
                    'pam_sequence': pam_seq,
                    'pam_start': pam_start,
                    'guide_start': guide_start,
                })
        return sites