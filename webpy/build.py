#!/usr/bin/env python3
"""Generate the standalone DSV WebAssembly playground."""
import argparse
import base64
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODE_DIR = os.path.join(REPO_ROOT, "dsv", "code")

if not os.path.isdir(CODE_DIR):
    raise FileNotFoundError(f"Python source directory not found: {CODE_DIR}")

# Collect all 44 python scripts
scripts_data = {}
for root, dirs, files in os.walk(CODE_DIR):
    dirs.sort()
    for f in sorted(files):
        if f.endswith(".py"):
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, CODE_DIR)
            with open(full_path, "r", encoding="utf-8") as fp:
                scripts_data[rel_path] = fp.read()

print(f"Loaded {len(scripts_data)} scripts.")

# Lectures categories mapping
LECTURE_MAP = [
    ("Vorlesung 01: Einführung & Dynamik", [
        ("buddhabrot.py", "Buddhabrot-Fraktal (Komplexe Zahlen & Dynamik)"),
        ("mandelbrot.py", "Mandelbrot-Menge (Diskrete Iteration)"),
        ("complex_exp.py", "Harmonische Exponentialschwingung")
    ]),
    ("Vorlesung 02: Harmonische Signale & Abtastung", [
        ("cont_harms.py", "Kontinuierliche Schwingungen & Phasoren"),
        ("disc_harms.py", "Diskrete Schwingungen & Periodizität"),
        ("disc_harms_comp.py", "Harmonische Trajektorien auf Einheitskreis"),
        ("aliasing.py", "Aliasing im Zeitbereich bei Unterabtastung")
    ]),
    ("Vorlesung 03: Samplingtheorem & Rekonstruktion", [
        ("sampling_theorem.py", "Dirac-Kamm & Sinc-Rekonstruktion"),
        ("fourier_trafo.py", "CFT des Rechteckpulses (Sinc-Spektrum)")
    ]),
    ("Vorlesung 04: Diskrete Signale & Systeme", [
        ("even_odd.py", "Gerade/Ungerade Signalzerlegung"),
        ("accumulator.py", "Diskreter Akkumulator (Gedächtnis)"),
        ("complex_exp.py", "Diskrete komplexe Exponentialfolge")
    ]),
    ("Vorlesung 05: LTI-Systeme & Differenzengleichungen", [
        ("moving_average.py", "Moving Average Glättungsfilter"),
        ("ramp_ma.py", "Kaskadierte Moving Averages & Rampe"),
        ("cumulative_sum.py", "Kumulatives Mittel (Rekursiv vs. Direkt)"),
        ("exp_mean.py", "Exponentielles Mittel (1-Pol-IIR)"),
        ("square_root.py", "Newton-Wurzelberechnung als LCCDE")
    ]),
    ("Vorlesung 06: Die z-Transformation", [
        ("dtft_z.py", "3D-Relief der z-Transformation & Einheitskreis")
    ]),
    ("Vorlesung 07: Fourier-Transformationen (CFT & DTFT)", [
        ("fourier_series.py", "Fourier-Reihe & Gibbs-Phänomen"),
        ("period_psd.py", "Leistungsdichtespektrum (PSD)"),
        ("dtft.py", "DTFT des diskreten Sinc-Signals")
    ]),
    ("Vorlesung 08: Diskrete Fourier-Transformation (DFT)", [
        ("dft_1.py", "DFT: Matrix- vs. Schleifenberechnung"),
        ("nyquist_seq.py", "DC- vs. Nyquist-Sequenz im DFT-Gitter"),
        ("dft_conv.py", "Schnelle Faltung im Frequenzbereich")
    ]),
    ("Vorlesung 09: Zeit-Frequenz-Analyse (STFT)", [
        ("stft_win.py", "Fensterfunktionen & Spectral Leakage"),
        ("stft_length.py", "Einfluss der Fensterbreite W"),
        ("stft_harm.py", "Spektrogramm harmonischer Töne"),
        ("stft_zp.py", "Zero-Padding in STFT-Fensterblöcken"),
        ("stft_bass.py", "Pitch Tracking einer Bassgitarre")
    ]),
    ("Vorlesung 11: Korrelation & Radar", [
        ("radar1.py", "Radar-Signale & Autokorrelation"),
        ("mlbs.py", "MLBS-Erzeugung via LFSR"),
        ("radar2.py", "Pulskompression & Mehrzielradar")
    ]),
    ("Vorlesung 12: Stochastische Signale & Stationarität", [
        ("random/discrete.py", "Diskrete Zufallsvariablen & Dichte"),
        ("random/normal1.py", "Normalverteilung (Histogramm vs. Gauß)"),
        ("random/signal1.py", "Realisierungen stochastischer Prozesse"),
        ("random/signal2.py", "Scharmittel vs. Zeitmittel"),
        ("random/signal3.py", "Stationarität (WSS) & AKF-Schätzung")
    ]),
    ("Vorlesung 13: Quantisierung & Parameterschätzung", [
        ("random/quantization1.py", "Quantisierungskennlinie & Fehlersignal"),
        ("random/quantization2.py", "Quantisierungsrauschen & Area Sampling"),
        ("random/quantization3.py", "Widrow-Theorem: Dichterekonstruktion"),
        ("random/paramest1.py", "Parameterschätzung normalverteilter Signale")
    ]),
    ("Vorlesung 14: Moderne Abtasttheorie & B-Splines", [
        ("bsplines_eval.py", "Auswertung kubischer B-Splines"),
        ("bsplines_coeffs.py", "Unser-Algorithmus (IIR-Rekursionsfilter)")
    ])
]

missing_scripts = sorted({
    script_file
    for _, items in LECTURE_MAP
    for script_file, _ in items
    if script_file not in scripts_data
})
if missing_scripts:
    raise FileNotFoundError(
        "Lecture catalog references missing scripts: " + ", ".join(missing_scripts)
    )

# Generate select HTML options
options_html = []
for group_name, items in LECTURE_MAP:
    options_html.append(f'        <optgroup label="{group_name}">')
    for script_file, desc in items:
        options_html.append(f'          <option value="{script_file}">{desc} ({script_file})</option>')
    options_html.append('        </optgroup>')
options_str = "\n".join(options_html)

scripts_json_str = json.dumps(scripts_data)

# Embed binary data files (WAV) as base64 so Pyodide can write them into its virtual FS.
# stft_bass.py uses a relative ../data path; the web UI also exposes the files at /data.
DATA_DIR = os.path.join(REPO_ROOT, "dsv", "data")
data_files = {}
for fname in ["g_maj.wav", "g_bend.wav"]:
    fpath = os.path.join(DATA_DIR, fname)
    if not os.path.isfile(fpath):
        raise FileNotFoundError(f"Required data file not found: {fpath}")
    with open(fpath, "rb") as fp:
        data_files[fname] = base64.b64encode(fp.read()).decode("ascii")
    print(f"Embedded {fname} ({os.path.getsize(fpath):,} bytes -> {len(data_files[fname]):,} b64 chars)")

data_files_json_str = json.dumps(data_files)

# HTML template using placeholders rather than f-string to prevent brace escaping bugs
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DSV Python Playground | TU Ilmenau (EMS)</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- FontAwesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  
  <!-- CodeMirror CSS -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/dracula.min.css">
  
  <!-- Pyodide WASM -->
  <script src="https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js"></script>

  <style>
    :root {
      --bg-dark: #1b2729;
      --bg-header: #23373B;
      --bg-surface: #2b3e42;
      --bg-editor: #282a36;
      --accent: #FF5D00;
      --accent-hover: #ff7524;
      --text-main: #f0f4f5;
      --text-sub: #b2c2c5;
      --border-color: #3b5055;
      --success: #10b981;
      --warning: #f59e0b;
      --error: #ef4444;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', sans-serif;
      background-color: var(--bg-dark);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* Header */
    header {
      background-color: var(--bg-header);
      border-bottom: 2px solid var(--accent);
      padding: 8px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      z-index: 10;
    }

    .logo-area {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-title {
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .logo-title span {
      color: var(--accent);
    }

    .logo-badge {
      font-size: 0.72rem;
      background: var(--bg-surface);
      color: var(--text-sub);
      padding: 2px 8px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
      font-weight: 500;
    }

    .controls {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .demo-select {
      background-color: var(--bg-surface);
      color: var(--text-main);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 6px 12px;
      font-size: 0.85rem;
      font-family: inherit;
      outline: none;
      cursor: pointer;
      max-width: 320px;
      transition: border-color 0.2s;
    }

    .demo-select:focus {
      border-color: var(--accent);
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      border: none;
      transition: all 0.2s ease;
      text-decoration: none;
      user-select: none;
    }

    .btn-run {
      background-color: var(--accent);
      color: #ffffff;
    }

    .btn-run:hover:not(:disabled) {
      background-color: var(--accent-hover);
      transform: translateY(-1px);
    }

    .btn-run:active:not(:disabled) {
      transform: translateY(0);
    }

    .btn-run:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-secondary {
      background-color: var(--bg-surface);
      color: var(--text-main);
      border: 1px solid var(--border-color);
    }

    .btn-secondary:hover {
      background-color: #354c51;
      border-color: #4b666c;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 500;
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--border-color);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--warning);
      animation: pulse 1.5s infinite;
    }

    .status-dot.ready {
      background-color: var(--success);
      animation: none;
    }

    .status-dot.running {
      background-color: var(--accent);
      animation: pulse 0.8s infinite;
    }

    .status-dot.error {
      background-color: var(--error);
      animation: none;
    }

    @keyframes pulse {
      from { transform: scale(0.9); opacity: 0.7; }
      to { transform: scale(1.3); opacity: 1; }
    }

    /* Main Container */
    main.workspace {
      display: flex;
      flex: 1;
      overflow: hidden;
      height: calc(100vh - 58px);
    }

    /* Left: Editor Pane */
    .pane-editor {
      flex: 1;
      display: flex;
      flex-direction: column;
      border-right: 2px solid var(--border-color);
      min-width: 320px;
      background: var(--bg-editor);
    }

    .pane-header {
      background: var(--bg-header);
      padding: 8px 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-sub);
      border-bottom: 1px solid var(--border-color);
    }

    .pane-header .file-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-main);
    }

    .pane-header .file-info i {
      color: var(--accent);
    }

    .editor-container {
      flex: 1;
      overflow: hidden;
      position: relative;
    }

    .CodeMirror {
      height: 100% !important;
      font-family: 'Fira Code', monospace;
      font-size: 13.5px;
      line-height: 1.5;
    }

    /* Right: Output Pane */
    .pane-output {
      flex: 1.1;
      display: flex;
      flex-direction: column;
      background: #141f21;
      overflow: hidden;
      position: relative;
    }

    .output-tabs {
      display: flex;
      background: var(--bg-header);
      border-bottom: 1px solid var(--border-color);
    }

    .output-tab {
      padding: 8px 18px;
      font-size: 0.83rem;
      font-weight: 600;
      color: var(--text-sub);
      background: none;
      border: none;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .output-tab.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
      background: rgba(255, 93, 0, 0.08);
    }

    .run-indicator {
      display: none;
      position: absolute;
      inset: 0;
      z-index: 20;
      align-items: center;
      justify-content: center;
      background: rgba(20, 31, 33, 0.72);
      backdrop-filter: blur(2px);
    }

    .run-indicator.is-running {
      display: flex;
    }

    .run-indicator-card {
      min-width: 210px;
      padding: 24px 30px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      color: var(--accent);
      background: var(--bg-header);
      border: 1px solid var(--accent);
      border-radius: 12px;
      box-shadow: 0 10px 35px rgba(0, 0, 0, 0.5), 0 0 24px rgba(255, 93, 0, 0.18);
      font-size: 0.9rem;
      font-weight: 600;
      animation: running-card-pulse 1.2s ease-in-out infinite alternate;
    }

    .run-indicator-spinner {
      width: 42px;
      height: 42px;
      padding: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid rgba(255, 93, 0, 0.22);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: running-spin 0.8s linear infinite;
    }

    .run-indicator-bars {
      height: 16px;
      display: flex;
      align-items: center;
      gap: 2px;
    }

    .run-indicator-bars span {
      width: 3px;
      height: 5px;
      border-radius: 2px;
      background: currentColor;
      animation: running-wave 0.8s ease-in-out infinite alternate;
    }

    .run-indicator-bars span:nth-child(2) { animation-delay: -0.6s; }
    .run-indicator-bars span:nth-child(3) { animation-delay: -0.4s; }
    .run-indicator-bars span:nth-child(4) { animation-delay: -0.2s; }

    @keyframes running-wave {
      from { height: 4px; opacity: 0.55; }
      to { height: 16px; opacity: 1; }
    }

    @keyframes running-spin {
      to { transform: rotate(360deg); }
    }

    @keyframes running-card-pulse {
      from { transform: scale(0.98); }
      to { transform: scale(1.02); }
    }

    @media (prefers-reduced-motion: reduce) {
      .run-indicator-bars span,
      .run-indicator-spinner,
      .run-indicator-card {
        animation: none;
      }
      .run-indicator-bars span {
        height: 8px;
      }
    }

    .output-content {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    /* Plots Container */
    #plot-container {
      display: flex;
      flex-direction: column;
      gap: 20px;
      align-items: center;
      justify-content: flex-start;
      width: 100%;
      min-height: 200px;
    }

    /* Pyodide Matplotlib Figure Card Styling */
    #plot-container > div {
      background: #ffffff !important;
      color: #1e293b !important;
      border-radius: 8px !important;
      padding: 12px 14px 16px 14px !important;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
      max-width: 100% !important;
      box-sizing: border-box !important;
      overflow-x: auto;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    #plot-container canvas {
      max-width: 100% !important;
      height: auto !important;
      display: block;
      border-radius: 4px;
    }

    button.matplotlib-toolbar-button {
      font-size: 11.5px !important;
      padding: 4px 10px !important;
      margin: 2px !important;
      border-radius: 4px !important;
      cursor: pointer;
    }

    .empty-state {
      color: var(--text-sub);
      text-align: center;
      padding: 40px 20px;
      font-size: 0.9rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }

    .empty-state i {
      font-size: 2.2rem;
      opacity: 0.5;
    }

    /* Terminal Output */
    #terminal-container {
      background: #0d1516;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 12px 14px;
      font-family: 'Fira Code', monospace;
      font-size: 0.83rem;
      color: #38bdf8;
      min-height: 120px;
      max-height: 260px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }

    .terminal-err {
      color: #f87171 !important;
    }

    .terminal-info {
      color: var(--text-sub) !important;
      font-style: italic;
    }

    /* Responsive */
    @media (max-width: 900px) {
      main.workspace {
        flex-direction: column;
        height: auto;
        overflow-y: auto;
      }
      .pane-editor, .pane-output {
        height: 50vh;
      }
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <div class="logo-area">
      <div class="logo-title">
        <i class="fa-solid fa-wave-square" style="color: var(--accent);"></i>
        DSV <span>Playground</span>
      </div>
      <div class="logo-badge">TU Ilmenau • EMS</div>
    </div>

    <div class="controls">
      <select id="demo-select" class="demo-select" title="Vorlesungs-Demo wählen">
__DEMO_OPTIONS__
      </select>

      <button id="btn-run" class="btn btn-run" title="Skript ausführen (Strg + Enter)">
        <i class="fa-solid fa-play"></i>
        <span>Ausführen</span>
      </button>

      <button id="btn-reset" class="btn btn-secondary" title="Code auf Originalzustand zurücksetzen">
        <i class="fa-solid fa-rotate-left"></i>
        <span>Reset</span>
      </button>

      <button id="btn-share" class="btn btn-secondary" title="Link zu diesem Skript kopieren">
        <i class="fa-solid fa-link"></i>
      </button>

      <div class="status-pill" id="status-pill">
        <div class="status-dot" id="status-dot"></div>
        <span id="status-text">Lade WebAssembly...</span>
      </div>
    </div>
  </header>

  <!-- Workspace -->
  <main class="workspace">
    <!-- Left: Code Editor -->
    <section class="pane-editor">
      <div class="pane-header">
        <div class="file-info">
          <i class="fa-brands fa-python"></i>
          <span id="current-filename">aliasing.py</span>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-sub);">
          <kbd style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">Strg + Enter</kbd> zum Starten
        </div>
      </div>
      <div class="editor-container">
        <textarea id="code-editor"></textarea>
      </div>
    </section>

    <!-- Right: Output Pane -->
    <section class="pane-output">
      <div class="output-tabs">
        <button class="output-tab active" id="tab-output">
          <i class="fa-solid fa-chart-line"></i>
          <span>Plots & Ausgabe</span>
        </button>
        <div style="flex: 1;"></div>
        <button id="btn-clear-out" style="background: none; border: none; color: var(--text-sub); padding: 0 14px; cursor: pointer; font-size: 0.8rem;" title="Ausgabe leeren">
          <i class="fa-solid fa-trash-can"></i> Leeren
        </button>
      </div>

      <div id="run-indicator" class="run-indicator" role="status" aria-live="polite" aria-hidden="true">
        <div class="run-indicator-card">
          <div class="run-indicator-spinner" aria-hidden="true">
            <div class="run-indicator-bars">
              <span></span><span></span><span></span><span></span>
            </div>
          </div>
          <span>Skript wird ausgeführt …</span>
        </div>
      </div>

      <div class="output-content">
        <!-- Rendered Plots -->
        <div id="plot-container">
          <div class="empty-state">
            <i class="fa-regular fa-image"></i>
            <span>Hier erscheinen generierte Matplotlib-Grafiken.<br>Klicken Sie oben auf <strong>Ausführen</strong>.</span>
          </div>
        </div>

        <!-- Terminal Output -->
        <div style="margin-top: 8px;">
          <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-sub); margin-bottom: 4px; display: flex; justify-content: space-between;">
            <span><i class="fa-solid fa-terminal"></i> Terminal / Konsolen-Ausgabe:</span>
          </div>
          <div id="terminal-container"><span class="terminal-info">Warte auf Programmausführung...</span></div>
        </div>
      </div>
    </section>
  </main>

  <!-- CodeMirror JS -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/python/python.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/edit/matchbrackets.min.js"></script>

  <!-- Main Playground Logic -->
  <script>
    // Embedded course catalog (all 44 scripts)
    const EMBEDDED_SCRIPTS = __EMBEDDED_SCRIPTS_JSON__;

    // Embedded binary data files (WAV), base64-encoded
    const EMBEDDED_DATA_FILES = __EMBEDDED_DATA_FILES_JSON__;

    // DOM Elements
    const demoSelect = document.getElementById("demo-select");
    const btnRun = document.getElementById("btn-run");
    const btnReset = document.getElementById("btn-reset");
    const btnShare = document.getElementById("btn-share");
    const btnClearOut = document.getElementById("btn-clear-out");
    const filenameLabel = document.getElementById("current-filename");
    const statusDot = document.getElementById("status-dot");
    const statusText = document.getElementById("status-text");
    const runIndicator = document.getElementById("run-indicator");
    const plotContainer = document.getElementById("plot-container");
    const terminalContainer = document.getElementById("terminal-container");

    // Immediately bind Pyodide Matplotlib target so plots NEVER append to document.body
    document.pyodideMplTarget = plotContainer;

    let editor = null;
    let pyodideInstance = null;
    let currentScriptKey = "aliasing.py";

    // Format error safely without [object Object]
    function formatError(err) {
      if (!err) return "Unbekannter Fehler";
      if (typeof err === "string") return err;
      if (err.message) return err.message;
      if (err.stack) return err.stack;
      try {
        return JSON.stringify(err);
      } catch (e) {
        return String(err);
      }
    }

    // Safely create nested directories in Pyodide FS
    function ensureDirectory(fs, dirPath) {
      const parts = dirPath.split("/").filter(p => p.length > 0);
      let curr = dirPath.startsWith("/") ? "/" : "";
      for (const p of parts) {
        curr = curr === "/" ? ("/" + p) : (curr ? (curr + "/" + p) : p);
        try {
          fs.mkdir(curr);
        } catch (e) {
          // Directory already exists, ignore
        }
      }
    }

    // Initialize CodeMirror
    function initEditor() {
      editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
        mode: "python",
        theme: "dracula",
        lineNumbers: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true
      });

      // Shortcut: Ctrl + Enter / Cmd + Enter to Run
      editor.setOption("extraKeys", {
        "Ctrl-Enter": () => runCode(),
        "Cmd-Enter": () => runCode()
      });
    }

    // Update Status Pill
    function setStatus(state, msg) {
      statusDot.className = "status-dot" + (state ? " " + state : "");
      statusText.textContent = msg;
      btnRun.disabled = (state === "running");
      const isRunning = state === "running";
      runIndicator.classList.toggle("is-running", isRunning);
      runIndicator.setAttribute("aria-hidden", String(!isRunning));
    }

    // Terminal Output
    function clearTerminal() {
      terminalContainer.innerHTML = "";
    }

    function appendTerminal(text, type = "") {
      const span = document.createElement("span");
      span.className = type;
      span.textContent = text;
      terminalContainer.appendChild(span);
      terminalContainer.scrollTop = terminalContainer.scrollHeight;
    }

    // Plot Display
    function clearPlots() {
      plotContainer.innerHTML = "";
    }

    // Load Pyodide WASM Runtime
    async function initPyodideRuntime() {
      try {
        setStatus("", "Lade Python WASM (v0.26)...");
        pyodideInstance = await loadPyodide({
          stdout: (text) => appendTerminal(text + "\\n"),
          stderr: (text) => appendTerminal(text + "\\n", "terminal-err")
        });

        setStatus("", "Lade NumPy, SciPy & Matplotlib...");
        await pyodideInstance.loadPackage(["numpy", "scipy", "matplotlib"]);

        // Preload all 44 course scripts into Pyodide virtual filesystem
        for (const [relPath, code] of Object.entries(EMBEDDED_SCRIPTS)) {
          try {
            const parts = relPath.split("/");
            if (parts.length > 1) {
              const dir = parts.slice(0, -1).join("/");
              ensureDirectory(pyodideInstance.FS, dir);
            }
            pyodideInstance.FS.writeFile(relPath, code);
            // Also write flat in root for simple imports (e.g. from radar1 import gen_receive)
            if (parts.length > 1) {
              pyodideInstance.FS.writeFile(parts[parts.length - 1], code);
            }
          } catch (fileErr) {
            console.warn("Preload warning for", relPath, fileErr);
          }
        }

        // Restore WAV files at the documented absolute path and at the
        // course scripts' existing ../data path relative to Pyodide's CWD.
        const dataDirectories = ["/data", "../data"];
        for (const dataDirectory of dataDirectories) {
          ensureDirectory(pyodideInstance.FS, dataDirectory);
        }
        for (const [fileName, encodedData] of Object.entries(EMBEDDED_DATA_FILES)) {
          try {
            const binary = atob(encodedData);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) {
              bytes[i] = binary.charCodeAt(i);
            }
            for (const dataDirectory of dataDirectories) {
              pyodideInstance.FS.writeFile(dataDirectory + "/" + fileName, bytes);
            }
          } catch (fileErr) {
            console.warn("Data preload warning for", fileName, fileErr);
          }
        }

        setStatus("", "Initialisiere Ausführungs-Umgebung...");
        await pyodideInstance.runPythonAsync(`
import sys, types

# Setup dedicated execution harness to ensure clean isolation
_dsv_harness = types.ModuleType('_dsv_harness')
sys.modules['_dsv_harness'] = _dsv_harness

_harness_code = '''
import sys

# Patch matplotlib_pyodide destroy to prevent null parentNode errors
try:
    import matplotlib_pyodide.browser_backend
    def _safe_destroy(self, *args, **kwargs):
        try:
            div = self.get_element("")
            if div is not None:
                parent = div.parentNode
                if parent is not None:
                    parent.removeChild(div)
        except Exception:
            pass
    matplotlib_pyodide.browser_backend.FigureCanvasWasm.destroy = _safe_destroy
except Exception:
    pass

def reset_environment():
    # 1. Close and wipe all matplotlib figures completely
    try:
        import matplotlib.pyplot as plt
        plt.close('all')
    except Exception:
        pass
    try:
        import matplotlib._pylab_helpers
        matplotlib._pylab_helpers.Gcf.figs.clear()
    except Exception:
        pass

    # 2. Reset cached course modules so edits in the editor take effect
    for mod in ['radar1', 'mlbs']:
        sys.modules.pop(mod, None)

    # 3. Wipe all user-defined globals from __main__
    main_dict = sys.modules['__main__'].__dict__
    keep_keys = {'__name__', '__doc__', '__package__', '__loader__', '__spec__', '__builtins__'}
    for key in list(main_dict.keys()):
        if key not in keep_keys:
            del main_dict[key]

def finish_execution():
    # Show any figures that were created but not yet shown (e.g. scripts using plt.savefig)
    try:
        import matplotlib.pyplot as plt
        for num in list(plt.get_fignums()):
            fig = plt.figure(num)
            fig.canvas.show()
    except Exception:
        pass

def execute(code_str, filename='<string>'):
    reset_environment()
    main_dict = sys.modules['__main__'].__dict__
    main_dict['__file__'] = filename
    compiled = compile(code_str, filename, 'exec')
    exec(compiled, main_dict, main_dict)
    finish_execution()
'''
exec(_harness_code, _dsv_harness.__dict__)
`);

        setStatus("ready", "Bereit (Python 3.11 WASM)");
        // Trigger initial run for initial script
        runCode();
      } catch (err) {
        console.error(err);
        setStatus("error", "Fehler beim Laden von Pyodide");
        appendTerminal("Fehler beim Initialisieren der Python-Umgebung:\\n" + formatError(err), "terminal-err");
      }
    }

    // Load Script Code from Catalog or URL
    async function loadScript(scriptName) {
      currentScriptKey = scriptName;
      filenameLabel.textContent = scriptName;

      // Update select dropdown if matches
      if ([...demoSelect.options].some(o => o.value === scriptName)) {
        demoSelect.value = scriptName;
      }

      // Check embedded catalog first
      if (EMBEDDED_SCRIPTS[scriptName]) {
        editor.setValue(EMBEDDED_SCRIPTS[scriptName]);
        return;
      }

      // Try fetching from repository or raw GitHub
      try {
        const candidates = [
          scriptName,
          `dsv/code/${scriptName}`,
          `../dsv/code/${scriptName}`,
          `https://raw.githubusercontent.com/SebastianSemper/lecturenotes/main/dsv/code/${scriptName}`
        ];
        for (const url of candidates) {
          try {
            const resp = await fetch(url);
            if (resp.ok) {
              const text = await resp.text();
              editor.setValue(text);
              return;
            }
          } catch (e) {}
        }
      } catch (e) {
        console.warn("Fetch error, falling back to aliasing.py", e);
      }

      // Default fallback
      editor.setValue(EMBEDDED_SCRIPTS["aliasing.py"] || "# Skript nicht gefunden.");
    }

    // Run Code
    async function runCode() {
      if (!pyodideInstance) return;
      const code = editor.getValue();

      setStatus("running", "Führe Skript aus...");
      clearPlots();
      clearTerminal();
      appendTerminal("▶ Starte " + currentScriptKey + "...\\n", "terminal-info");

      // Let the browser paint the running overlay before WASM work begins.
      await new Promise(resolve => requestAnimationFrame(resolve));

      // Sync edited code into Pyodide virtual filesystem
      try {
        pyodideInstance.FS.writeFile(currentScriptKey, code);
        const parts = currentScriptKey.split("/");
        if (parts.length > 1) {
          pyodideInstance.FS.writeFile(parts[parts.length - 1], code);
        }
      } catch (e) {}

      const startTime = performance.now();

      try {
        // Run code via harness module which guarantees clean __main__ namespace and fresh figure state
        pyodideInstance.globals.set("__user_code__", code);
        pyodideInstance.globals.set("__user_filename__", currentScriptKey);
        await pyodideInstance.runPythonAsync(`
import sys
sys.modules['_dsv_harness'].execute(__user_code__, __user_filename__)
`);

        const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);
        setStatus("ready", `Fertig (${elapsed}s)`);
        appendTerminal(`\\n✔ Erfolgreich beendet in ${elapsed}s\\n`, "terminal-info");

        // If no plots were generated, show informative note in plot area
        if (plotContainer.children.length === 0) {
          plotContainer.innerHTML = `
            <div class="empty-state">
              <i class="fa-solid fa-circle-check" style="color: var(--success); opacity: 0.85;"></i>
              <span>Skript ohne grafische Ausgabe ausgeführt.<br>Siehe Konsolenausgabe unten.</span>
            </div>
          `;
        }
      } catch (err) {
        console.error(err);
        setStatus("error", "Laufzeitfehler");
        appendTerminal("\\n" + formatError(err) + "\\n", "terminal-err");

        if (plotContainer.children.length === 0) {
          plotContainer.innerHTML = `
            <div class="empty-state">
              <i class="fa-solid fa-triangle-exclamation" style="color: var(--error); opacity: 0.85;"></i>
              <span>Ausführung mit Fehler abgebrochen.<br>Details siehe Terminal-Ausgabe.</span>
            </div>
          `;
        }
      }
    }

    // Event Listeners
    btnRun.addEventListener("click", runCode);

    btnReset.addEventListener("click", () => {
      loadScript(currentScriptKey);
    });

    btnShare.addEventListener("click", () => {
      const url = new URL(window.location.href);
      url.searchParams.set("script", currentScriptKey);
      navigator.clipboard.writeText(url.href).then(() => {
        setStatus("ready", "Link in Zwischenablage kopiert!");
        setTimeout(() => {
          setStatus("ready", "Bereit (Python 3.11 WASM)");
        }, 2500);
      }).catch(() => {
        alert("Link: " + url.href);
      });
    });

    btnClearOut.addEventListener("click", () => {
      clearPlots();
      clearTerminal();
      plotContainer.innerHTML = `
        <div class="empty-state">
          <i class="fa-regular fa-image"></i>
          <span>Hier erscheinen generierte Matplotlib-Grafiken.<br>Klicken Sie oben auf <strong>Ausführen</strong>.</span>
        </div>
      `;
    });

    demoSelect.addEventListener("change", async (e) => {
      const script = e.target.value;
      const url = new URL(window.location.href);
      url.searchParams.set("script", script);
      window.history.pushState({}, "", url);
      await loadScript(script);
      if (pyodideInstance) {
        runCode();
      }
    });

    // Init on page load
    window.addEventListener("DOMContentLoaded", () => {
      initEditor();

      // Read URL query parameter
      const params = new URLSearchParams(window.location.search);
      const targetScript = params.get("script") || params.get("code") || "aliasing.py";

      loadScript(targetScript);
      initPyodideRuntime();
    });
  </script>
</body>
</html>
"""

# Replace placeholders
final_html = (
    HTML_TEMPLATE
    .replace("__DEMO_OPTIONS__", options_str)
    .replace("__EMBEDDED_SCRIPTS_JSON__", scripts_json_str)
    .replace("__EMBEDDED_DATA_FILES_JSON__", data_files_json_str)
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output",
    default=os.path.join(REPO_ROOT, "docs", "index.html"),
    help="Generated HTML path (default: docs/index.html)",
)
args = parser.parse_args()

OUTPUT_HTML = os.path.abspath(args.output)
os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(final_html)
print(f"Created {OUTPUT_HTML} ({len(final_html)} bytes)")
