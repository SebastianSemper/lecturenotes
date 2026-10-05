#!/usr/bin/env python3
"""Build the DSV Codeschnippsel static website."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil


REPO_ROOT = Path(__file__).resolve().parent.parent
WEBPY_DIR = REPO_ROOT / "webpy"
SOURCE_DIR = WEBPY_DIR / "src"
CODE_DIR = REPO_ROOT / "dsv" / "code"
DATA_DIR = REPO_ROOT / "dsv" / "data"
FONT_SOURCE_DIR = WEBPY_DIR / "assets" / "fonts"

FONT_FILES = {
    "InterVariable.woff2": "693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3",
    "FiraCode-VF.woff2": "408e876a202f15ea6ee307a70a65cf40ceb222c589a0b17e0a3a371db96dd49f",
    "Inter-OFL.txt": "262481e844521b326f5ecd053e59b98c8b2da78c8ee1bdbb6e8174305e54935a",
    "FiraCode-OFL.txt": "1d41e10031ab125302780a05ec4c91d218e47db0c7e37cf315cce5e608cdc25c",
}

SOURCE_FILES = {
    "index": "index.html",
    "legal": "rechtliches.html",
    "root": "root.html",
    "app_css": "app.css",
    "legal_css": "legal.css",
    "root_css": "root.css",
    "app_js": "app.js",
    "redirect_js": "redirect.js",
}

LECTURE_MAP = [('Vorlesung 01: Einführung & Dynamik',
  [('buddhabrot.py', 'Buddhabrot-Fraktal (Komplexe Zahlen & Dynamik)'),
   ('mandelbrot.py', 'Mandelbrot-Menge (Diskrete Iteration)'),
   ('complex_exp.py', 'Harmonische Exponentialschwingung')]),
 ('Vorlesung 02: Harmonische Signale & Abtastung',
  [('cont_harms.py', 'Kontinuierliche Schwingungen & Phasoren'),
   ('disc_harms.py', 'Diskrete Schwingungen & Periodizität'),
   ('disc_harms_comp.py', 'Harmonische Trajektorien auf Einheitskreis'),
   ('aliasing.py', 'Aliasing im Zeitbereich bei Unterabtastung')]),
 ('Vorlesung 03: Samplingtheorem & Rekonstruktion',
  [('sampling_theorem.py', 'Dirac-Kamm & Sinc-Rekonstruktion'),
   ('fourier_trafo.py', 'CFT des Rechteckpulses (Sinc-Spektrum)')]),
 ('Vorlesung 04: Diskrete Signale & Systeme',
  [('even_odd.py', 'Gerade/Ungerade Signalzerlegung'),
   ('accumulator.py', 'Diskreter Akkumulator (Gedächtnis)'),
   ('complex_exp.py', 'Diskrete komplexe Exponentialfolge')]),
 ('Vorlesung 05: LTI-Systeme & Differenzengleichungen',
  [('moving_average.py', 'Moving Average Glättungsfilter'),
   ('ramp_ma.py', 'Kaskadierte Moving Averages & Rampe'),
   ('cumulative_sum.py', 'Kumulatives Mittel (Rekursiv vs. Direkt)'),
   ('exp_mean.py', 'Exponentielles Mittel (1-Pol-IIR)'),
   ('square_root.py', 'Newton-Wurzelberechnung als LCCDE')]),
 ('Vorlesung 06: Die z-Transformation',
  [('dtft_z.py', '3D-Relief der z-Transformation & Einheitskreis')]),
 ('Vorlesung 07: Fourier-Transformationen (CFT & DTFT)',
  [('fourier_series.py', 'Fourier-Reihe & Gibbs-Phänomen'),
   ('period_psd.py', 'Leistungsdichtespektrum (PSD)'),
   ('dtft.py', 'DTFT des diskreten Sinc-Signals')]),
 ('Vorlesung 08: Diskrete Fourier-Transformation (DFT)',
  [('dft_1.py', 'DFT: Matrix- vs. Schleifenberechnung'),
   ('nyquist_seq.py', 'DC- vs. Nyquist-Sequenz im DFT-Gitter'),
   ('dft_conv.py', 'Schnelle Faltung im Frequenzbereich')]),
 ('Vorlesung 09: Zeit-Frequenz-Analyse (STFT)',
  [('stft_win.py', 'Fensterfunktionen & Spectral Leakage'),
   ('stft_length.py', 'Einfluss der Fensterbreite W'),
   ('stft_harm.py', 'Spektrogramm harmonischer Töne'),
   ('stft_zp.py', 'Zero-Padding in STFT-Fensterblöcken'),
   ('stft_bass.py', 'Pitch Tracking einer Bassgitarre')]),
 ('Vorlesung 11: Korrelation & Radar',
  [('radar1.py', 'Radar-Signale & Autokorrelation'),
   ('mlbs.py', 'MLBS-Erzeugung via LFSR'),
   ('radar2.py', 'Pulskompression & Mehrzielradar')]),
 ('Vorlesung 12: Stochastische Signale & Stationarität',
  [('random/discrete.py', 'Diskrete Zufallsvariablen & Dichte'),
   ('random/normal1.py', 'Normalverteilung (Histogramm vs. Gauß)'),
   ('random/signal1.py', 'Realisierungen stochastischer Prozesse'),
   ('random/signal2.py', 'Scharmittel vs. Zeitmittel'),
   ('random/signal3.py', 'Stationarität (WSS) & AKF-Schätzung')]),
 ('Vorlesung 13: Quantisierung & Parameterschätzung',
  [('random/quantization1.py', 'Quantisierungskennlinie & Fehlersignal'),
   ('random/quantization2.py', 'Quantisierungsrauschen & Area Sampling'),
   ('random/quantization3.py', 'Widrow-Theorem: Dichterekonstruktion'),
   ('random/paramest1.py', 'Parameterschätzung normalverteilter Signale')]),
 ('Vorlesung 14: Moderne Abtasttheorie & B-Splines',
  [('bsplines_eval.py', 'Auswertung kubischer B-Splines'),
   ('bsplines_coeffs.py', 'Unser-Algorithmus (IIR-Rekursionsfilter)')])]


def read_source(name):
    path = SOURCE_DIR / SOURCE_FILES[name]
    if not path.is_file():
        raise FileNotFoundError(f"Required web source not found: {path}")
    return path.read_text(encoding="utf-8")


def render_template(template_name, replacements):
    rendered = read_source(template_name)
    for marker_name, value in replacements.items():
        marker = f"__{marker_name}__"
        count = rendered.count(marker)
        if count != 1:
            raise ValueError(
                f"Template {SOURCE_FILES[template_name]} must contain {marker} "
                f"exactly once; found {count}"
            )
        rendered = rendered.replace(marker, value)

    unresolved = sorted(set(re.findall(r"__[A-Z][A-Z0-9_]*__", rendered)))
    if unresolved:
        raise ValueError(
            f"Template {SOURCE_FILES[template_name]} has unresolved placeholders: "
            + ", ".join(unresolved)
        )
    return rendered


def collect_scripts():
    if not CODE_DIR.is_dir():
        raise FileNotFoundError(f"Python source directory not found: {CODE_DIR}")

    scripts = {
        path.relative_to(CODE_DIR).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(CODE_DIR.rglob("*.py"))
    }
    referenced = {
        script_name
        for _, entries in LECTURE_MAP
        for script_name, _ in entries
    }
    missing = sorted(referenced - scripts.keys())
    if missing:
        raise FileNotFoundError(
            "Lecture catalog references missing scripts: " + ", ".join(missing)
        )

    print(f"Loaded {len(scripts)} scripts.")
    return scripts


def collect_data_files():
    data_files = {}
    for name in ("g_maj.wav", "g_bend.wav"):
        path = DATA_DIR / name
        if not path.is_file():
            raise FileNotFoundError(f"Required data file not found: {path}")
        data_files[name] = base64.b64encode(path.read_bytes()).decode("ascii")
        print(
            f"Embedded {name} ({path.stat().st_size:,} bytes -> "
            f"{len(data_files[name]):,} b64 chars)"
        )
    return data_files


def render_demo_options():
    lines = []
    for group_name, entries in LECTURE_MAP:
        lines.append(f'        <optgroup label="{group_name}">')
        for script_name, description in entries:
            lines.append(
                f'          <option value="{script_name}">'
                f'{description} ({script_name})</option>'
            )
        lines.append("        </optgroup>")
    return "\n".join(lines)


def validate_fonts():
    for name, expected_hash in FONT_FILES.items():
        path = FONT_SOURCE_DIR / name
        if not path.is_file():
            raise FileNotFoundError(f"Required font asset not found: {path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Font asset hash mismatch: {path}")


def render_site():
    scripts = collect_scripts()
    data_files = collect_data_files()
    validate_fonts()

    app_js = render_template(
        "app_js",
        {
            "EMBEDDED_SCRIPTS_JSON": json.dumps(scripts),
            "EMBEDDED_DATA_FILES_JSON": json.dumps(data_files),
        },
    )
    app_html = render_template(
        "index",
        {
            "APP_CSS": read_source("app_css"),
            "DEMO_OPTIONS": render_demo_options(),
            "APP_JS": app_js,
        },
    )
    legal_html = render_template(
        "legal",
        {"LEGAL_CSS": read_source("legal_css")},
    )
    root_html = render_template(
        "root",
        {
            "ROOT_CSS": read_source("root_css"),
            "REDIRECT_JS": read_source("redirect_js"),
        },
    )
    return root_html, app_html, legal_html


def write_site(site_root):
    root_html, app_html, legal_html = render_site()
    dsv_dir = site_root / "dsv"
    dsv_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        site_root / "index.html": root_html,
        dsv_dir / "index.html": app_html,
        dsv_dir / "rechtliches.html": legal_html,
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
        print(f"Created {path} ({len(content.encode('utf-8'))} bytes)")

    font_output_dir = dsv_dir / "assets" / "fonts"
    font_output_dir.mkdir(parents=True, exist_ok=True)
    for name in FONT_FILES:
        shutil.copyfile(FONT_SOURCE_DIR / name, font_output_dir / name)
    print(f"Copied {len(FONT_FILES)} font assets to {font_output_dir}")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-root",
        type=Path,
        default=REPO_ROOT / "docs",
        help="Generated site directory (default: docs)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    write_site(args.site_root.resolve())


if __name__ == "__main__":
    main()
