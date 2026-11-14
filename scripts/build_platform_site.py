#!/usr/bin/env python3
"""
Platform Site Builder for EMG-IMU Multimodal Research.
Orchestrates:
1. Documentation build (MkDocs Material -> site/docs/)
2. React Dashboard build (Vite + TypeScript -> site/explorer/)
3. Presentation distribution (site/presentation/)
4. Unified Master Portal Landing Page (site/index.html)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_cmd(cmd: list[str], cwd: Path | None = None) -> None:
    display = " ".join(cmd)
    print(f"==> Running: {display}")
    result = subprocess.run(cmd, cwd=cwd or REPO_ROOT)
    if result.returncode != 0:
        print(f"ERROR: Command failed with exit code {result.returncode}: {display}", file=sys.stderr)
        sys.exit(result.returncode)

def generate_landing_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Subject-Independent EMG–IMU Multimodal Sensor Fusion Platform</title>
  <meta name="description" content="Research software platform, interactive explorer, and comprehensive documentation for multimodal biosignal sensor fusion in human activity recognition.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0B1120;
      --card-bg: rgba(15, 23, 42, 0.75);
      --card-border: rgba(51, 65, 85, 0.6);
      --primary: #38BDF8;
      --primary-hover: #0284C7;
      --accent: #818CF8;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.6;
      background-image: 
        radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.1) 0px, transparent 50%),
        radial-gradient(at 50% 50%, rgba(14, 165, 233, 0.05) 0px, transparent 60%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .container {
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 24px;
      width: 100%;
    }

    /* Header Nav */
    header {
      padding: 24px 0;
      border-bottom: 1px solid rgba(51, 65, 85, 0.4);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(11, 17, 32, 0.85);
    }
    .nav-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text);
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }
    .brand-badge {
      background: linear-gradient(135deg, #0284C7, #6366F1);
      color: white;
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 9999px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .nav-links {
      display: flex;
      align-items: center;
      gap: 20px;
    }
    .nav-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.92rem;
      font-weight: 500;
      transition: color 0.2s;
    }
    .nav-link:hover { color: var(--primary); }
    .btn-github {
      background: #1E293B;
      color: #E2E8F0;
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid #334155;
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .btn-github:hover {
      background: #334155;
      border-color: #475569;
      color: white;
    }

    /* Hero */
    .hero {
      padding: 80px 0 60px;
      text-align: center;
    }
    .badge-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 16px;
      border-radius: 9999px;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--primary);
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 24px;
    }
    h1 {
      font-size: clamp(2.2rem, 5vw, 3.8rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.15;
      max-width: 980px;
      margin: 0 auto 20px;
      background: linear-gradient(180deg, #FFFFFF 0%, #CBD5E1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
      font-size: clamp(1.05rem, 2vw, 1.3rem);
      color: var(--text-muted);
      max-width: 820px;
      margin: 0 auto 40px;
      font-weight: 400;
      line-height: 1.6;
    }

    /* Stats Grid */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin: 0 auto 60px;
      max-width: 1040px;
    }
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 24px;
      text-align: center;
      backdrop-filter: blur(8px);
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    }
    .stat-val {
      font-size: 2.2rem;
      font-weight: 800;
      font-family: var(--font-mono);
      background: linear-gradient(135deg, #38BDF8, #818CF8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 6px;
    }
    .stat-label {
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      font-weight: 600;
    }

    /* Portals Section */
    .section-title {
      font-size: 1.8rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      text-align: center;
      margin-bottom: 12px;
    }
    .section-desc {
      color: var(--text-muted);
      text-align: center;
      max-width: 600px;
      margin: 0 auto 40px;
      font-size: 1rem;
    }
    .portals-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 24px;
      margin-bottom: 80px;
    }
    .portal-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 32px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s ease;
      text-decoration: none;
      color: inherit;
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(10px);
    }
    .portal-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #38BDF8, #818CF8);
      opacity: 0;
      transition: opacity 0.25s ease;
    }
    .portal-card:hover {
      transform: translateY(-4px);
      border-color: rgba(56, 189, 248, 0.5);
      box-shadow: 0 20px 35px -10px rgba(56, 189, 248, 0.15);
    }
    .portal-card:hover::before { opacity: 1; }
    .portal-header {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 16px;
    }
    .portal-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
    }
    .portal-title {
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: -0.01em;
    }
    .portal-desc {
      color: var(--text-muted);
      font-size: 0.94rem;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    .portal-footer {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--primary);
      font-size: 0.9rem;
      font-weight: 600;
    }

    /* Diagram Section */
    .preview-box {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 32px;
      margin-bottom: 80px;
      text-align: center;
    }
    .preview-box img {
      max-width: 100%;
      height: auto;
      border-radius: 8px;
    }

    /* Code Snippet */
    .code-box {
      background: #060913;
      border: 1px solid #1E293B;
      border-radius: 12px;
      padding: 20px;
      font-family: var(--font-mono);
      font-size: 0.9rem;
      color: #E2E8F0;
      text-align: left;
      overflow-x: auto;
      margin: 20px auto 0;
      max-width: 720px;
    }

    /* Footer */
    footer {
      margin-top: auto;
      padding: 40px 0;
      border-top: 1px solid rgba(51, 65, 85, 0.4);
      background: rgba(11, 17, 32, 0.95);
      text-align: center;
      color: var(--text-muted);
      font-size: 0.88rem;
    }
    .footer-links {
      display: flex;
      justify-content: center;
      gap: 24px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }
    .footer-links a {
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.2s;
    }
    .footer-links a:hover { color: var(--primary); }
  </style>
</head>
<body>

  <header>
    <div class="container nav-bar">
      <a href="./" class="brand">
        <span>EMG–IMU Fusion</span>
        <span class="brand-badge">v2.0.0</span>
      </a>
      <div class="nav-links">
        <a href="docs/" class="nav-link">Documentation</a>
        <a href="explorer/" class="nav-link">Interactive Explorer</a>
        <a href="presentation/EMG_IMU_Research_Presentation.pdf" target="_blank" class="nav-link">Presentation (PDF)</a>
        <a href="https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion" target="_blank" class="btn-github">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
          </svg>
          GitHub
        </a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <div class="badge-pill">
        <span>🔬 Scientific Research Platform & Open Benchmark</span>
      </div>
      <h1>Subject-Independent Multimodal EMG–IMU Sensor Fusion</h1>
      <p class="hero-subtitle">
        Investigating rate-harmonization versus native-rate processing in deep multimodal neural architectures for human activity recognition across 90 Leave-One-Subject-Out evaluations.
      </p>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-val">+3.83 pp</div>
          <div class="stat-label">Rate-Matching Gain (E3-D vs E4)</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">p = 0.039</div>
          <div class="stat-label">Wilcoxon Signed-Rank Test</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">[1.07, 6.65]</div>
          <div class="stat-label">Bootstrap 95% CI (pp)</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">8 / 9</div>
          <div class="stat-label">Subjects Favoring E3-D</div>
        </div>
      </div>
    </section>

    <section>
      <h2 class="section-title">Explore Research Platform Portals</h2>
      <p class="section-desc">Interactive dashboards, complete mathematical derivations, and executive slide presentations.</p>

      <div class="portals-grid">
        <a href="explorer/" class="portal-card">
          <div>
            <div class="portal-header">
              <div class="portal-icon" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8;">📊</div>
              <h3 class="portal-title">Results Explorer</h3>
            </div>
            <p class="portal-desc">
              Full interactive React dashboard. Inspect all 90 runs, filter by random seed, drill into individual participants, explore aliasing spectra, and export CSV/JSON data.
            </p>
          </div>
          <div class="portal-footer">
            <span>Launch Live Explorer</span>
            <span>&rarr;</span>
          </div>
        </a>

        <a href="docs/" class="portal-card">
          <div>
            <div class="portal-header">
              <div class="portal-icon" style="background: rgba(129, 140, 248, 0.15); color: #818CF8;">📖</div>
              <h3 class="portal-title">Documentation Hub</h3>
            </div>
            <p class="portal-desc">
              Comprehensive MkDocs Material documentation. In-depth coverage of neural architectures, receptive field derivations, SDALLE dataset protocols, and reproducible pipelines.
            </p>
          </div>
          <div class="portal-footer">
            <span>Read Documentation</span>
            <span>&rarr;</span>
          </div>
        </a>

        <a href="presentation/EMG_IMU_Research_Presentation.pdf" target="_blank" class="portal-card">
          <div>
            <div class="portal-header">
              <div class="portal-icon" style="background: rgba(192, 132, 252, 0.15); color: #C084FC;">📑</div>
              <h3 class="portal-title">Research Presentation</h3>
            </div>
            <p class="portal-desc">
              24-slide widescreen presentation deck in vector PDF and PowerPoint formats. Features publication-quality figures, statistical decompositions, and clinical takeaways.
            </p>
          </div>
          <div class="portal-footer">
            <span>Open Vector Presentation (PDF)</span>
            <span>&rarr;</span>
          </div>
        </a>
      </div>
    </section>

    <section class="preview-box">
      <h2 style="font-size: 1.5rem; margin-bottom: 8px;">Dual-Branch Neural Architecture</h2>
      <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 24px;">Synchronized 1.0-second sliding windows ingested through dedicated 1D convolutional backbones with late feature fusion.</p>
      <img src="docs/assets/diagrams/dual_branch_cnn_architecture.svg" alt="Architecture Diagram" />
    </section>

    <section class="preview-box">
      <h2 style="font-size: 1.5rem; margin-bottom: 8px;">Deterministic Verification in 60 Seconds</h2>
      <p style="color: var(--text-muted); font-size: 0.95rem;">Verify all published statistical results and neural architecture configurations instantly without GPU re-training:</p>
      <div class="code-box">
        <span style="color: #64748B;"># Clone repository and verify 90 evaluation runs</span><br>
        git clone https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion.git<br>
        cd subject-independent-emg-imu-fusion<br>
        python3 scripts/verify_release.py
      </div>
    </section>
  </main>

  <footer>
    <div class="container">
      <div class="footer-links">
        <a href="docs/">Documentation</a>
        <a href="explorer/">Interactive Explorer</a>
        <a href="presentation/EMG_IMU_Research_Presentation.pdf">Presentation Deck (PDF)</a>
        <a href="presentation/EMG_IMU_Research_Presentation.pptx">PowerPoint Deck (PPTX)</a>
        <a href="https://doi.org/10.5281/zenodo.22649504" target="_blank">Zenodo Archive</a>
        <a href="https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion" target="_blank">GitHub Repository</a>
      </div>
      <p style="margin-bottom: 6px;">
        &copy; 2025–2026 Saqib Ahmad Bhat, G. Sona, P. Subha Karuvelam. Open-source scientific release.
      </p>
      <p style="font-size: 0.8rem; color: #64748B;">
        Code licensed under MIT License. Documentation, figures, and presentation licensed under CC-BY 4.0.
      </p>
    </div>
  </footer>

</body>
</html>
"""

def main() -> None:
    print("=======================================================")
    print("  Building EMG-IMU Multimodal Platform Site Bundle     ")
    print("=======================================================")

    site_dir = REPO_ROOT / "site"
    if site_dir.exists():
        print(f"Cleaning previous build at {site_dir}...")
        shutil.rmtree(site_dir)
    site_dir.mkdir(parents=True, exist_ok=True)

    # 1. Build MkDocs
    print("\n--- Step 1: Building MkDocs Documentation ---")
    run_cmd([sys.executable, "-m", "mkdocs", "build", "-d", str(site_dir / "docs")])

    # 2. Build Dashboard
    print("\n--- Step 2: Building Interactive React Dashboard ---")
    dashboard_dir = REPO_ROOT / "dashboard"
    run_cmd(["npm", "run", "build"], cwd=dashboard_dir)
    dist_dir = dashboard_dir / "dist"
    shutil.copytree(dist_dir, site_dir / "explorer")
    print(f"Copied dashboard build from {dist_dir} to {site_dir / 'explorer'}")

    # 3. Copy Presentation assets
    print("\n--- Step 3: Copying Presentation & Figures ---")
    pres_dest = site_dir / "presentation"
    pres_dest.mkdir(parents=True, exist_ok=True)
    
    pres_pdf = REPO_ROOT / "presentation" / "EMG_IMU_Research_Presentation.pdf"
    if pres_pdf.exists():
        shutil.copy2(pres_pdf, pres_dest / "EMG_IMU_Research_Presentation.pdf")
        print(f"Copied presentation PDF ({pres_pdf.stat().st_size / 1e6:.2f} MB)")

    pres_pptx = REPO_ROOT / "presentation" / "EMG_IMU_Research_Presentation.pptx"
    if pres_pptx.exists():
        shutil.copy2(pres_pptx, pres_dest / "EMG_IMU_Research_Presentation.pptx")
        print(f"Copied presentation PPTX ({pres_pptx.stat().st_size / 1e6:.2f} MB)")

    figures_dir = REPO_ROOT / "presentation" / "figures"
    if figures_dir.exists():
        shutil.copytree(figures_dir, pres_dest / "figures", dirs_exist_ok=True)

    # 4. Generate Master Landing Page
    print("\n--- Step 4: Generating Master Landing Page ---")
    index_html = generate_landing_html()
    (site_dir / "index.html").write_text(index_html, encoding="utf-8")
    print(f"Master landing page generated at {site_dir / 'index.html'}")

    # 5. Add .nojekyll for GitHub Pages
    (site_dir / ".nojekyll").write_text("", encoding="utf-8")
    print("Added .nojekyll for GitHub Pages asset routing")

    print("\n=======================================================")
    print("  Site Bundle Build Complete Successfully!             ")
    print("=======================================================")

if __name__ == "__main__":
    main()
