"""Tests for feature extraction."""

import unittest
from ..features.extractor import FeatureExtractor
from ..features.pam_scanner import PAMScanner
from ..utils.config import Config


class TestFeatureExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = FeatureExtractor()
        self.config = Config()
        self.scanner = PAMScanner(self.config)

    def test_gc_content(self):
        seq = "ATCGATCG"
        gc = self.extractor.calculate_gc_content(seq)
        self.assertAlmostEqual(gc, 50.0)

    def test_pam_scanning(self):
        sequence = "ATCGATCGNGGATCG"
        sites = self.scanner.find_pam_sites(sequence)
        self.assertGreater(len(sites), 0)
        self.assertEqual(sites[0]['pam_sequence'], 'NGG')

    def test_feature_extraction(self):
        guide_seq = "ATCGATCGATCGATCG"
        pam_seq = "NGG"
        features = self.extractor.extract_features(guide_seq, pam_seq, 100, 1000)
        self.assertIn('gc_content', features)
        self.assertIn('thermodynamic', features)


if __name__ == '__main__':
    unittest.main()