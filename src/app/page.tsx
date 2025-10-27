'use client';

import { useState } from 'react';
import axios from 'axios';
import { Search, Dna, Star, Download, BarChart3, Target, Zap, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';

interface Guide {
  candidate_id: string;
  locus: number;
  guide_sequence: string;
  pam_sequence: string;
  gc_content: number;
  on_target_score: number;
  off_target_penalty: number;
  composite_score: number;
}

export default function Home() {
  const [geneId, setGeneId] = useState('');
  const [sequence, setSequence] = useState('');
  const [guides, setGuides] = useState<Guide[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState({ start: 0, end: 0 });

  const fetchSequence = async () => {
    if (!geneId) return;
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/crispr/sequence/${geneId}`);
      setSequence(response.data.sequence);
      setSelectedRegion({ start: 0, end: response.data.length });
    } catch (error) {
      console.error('Error fetching sequence:', error);
    }
    setLoading(false);
  };

  const designGuides = async () => {
    if (!geneId || !sequence) return;
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/crispr/design', {
        gene_id: geneId,
        region_start: selectedRegion.start,
        region_end: selectedRegion.end,
      });
      setGuides(response.data.guides);
    } catch (error) {
      console.error('Error designing guides:', error);
    }
    setLoading(false);
  };

  const submitFeedback = async (candidateId: string, rating: number) => {
    try {
      await axios.post('http://localhost:8000/crispr/feedback', {
        candidate_id: candidateId,
        rating,
      });
      alert('Feedback submitted! Model will improve.');
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const exportResults = () => {
    const csv = guides.map(g => `${g.candidate_id},${g.guide_sequence},${g.pam_sequence},${g.gc_content.toFixed(2)},${g.on_target_score.toFixed(2)},${g.off_target_penalty.toFixed(2)},${g.composite_score.toFixed(2)}`).join('\n');
    const blob = new Blob([`ID,Guide,PAM,GC%,On-target,Off-target,Composite\n${csv}`], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'crispr_guides.csv';
    a.click();
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-accent rounded-full">
              <Dna className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-primary">
              CRISPR Design Platform
            </h1>
          </div>
          <p className="text-lg text-secondary max-w-2xl mx-auto">
            Advanced CRISPR-Cas9 guide RNA design using reinforcement learning optimization
          </p>
        </div>

        {/* Metrics Dashboard */}
        {guides.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="scientific-metric">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-5 h-5 text-accent" />
                <h3>Total Guides</h3>
              </div>
              <p>{guides.length}</p>
            </div>
            <div className="scientific-metric">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-accent" />
                <h3>Avg On-target</h3>
              </div>
              <p>{(guides.reduce((sum, g) => sum + g.on_target_score, 0) / guides.length).toFixed(2)}</p>
            </div>
            <div className="scientific-metric">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-5 h-5 text-accent" />
                <h3>Avg GC Content</h3>
              </div>
              <p>{(guides.reduce((sum, g) => sum + g.gc_content, 0) / guides.length).toFixed(1)}%</p>
            </div>
            <div className="scientific-metric">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-5 h-5 text-accent" />
                <h3>Top Score</h3>
              </div>
              <p>{Math.max(...guides.map(g => g.composite_score)).toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* Gene ID Input */}
        <div className="scientific-card p-8 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-primary mb-2">
                Target Gene Identifier
              </label>
              <input
                type="text"
                placeholder="Enter UniProt ID (e.g., P50607)"
                value={geneId}
                onChange={(e) => setGeneId(e.target.value)}
                className="scientific-input w-full p-4 border rounded-lg text-lg"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={fetchSequence}
                disabled={loading}
                className="scientific-button px-8 py-4 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Search className="w-5 h-5 inline mr-2" />
                Fetch Sequence
              </button>
            </div>
          </div>
        </div>

        {/* Sequence Viewer */}
        {sequence && (
          <div className="scientific-card p-8 mb-8">
            <h2 className="text-2xl font-semibold text-primary mb-6 flex items-center gap-2">
              <Dna className="w-6 h-6 text-accent" />
              Target Sequence Analysis
            </h2>
            <div className="bg-muted p-6 rounded-lg font-mono text-sm overflow-x-auto max-h-48 mb-6">
              <div className="text-secondary mb-2">Sequence Length: {sequence.length} bp</div>
              <div className="text-foreground break-all">{sequence}</div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Region Start (bp)
                </label>
                <input
                  type="number"
                  value={selectedRegion.start}
                  onChange={(e) => setSelectedRegion(prev => ({ ...prev, start: parseInt(e.target.value) || 0 }))}
                  className="scientific-input w-full p-3 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Region End (bp)
                </label>
                <input
                  type="number"
                  value={selectedRegion.end}
                  onChange={(e) => setSelectedRegion(prev => ({ ...prev, end: parseInt(e.target.value) || sequence.length }))}
                  className="scientific-input w-full p-3 border rounded-lg"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={designGuides}
                  disabled={loading}
                  className="scientific-button w-full px-6 py-3 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Zap className="w-5 h-5 inline mr-2" />
                  Design Guides
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Score Visualization */}
        {guides.length > 0 && (
          <div className="scientific-card p-8 mb-8">
            <h2 className="text-2xl font-semibold text-primary mb-6 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-accent" />
              Guide Performance Analysis
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium text-primary mb-4">Score Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={guides.slice(0, 10).map((g, i) => ({ rank: i + 1, score: g.composite_score }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="rank" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div>
                <h3 className="text-lg font-medium text-primary mb-4">On-target vs Off-target</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart data={guides.map(g => ({ onTarget: g.on_target_score, offTarget: g.off_target_penalty }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="onTarget" name="On-target Score" />
                    <YAxis dataKey="offTarget" name="Off-target Penalty" />
                    <Tooltip />
                    <Scatter dataKey="offTarget" fill="#ef4444" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Guides Table */}
        {guides.length > 0 && (
          <div className="scientific-card p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-primary flex items-center gap-2">
                <Target className="w-6 h-6 text-accent" />
                Ranked Guide Candidates
              </h2>
              <div className="flex gap-3">
                <button
                  onClick={exportResults}
                  className="scientific-button px-6 py-3 rounded-lg font-semibold flex items-center gap-2"
                >
                  <Download className="w-5 h-5" />
                  Export CSV
                </button>
                <button
                  onClick={designGuides}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2"
                >
                  <TrendingUp className="w-5 h-5" />
                  Retrain Model
                </button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="scientific-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Guide Sequence</th>
                    <th>PAM</th>
                    <th>Locus (bp)</th>
                    <th>GC Content</th>
                    <th>On-target Score</th>
                    <th>Off-target Penalty</th>
                    <th>Composite Score</th>
                    <th>RL Feedback</th>
                  </tr>
                </thead>
                <tbody>
                  {guides.map((guide, index) => (
                    <tr key={guide.candidate_id}>
                      <td className="font-semibold text-accent">{index + 1}</td>
                      <td className="font-mono text-sm">{guide.guide_sequence}</td>
                      <td className="font-mono text-sm">{guide.pam_sequence}</td>
                      <td>{guide.locus.toLocaleString()}</td>
                      <td>{guide.gc_content.toFixed(1)}%</td>
                      <td>{guide.on_target_score.toFixed(3)}</td>
                      <td>{guide.off_target_penalty.toFixed(3)}</td>
                      <td className="font-semibold text-accent">{guide.composite_score.toFixed(3)}</td>
                      <td>
                        <div className="flex gap-1">
                          {[1, 2, 3, 4, 5].map(rating => (
                            <button
                              key={rating}
                              onClick={() => submitFeedback(guide.candidate_id, rating)}
                              className="text-yellow-400 hover:text-yellow-600 transition-colors"
                            >
                              <Star className="w-4 h-4" fill="currentColor" />
                            </button>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
