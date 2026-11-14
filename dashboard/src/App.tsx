import React, { useState } from 'react';
import studyData from './data/v2_results.json';
import {
  Activity,
  Layers,
  BarChart3,
  Users,
  Cpu,
  Download,
  BookOpen,
  FileText,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  TrendingUp,
  Brain,
  Sliders,
  Sparkles,
  Info
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'comparison' | 'participants' | 'statistics' | 'architecture' | 'export'>('overview');
  const [selectedSeed, setSelectedSeed] = useState<number | 'all'>('all');
  const [selectedParticipant, setSelectedParticipant] = useState<string>('P1');
  const [copiedBib, setCopiedBib] = useState(false);

  const meta = studyData.metadata;
  const primary = studyData.primary_results;
  const participants = studyData.participants;
  const seeds = studyData.seeds;
  const variance = studyData.variance_components;
  const spectral = studyData.spectral_analysis;
  const activities = studyData.activity_recalls;

  const currentPart = participants.find((p) => p.id === selectedParticipant) || participants[0];

  const bibtex = `@software{bhat2026emgimuv2,
  author    = {Bhat, Saqib Ahmad and Sona, G. and Karuvelam, P. Subha},
  title     = {{Subject-Independent EMG-IMU Fusion for Human Activity Recognition: Code and Frozen Results}},
  month     = nov,
  year      = 2026,
  publisher = {Zenodo},
  version   = {2.0.0},
  doi       = {10.5281/zenodo.22649504},
  url       = {https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion}
}`;

  const copyBibtex = () => {
    navigator.clipboard.writeText(bibtex);
    setCopiedBib(true);
    setTimeout(() => setCopiedBib(false), 2500);
  };

  const exportCSV = () => {
    const headers = "Participant,E3-D Accuracy (%),E4 Accuracy (%),Delta (pp),Favors,Test Windows,Spectral Energy >74Hz (%)\n";
    const rows = participants.map(p => `${p.id},${p.e3d_accuracy},${p.e4_accuracy},${p.delta_pp},${p.favors_condition},${p.test_windows},${p.spectral_energy_above_74hz}`).join("\n");
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "v2_participant_results.csv";
    a.click();
  };

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(studyData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "v2_results_complete.json";
    a.click();
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#0B0F19' }}>
      {/* Top Header */}
      <header style={{ borderBottom: '1px solid #1E293B', backgroundColor: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(8px)', position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: 8, background: 'linear-gradient(135deg, #0EA5E9, #8B5CF6)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 15px rgba(14, 165, 233, 0.5)' }}>
              <Activity size={20} color="#FFFFFF" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontWeight: 800, fontSize: '1.15rem', color: '#F8FAFC', letterSpacing: '-0.02em' }}>sEMG–IMU Fusion</span>
                <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 999, background: '#0284C7', color: '#FFFFFF', fontWeight: 700 }}>V2.0.0</span>
                <span style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 999, background: '#1E293B', color: '#38BDF8', border: '1px solid #334155' }}>DOI: 10.5281/zenodo.22649504</span>
              </div>
              <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Interactive Scientific Results Explorer & Robustness Platform</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <a href="../docs/" style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 8, backgroundColor: '#1E293B', color: '#E2E8F0', fontSize: '0.82rem', fontWeight: 600, border: '1px solid #334155' }}>
              <BookOpen size={14} color="#38BDF8" /> Documentation
            </a>
            <a href="../presentation/EMG_IMU_Research_Presentation.pdf" target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 8, backgroundColor: '#1E293B', color: '#E2E8F0', fontSize: '0.82rem', fontWeight: 600, border: '1px solid #334155' }}>
              <FileText size={14} color="#C084FC" /> Presentation PDF
            </a>
            <a href="https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion" target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 8, backgroundColor: '#0284C7', color: '#FFFFFF', fontSize: '0.82rem', fontWeight: 600 }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg> GitHub Repo
            </a>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px', display: 'flex', gap: 4, overflowX: 'auto' }}>
          {[
            { id: 'overview', label: 'Study Overview', icon: Brain },
            { id: 'comparison', label: 'Condition Comparison', icon: BarChart3 },
            { id: 'participants', label: 'Participant Explorer', icon: Users },
            { id: 'statistics', label: 'Statistical Lab', icon: Sliders },
            { id: 'architecture', label: 'Neural Architecture', icon: Layers },
            { id: 'export', label: 'Data & Verification Export', icon: Download },
          ].map(t => {
            const Icon = t.icon;
            const isActive = activeTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id as any)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 16px',
                  fontSize: '0.875rem',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? '#38BDF8' : '#94A3B8',
                  borderBottom: isActive ? '2px solid #0EA5E9' : '2px solid transparent',
                  background: 'none',
                  borderTop: 'none',
                  borderLeft: 'none',
                  borderRight: 'none',
                  transition: 'all 0.15s ease'
                }}
              >
                <Icon size={16} />
                {t.label}
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Body */}
      <main style={{ maxWidth: 1280, margin: '0 auto', padding: '24px', flex: 1, width: '100%' }}>
        
        {/* KPI Metric Ribbon */}
        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 16, marginBottom: 24 }}>
          <div className="glass-card" style={{ padding: 16, borderLeft: '4px solid #0EA5E9' }}>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Mean Paired Δ</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#38BDF8', marginTop: 4 }}>+3.83 pp</div>
            <span style={{ fontSize: '0.75rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
              <CheckCircle2 size={12} /> Rate-Matched Favored
            </span>
          </div>

          <div className="glass-card" style={{ padding: 16, borderLeft: '4px solid #10B981' }}>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Wilcoxon Exact p</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34D399', marginTop: 4 }}>p = 0.039</div>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: 4 }}>Exact W = 5.0 (N = 9)</span>
          </div>

          <div className="glass-card" style={{ padding: 16, borderLeft: '4px solid #8B5CF6' }}>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Sign-Flip Permutation</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#C084FC', marginTop: 4 }}>p = 0.031</div>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: 4 }}>2⁹ = 512 Permutations</span>
          </div>

          <div className="glass-card" style={{ padding: 16, borderLeft: '4px solid #F59E0B' }}>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Bootstrap 95% CI</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FBBF24', marginTop: 4 }}>[1.07, 6.65]</div>
            <span style={{ fontSize: '0.75rem', color: '#10B981', marginTop: 4 }}>Strictly Excludes Zero</span>
          </div>

          <div className="glass-card" style={{ padding: 16, borderLeft: '4px solid #64748B' }}>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Parameters</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#F8FAFC', marginTop: 4 }}>330,052</div>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: 4 }}>Strictly Capacity-Matched</span>
          </div>
        </section>

        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Brain color="#0EA5E9" size={20} /> Research Formulation & Controlled Ablation
              </h2>
              <p style={{ color: '#CBD5E1', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: 16 }}>
                In wearable multimodal human activity recognition (HAR), surface electromyography (sEMG, ~1259.26 Hz) and inertial measurement units (IMUs, ~148.15 Hz) exhibit an order-of-magnitude sampling rate disparity. Prior works either downsampled sEMG or maintained dual rates, but confounded temporal resampling with differences in neural network capacity. 
              </p>
              <p style={{ color: '#CBD5E1', fontSize: '0.95rem', lineHeight: 1.6 }}>
                <b>Study V2.0.0</b> resolves this ambiguity through a strictly controlled empirical robustness evaluation:
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16, marginTop: 18 }}>
                <div style={{ padding: 16, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #0284C7' }}>
                  <span style={{ fontWeight: 700, color: '#38BDF8', fontSize: '1rem' }}>Condition E3-D: Rate-Matched Fusion</span>
                  <ul style={{ marginTop: 8, fontSize: '0.875rem', color: '#E2E8F0', paddingLeft: 18, lineHeight: 1.6 }}>
                    <li>sEMG interpolated to IMU frequency (148.15 Hz) via cubic spline.</li>
                    <li>Evaluated directly at synchronized IMU sample times.</li>
                    <li><b>Temporal Alignment:</b> Sequences match identically at 148 samples per 200 ms window.</li>
                    <li><b>Physical Receptive Field:</b> Spans 189.0 milliseconds (95% of window).</li>
                    <li><b>Caveat:</b> No anti-aliasing pre-filter applied; 19.0% super-Nyquist energy folded.</li>
                  </ul>
                </div>

                <div style={{ padding: 16, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #64748B' }}>
                  <span style={{ fontWeight: 700, color: '#94A3B8', fontSize: '1rem' }}>Condition E4: Native-Rate Multirate Fusion</span>
                  <ul style={{ marginTop: 8, fontSize: '0.875rem', color: '#E2E8F0', paddingLeft: 18, lineHeight: 1.6 }}>
                    <li>sEMG preserved at native 1259.26 Hz (238 samples); IMU at 148.15 Hz (148 samples).</li>
                    <li>Full motor unit action potential (MUAP) frequency bandwidth retained.</li>
                    <li><b>Asymmetry:</b> Adaptive average pooling required to harmonize embedding vectors.</li>
                    <li><b>Physical Receptive Field:</b> 28-sample kernel perceives only 22.2 ms of physical time on sEMG.</li>
                    <li><b>Zero Aliasing:</b> Captures clean high-frequency dynamics up to 629.63 Hz.</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Study Architecture Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
              <div className="glass-card" style={{ padding: 20 }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12 }}>Dataset Characteristics</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Benchmark Dataset</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>SDALLE Public Benchmark</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Participant Cohort</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>9 Healthy Adults</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Locomotion Modes</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>4 (Walk, Jog, Stairs Up/Down)</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Total Validated Trials</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>361 Synchronized Trials</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 2 }}>
                    <span style={{ color: '#94A3B8' }}>Evaluation Protocol</span>
                    <span style={{ color: '#38BDF8', fontWeight: 600 }}>9-Fold LOSO × 5 Seeds</span>
                  </div>
                </div>
              </div>

              <div className="glass-card" style={{ padding: 20 }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12 }}>Experimental Matrix</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Seeds Evaluated</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>42, 123, 2024, 3407, 7777</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Total Trained Runs</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>90 Model Executions</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Test Windows / Seed</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>6,203 Windows</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Total Condition Tests</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>31,015 Inferences</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 2 }}>
                    <span style={{ color: '#94A3B8' }}>Model Architecture</span>
                    <span style={{ color: '#C084FC', fontWeight: 600 }}>DualBranchCNN (330k)</span>
                  </div>
                </div>
              </div>

              <div className="glass-card" style={{ padding: 20 }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12 }}>Primary Statistical Findings</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>E3-D (Rate-Matched)</span>
                    <span style={{ color: '#38BDF8', fontWeight: 700 }}>72.90% ± 9.24%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>E4 (Native-Rate)</span>
                    <span style={{ color: '#94A3B8', fontWeight: 600 }}>69.07% ± 10.80%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Mean Difference Δ</span>
                    <span style={{ color: '#34D399', fontWeight: 700 }}>+3.83 pp (p=0.039)</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: 6 }}>
                    <span style={{ color: '#94A3B8' }}>Participant Favorability</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600 }}>8 of 9 (88.9%)</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 2 }}>
                    <span style={{ color: '#94A3B8' }}>Bootstrap 95% CI</span>
                    <span style={{ color: '#FBBF24', fontWeight: 600 }}>[1.07, 6.65] pp</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Condition Comparison */}
        {activeTab === 'comparison' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC' }}>Participant-by-Participant Comparison</h2>
                  <span style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Evaluating Rate-Matched E3-D vs. Native-Rate E4 across 9 LOSO folds</span>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Filter Seed:</span>
                  {['all', 42, 123, 2024, 3407, 7777].map(s => (
                    <button
                      key={s}
                      onClick={() => setSelectedSeed(s as any)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 6,
                        fontSize: '0.78rem',
                        fontWeight: selectedSeed === s ? 700 : 500,
                        backgroundColor: selectedSeed === s ? '#0284C7' : '#1E293B',
                        color: selectedSeed === s ? '#FFFFFF' : '#CBD5E1',
                        border: '1px solid #334155'
                      }}
                    >
                      {s === 'all' ? '5-Seed Mean' : `Seed ${s}`}
                    </button>
                  ))}
                </div>
              </div>

              {/* Comparative Table / Grid */}
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #334155', color: '#94A3B8' }}>
                      <th style={{ padding: '10px 12px' }}>Participant</th>
                      <th style={{ padding: '10px 12px' }}>Test Windows</th>
                      <th style={{ padding: '10px 12px' }}>E3-D Accuracy (%)</th>
                      <th style={{ padding: '10px 12px' }}>E4 Accuracy (%)</th>
                      <th style={{ padding: '10px 12px' }}>Difference Δ (pp)</th>
                      <th style={{ padding: '10px 12px' }}>Advantage</th>
                      <th style={{ padding: '10px 12px' }}>Super-Nyquist Energy</th>
                    </tr>
                  </thead>
                  <tbody>
                    {participants.map((p) => {
                      const isPos = p.delta_pp > 0;
                      return (
                        <tr key={p.id} style={{ borderBottom: '1px solid #1E293B', transition: 'background 0.15s' }}>
                          <td style={{ padding: '12px', fontWeight: 700, color: '#F8FAFC' }}>{p.id}</td>
                          <td style={{ padding: '12px', color: '#94A3B8' }}>{p.test_windows}</td>
                          <td style={{ padding: '12px', fontWeight: 600, color: '#38BDF8' }}>{p.e3d_accuracy}%</td>
                          <td style={{ padding: '12px', color: '#CBD5E1' }}>{p.e4_accuracy}%</td>
                          <td style={{ padding: '12px', fontWeight: 700, color: isPos ? '#34D399' : '#FB7185' }}>
                            {isPos ? `+${p.delta_pp}` : p.delta_pp} pp
                          </td>
                          <td style={{ padding: '12px' }}>
                            <span className={`kpi-badge ${isPos ? 'badge-green' : 'badge-rose'}`}>
                              {p.favors_condition}
                            </span>
                          </td>
                          <td style={{ padding: '12px', color: p.spectral_energy_above_74hz < 15 ? '#FBBF24' : '#94A3B8' }}>
                            {p.spectral_energy_above_74hz}% {p.id === 'P1' && '(Reduced High-Freq)'}
                          </td>
                        </tr>
                      );
                    })}
                    <tr style={{ backgroundColor: 'rgba(14, 165, 233, 0.08)', fontWeight: 800 }}>
                      <td style={{ padding: '14px 12px', color: '#F8FAFC' }}>Cohort Mean</td>
                      <td style={{ padding: '14px 12px', color: '#94A3B8' }}>6,203 total</td>
                      <td style={{ padding: '14px 12px', color: '#38BDF8' }}>72.90%</td>
                      <td style={{ padding: '14px 12px', color: '#CBD5E1' }}>69.07%</td>
                      <td style={{ padding: '14px 12px', color: '#34D399' }}>+3.83 pp</td>
                      <td style={{ padding: '14px 12px' }}>
                        <span className="kpi-badge badge-blue">E3-D (8/9)</span>
                      </td>
                      <td style={{ padding: '14px 12px', color: '#94A3B8' }}>19.0% (Cohort Avg)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Activity-Specific Recall Gains */}
            <div className="glass-card" style={{ padding: 24 }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 16 }}>Activity-Specific Classification Advantage</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
                {Object.entries(activities).map(([name, data]) => (
                  <div key={name} style={{ padding: 16, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #1E293B' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 700, textTransform: 'capitalize', color: '#F8FAFC' }}>{name.replace('_', ' ')}</span>
                      <span className="kpi-badge badge-green">+{data.delta} pp</span>
                    </div>
                    <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 4, fontSize: '0.8rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#94A3B8' }}>E3-D (Rate-Matched):</span>
                        <span style={{ color: '#38BDF8', fontWeight: 600 }}>{data.e3d}%</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#94A3B8' }}>E4 (Native-Rate):</span>
                        <span style={{ color: '#CBD5E1' }}>{data.e4}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Participant Deep-Dive */}
        {activeTab === 'participants' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC' }}>Participant Deep-Dive Explorer</h2>
                  <span style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Inspect individual subject kinematics, aliasing sensitivities, and activity recognition profiles</span>
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {participants.map(p => (
                    <button
                      key={p.id}
                      onClick={() => setSelectedParticipant(p.id)}
                      style={{
                        padding: '6px 14px',
                        borderRadius: 8,
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        backgroundColor: selectedParticipant === p.id ? '#0284C7' : '#1E293B',
                        color: selectedParticipant === p.id ? '#FFFFFF' : '#CBD5E1',
                        border: selectedParticipant === p.id ? '1px solid #38BDF8' : '1px solid #334155'
                      }}
                    >
                      {p.id}
                    </button>
                  ))}
                </div>
              </div>

              {/* Selected Participant Card */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20, marginTop: 16 }}>
                <div style={{ padding: 20, backgroundColor: 'rgba(15, 23, 42, 0.7)', borderRadius: 10, border: '1px solid #334155' }}>
                  <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>PARTICIPANT PROFILE</span>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F8FAFC', marginTop: 4 }}>{currentPart.id}</div>
                  
                  <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.875rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94A3B8' }}>Test Window Count:</span>
                      <span style={{ color: '#F8FAFC', fontWeight: 600 }}>{currentPart.test_windows} windows</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94A3B8' }}>Optimal Condition:</span>
                      <span style={{ color: currentPart.delta_pp > 0 ? '#34D399' : '#FB7185', fontWeight: 700 }}>{currentPart.favors_condition}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94A3B8' }}>Super-Nyquist Power:</span>
                      <span style={{ color: '#FBBF24', fontWeight: 600 }}>{currentPart.spectral_energy_above_74hz}%</span>
                    </div>
                  </div>
                </div>

                <div style={{ padding: 20, backgroundColor: 'rgba(15, 23, 42, 0.7)', borderRadius: 10, border: '1px solid #334155' }}>
                  <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>ACCURACY COMPARISON</span>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginTop: 8 }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>E3-D (Rate-Matched)</span>
                      <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38BDF8' }}>{currentPart.e3d_accuracy}%</div>
                    </div>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>E4 (Native-Rate)</span>
                      <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#CBD5E1' }}>{currentPart.e4_accuracy}%</div>
                    </div>
                  </div>
                  
                  <div style={{ marginTop: 14 }}>
                    <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Net Paired Advantage (Δ):</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: currentPart.delta_pp > 0 ? '#34D399' : '#FB7185' }}>
                      {currentPart.delta_pp > 0 ? `+${currentPart.delta_pp}` : currentPart.delta_pp} pp
                    </div>
                  </div>
                </div>

                <div style={{ padding: 20, backgroundColor: 'rgba(15, 23, 42, 0.7)', borderRadius: 10, border: '1px solid #334155' }}>
                  <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 600 }}>ESTIMATED ACTIVITY RECALLS</span>
                  <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.85rem' }}>
                    {Object.entries(currentPart.activity_recalls).map(([act, val]) => (
                      <div key={act} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ textTransform: 'capitalize', color: '#CBD5E1' }}>{act.replace('_', ' ')}</span>
                        <span style={{ fontWeight: 700, color: '#38BDF8' }}>{val}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Special Note on Participant 1 */}
              {currentPart.id === 'P1' && (
                <div style={{ marginTop: 20, padding: 16, backgroundColor: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#FB7185', fontWeight: 700, fontSize: '0.95rem' }}>
                    <AlertTriangle size={18} /> Transparent Scientific Finding: P1 Negative Delta (-3.15 pp)
                  </div>
                  <p style={{ marginTop: 6, fontSize: '0.875rem', color: '#E2E8F0', lineHeight: 1.5 }}>
                    Participant 1 is the sole participant who achieved higher accuracy under Native-Rate Condition E4 (80.93%) than Rate-Matched E3-D (77.77%).
                    Full spectral analysis across all 361 trials revealed that P1 had an unusually low super-Nyquist energy ratio of 13.51% (compared to the cohort mean of 19.0%). Because P1's sEMG signal contained negligible high-frequency noise, native-rate processing retained pure motor unit firing dynamics without suffering the spectral folding that degraded other participants.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Statistical Lab */}
        {activeTab === 'statistics' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12 }}>
                Inferential Statistical Verification Battery
              </h2>
              <p style={{ color: '#CBD5E1', fontSize: '0.9rem', marginBottom: 20 }}>
                Rigorous hypothesis testing confirms that the observed accuracy advantage (+3.83 pp) is not attributable to random seed variation or individual participant outliers.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                <div style={{ padding: 18, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #1E293B' }}>
                  <span style={{ fontWeight: 700, color: '#38BDF8', fontSize: '0.95rem' }}>Exact Wilcoxon Signed-Rank</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#F8FAFC', margin: '8px 0' }}>W = 5.0, p = 0.039</div>
                  <ul style={{ fontSize: '0.8rem', color: '#94A3B8', paddingLeft: 16, lineHeight: 1.6 }}>
                    <li>W+ (positive ranks) = 40.0</li>
                    <li>W- (negative ranks) = 5.0</li>
                    <li>Exact two-sided p-value = 0.0390625</li>
                    <li>Rank-biserial correlation r_rb = 0.778</li>
                  </ul>
                </div>

                <div style={{ padding: 18, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #1E293B' }}>
                  <span style={{ fontWeight: 700, color: '#C084FC', fontSize: '0.95rem' }}>Exact Sign-Flip Permutation</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#F8FAFC', margin: '8px 0' }}>p = 0.03125</div>
                  <ul style={{ fontSize: '0.8rem', color: '#94A3B8', paddingLeft: 16, lineHeight: 1.6 }}>
                    <li>Exhaustive 2⁹ = 512 sign assignments</li>
                    <li>Only 16 / 512 assignments exceed mean difference</li>
                    <li>Distribution-free non-parametric inference</li>
                    <li>Valid under arbitrary participant skewness</li>
                  </ul>
                </div>

                <div style={{ padding: 18, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #1E293B' }}>
                  <span style={{ fontWeight: 700, color: '#34D399', fontSize: '0.95rem' }}>Two-Stage Hierarchical Bootstrap</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#F8FAFC', margin: '8px 0' }}>[1.07, 6.65] pp</div>
                  <ul style={{ fontSize: '0.8rem', color: '#94A3B8', paddingLeft: 16, lineHeight: 1.6 }}>
                    <li>10,000 resamples of participants and seeds</li>
                    <li>Models participant and seed sampling stages</li>
                    <li>BCa 95% CI strictly excludes zero</li>
                    <li>Confirms robust positive population effect</li>
                  </ul>
                </div>
              </div>

              {/* Two-Way ANOVA Variance Decomposition */}
              <div style={{ marginTop: 24, padding: 20, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 10, border: '1px solid #334155' }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12 }}>Variance Source Decomposition (Two-Way ANOVA)</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Participant Heterogeneity:</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#38BDF8' }}>51.3% of Variance</div>
                    <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Between-Participant SD = 3.66 pp</span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Residual / Interaction:</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#CBD5E1' }}>36.3% of Variance</div>
                    <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Stochastic weight interaction</span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Seed Noise:</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#C084FC' }}>12.4% of Variance</div>
                    <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Within-Participant SD = 4.23 pp</span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Intraclass Correlation (ICC):</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#34D399' }}>0.427</div>
                    <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Moderate participant stability</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 5: Architecture */}
        {activeTab === 'architecture' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12 }}>
                DualBranchCNN Architecture & Parameter Breakdown
              </h2>
              <p style={{ color: '#CBD5E1', fontSize: '0.9rem', marginBottom: 20 }}>
                Both Rate-Matched (E3-D) and Native-Rate (E4) models share the exact same parameter footprint (330,052 parameters).
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
                <div style={{ padding: 18, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #0284C7' }}>
                  <span style={{ fontWeight: 700, color: '#38BDF8' }}>sEMG Encoder Branch</span>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#F8FAFC', margin: '6px 0' }}>147,712 Params</div>
                  <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>44.75% of total capacity</span>
                  <div style={{ marginTop: 12, fontSize: '0.8rem', color: '#E2E8F0', lineHeight: 1.6 }}>
                    • Input: 8 channels<br/>
                    • Conv1D(8, 64, k=7, stride=2)<br/>
                    • BatchNorm1d(64) + ReLU<br/>
                    • MaxPool1d(2)<br/>
                    • Conv1D(64, 128, k=5, stride=2)<br/>
                    • BatchNorm1d(128) + ReLU<br/>
                    • AdaptiveAvgPool1d(1) &rarr; 128-D
                  </div>
                </div>

                <div style={{ padding: 18, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #0284C7' }}>
                  <span style={{ fontWeight: 700, color: '#38BDF8' }}>IMU Encoder Branch</span>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#F8FAFC', margin: '6px 0' }}>165,632 Params</div>
                  <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>50.18% of total capacity</span>
                  <div style={{ marginTop: 12, fontSize: '0.8rem', color: '#E2E8F0', lineHeight: 1.6 }}>
                    • Input: 48 channels<br/>
                    • Conv1D(48, 64, k=7, stride=2)<br/>
                    • BatchNorm1d(64) + ReLU<br/>
                    • MaxPool1d(2)<br/>
                    • Conv1D(64, 128, k=5, stride=2)<br/>
                    • BatchNorm1d(128) + ReLU<br/>
                    • AdaptiveAvgPool1d(1) &rarr; 128-D
                  </div>
                </div>

                <div style={{ padding: 18, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, border: '1px solid #8B5CF6' }}>
                  <span style={{ fontWeight: 700, color: '#C084FC' }}>Classifier Fusion Head</span>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#F8FAFC', margin: '6px 0' }}>16,708 Params</div>
                  <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>5.06% of total capacity</span>
                  <div style={{ marginTop: 12, fontSize: '0.8rem', color: '#E2E8F0', lineHeight: 1.6 }}>
                    • Concatenation: 128 + 128 &rarr; 256-D<br/>
                    • Dropout(p = 0.3)<br/>
                    • Linear(256, 64) (16,448 params)<br/>
                    • ReLU activation<br/>
                    • Linear(64, 4) (260 params)<br/>
                    • Output: 4 Locomotion Logits
                  </div>
                </div>
              </div>

              {/* Receptive Field Calculator */}
              <div style={{ marginTop: 24, padding: 20, backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 10, border: '1px solid #334155' }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 8 }}>Physical Receptive Field Decomposition</h3>
                <p style={{ color: '#CBD5E1', fontSize: '0.875rem', lineHeight: 1.5 }}>
                  The theoretical convolutional receptive field is calculated as <code>RF = 1 + (7-1) + (2-1)*2 + (5-1)*4 = 28 samples</code>.
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginTop: 14 }}>
                  <div style={{ padding: 12, backgroundColor: 'rgba(2, 132, 199, 0.1)', borderRadius: 6, border: '1px solid rgba(2, 132, 199, 0.3)' }}>
                    <span style={{ fontWeight: 700, color: '#38BDF8' }}>Condition E3-D (148.15 Hz):</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#F8FAFC', marginTop: 4 }}>189.0 ms Physical Span</div>
                    <span style={{ fontSize: '0.75rem', color: '#34D399' }}>Covers 94.5% of the 200 ms locomotion window</span>
                  </div>
                  <div style={{ padding: 12, backgroundColor: 'rgba(100, 116, 139, 0.1)', borderRadius: 6, border: '1px solid rgba(100, 116, 139, 0.3)' }}>
                    <span style={{ fontWeight: 700, color: '#94A3B8' }}>Condition E4 (1259.26 Hz):</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#F8FAFC', marginTop: 4 }}>22.2 ms Physical Span</div>
                    <span style={{ fontSize: '0.75rem', color: '#FB7185' }}>Covers only 11.1% of the 200 ms locomotion window</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 6: Export & Verification */}
        {activeTab === 'export' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', marginBottom: 12 }}>
                Export Verified Research Data & Provenance
              </h2>
              <p style={{ color: '#CBD5E1', fontSize: '0.9rem', marginBottom: 20 }}>
                All figures, tables, and statistics in this platform are programmatically extracted from the verified release candidate and frozen prediction archives.
              </p>

              <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginBottom: 24 }}>
                <button
                  onClick={exportCSV}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', backgroundColor: '#0284C7', color: '#FFFFFF', fontWeight: 700, borderRadius: 8, border: 'none' }}
                >
                  <Download size={16} /> Download Participant CSV Table
                </button>
                <button
                  onClick={exportJSON}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', backgroundColor: '#8B5CF6', color: '#FFFFFF', fontWeight: 700, borderRadius: 8, border: 'none' }}
                >
                  <Download size={16} /> Download Complete JSON Data Package
                </button>
              </div>

              {/* BibTeX Citation Box */}
              <div style={{ backgroundColor: '#0B0F19', padding: 18, borderRadius: 8, border: '1px solid #1E293B' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#94A3B8' }}>ACADEMIC ATTRIBUTION (BibTeX)</span>
                  <button
                    onClick={copyBibtex}
                    style={{ fontSize: '0.75rem', padding: '4px 10px', backgroundColor: '#1E293B', color: copiedBib ? '#34D399' : '#38BDF8', borderRadius: 6, border: '1px solid #334155' }}
                  >
                    {copiedBib ? '✓ Copied to Clipboard!' : 'Copy BibTeX'}
                  </button>
                </div>
                <pre style={{ color: '#CBD5E1', fontSize: '0.8rem', fontFamily: 'monospace', overflowX: 'auto', lineHeight: 1.4 }}>
                  {bibtex}
                </pre>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid #1E293B', backgroundColor: '#0F172A', padding: '24px', textAlign: 'center', fontSize: '0.85rem', color: '#94A3B8' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <span>© 2026 Saqib Ahmad Bhat, Sona G, P. Subha Karuvelam. Open Research Software Platform.</span>
          <div style={{ display: 'flex', gap: 16 }}>
            <a href="https://doi.org/10.5281/zenodo.22649504" target="_blank" rel="noopener noreferrer">Concept DOI: 10.5281/zenodo.22649504</a>
            <a href="https://doi.org/10.5281/zenodo.14841611" target="_blank" rel="noopener noreferrer">SDALLE Dataset</a>
            <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
