import base64
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "webpy" / "build.py"
WEB_SOURCES = REPO_ROOT / "webpy" / "src"


class WebBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.site_root = pathlib.Path(cls.temp_dir.name) / "site"
        cls._run_build(cls.site_root)
        cls.root_html = (cls.site_root / "index.html").read_text(encoding="utf-8")
        cls.output = cls.site_root / "dsv" / "index.html"
        cls.html_bytes = cls.output.read_bytes()
        cls.html = cls.html_bytes.decode("utf-8")
        cls.legal = (cls.site_root / "dsv" / "rechtliches.html").read_text(
            encoding="utf-8"
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @staticmethod
    def _run_build(site_root, build_script=BUILD_SCRIPT, cwd=REPO_ROOT, check=True):
        return subprocess.run(
            [
                sys.executable,
                str(build_script),
                "--site-root",
                str(site_root),
            ],
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
        )

    @staticmethod
    def _generated_tree(site_dir):
        return {
            path.relative_to(site_dir).as_posix(): path.read_bytes()
            for path in sorted(site_dir.rglob("*"))
            if path.is_file()
        }

    @staticmethod
    def _copy_isolated_repository(destination):
        isolated_webpy = destination / "webpy"
        isolated_webpy.mkdir(parents=True)
        shutil.copyfile(BUILD_SCRIPT, isolated_webpy / "build.py")
        shutil.copytree(REPO_ROOT / "webpy" / "assets", isolated_webpy / "assets")
        shutil.copytree(WEB_SOURCES, isolated_webpy / "src")
        shutil.copytree(REPO_ROOT / "dsv" / "code", destination / "dsv" / "code")
        shutil.copytree(REPO_ROOT / "dsv" / "data", destination / "dsv" / "data")
        return isolated_webpy / "build.py"

    def _embedded_json(self, variable):
        match = re.search(
            rf"const {variable} = (\{{.*?\}});\n",
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, f"Missing JavaScript variable {variable}")
        return json.loads(match.group(1))

    def test_all_python_sources_are_embedded(self):
        embedded = self._embedded_json("EMBEDDED_SCRIPTS")
        code_dir = REPO_ROOT / "dsv" / "code"
        expected = {
            path.relative_to(code_dir).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(code_dir.rglob("*.py"))
        }
        self.assertEqual(embedded, expected)

    def test_wav_payloads_match_sources(self):
        embedded = self._embedded_json("EMBEDDED_DATA_FILES")
        self.assertEqual(set(embedded), {"g_maj.wav", "g_bend.wav"})
        for name, payload in embedded.items():
            self.assertEqual(
                base64.b64decode(payload, validate=True),
                (REPO_ROOT / "dsv" / "data" / name).read_bytes(),
            )

    def test_generated_page_is_complete(self):
        self.assertNotRegex(self.html, r"__[A-Z_]+__")
        self.assertNotIn('http-equiv="refresh"', self.html)
        self.assertIn('const dataDirectories = ["/data", "../data"]', self.html)
        self.assertIn('class="run-indicator-card"', self.html)
        self.assertIn("requestAnimationFrame(resolve)", self.html)
        self.assertIn("DSV Codeschnippsel", self.html)
        self.assertNotIn("DSV Python Playground", self.html)
        self.assertIn("DSV Lehrprojekt", self.html)
        self.assertIn('href="rechtliches.html#impressum"', self.html)
        self.assertIn('href="rechtliches.html#datenschutz"', self.html)
        self.assertIn('href="rechtliches.html#lizenzen"', self.html)
        self.assertIn("assets/fonts/InterVariable.woff2", self.html)
        self.assertIn("assets/fonts/FiraCode-VF.woff2", self.html)

    def test_root_redirect_preserves_query_and_fragment(self):
        self.assertIn('new URL("dsv/", window.location.href)', self.root_html)
        self.assertIn("target.search = window.location.search", self.root_html)
        self.assertIn("target.hash = window.location.hash", self.root_html)
        self.assertIn("window.location.replace(target.href)", self.root_html)
        self.assertIn('href="dsv/"', self.root_html)

        node = shutil.which("node")
        if node is None:
            return
        script_match = re.search(r"<script>\s*(.*?)</script>", self.root_html, re.DOTALL)
        self.assertIsNotNone(script_match)
        harness = """
let redirected;
global.window = {
  location: {
    href: "https://sebastiansemper.github.io/lecturenotes/?script=dsv/code/aliasing.py#plot",
    search: "?script=dsv/code/aliasing.py",
    hash: "#plot",
    replace: value => { redirected = value; }
  }
};
global.document = { getElementById: () => ({ href: "" }) };
""" + script_match.group(1) + """
if (redirected !== "https://sebastiansemper.github.io/lecturenotes/dsv/?script=dsv/code/aliasing.py#plot") {
  throw new Error(redirected);
}
"""
        result = subprocess.run(
            [node, "--check", "-"], input=harness, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(
            [node, "-"], input=harness, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_prefixed_script_paths_are_normalized(self):
        match = re.search(
            r"(function normalizeScriptName\(scriptName\) \{.*?\n    \})",
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not installed")
        harness = match.group(1) + """
const actual = [
  normalizeScriptName("dsv/code/aliasing.py"),
  normalizeScriptName("code/random/discrete.py"),
  normalizeScriptName("random/discrete.py")
];
if (JSON.stringify(actual) !== JSON.stringify(["aliasing.py", "random/discrete.py", "random/discrete.py"])) {
  throw new Error(JSON.stringify(actual));
}
"""
        result = subprocess.run(
            [node, "-"], input=harness, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_code_caption_links_to_nested_site(self):
        header = (REPO_ROOT / "include" / "head.tex").read_text(encoding="utf-8")
        self.assertIn(
            r"\href{https://SebastianSemper.github.io/lecturenotes/dsv/?script=#1}",
            header,
        )

    def test_generated_site_does_not_contact_google_fonts(self):
        for html_path in self.site_root.rglob("*.html"):
            html_text = html_path.read_text(encoding="utf-8")
            self.assertNotIn("fonts.googleapis.com", html_text, html_path.as_posix())
            self.assertNotIn("fonts.gstatic.com", html_text, html_path.as_posix())

    def test_legal_page_is_complete_and_static(self):
        self.assertIn("DSV Codeschnippsel", self.legal)
        for section in ("impressum", "datenschutz", "lizenzen"):
            self.assertIn(f'id="{section}"', self.legal)
        for value in (
            "Dr.-Ing. Sebastian Semper",
            "Ehrenbergstr. 24",
            "98693 Ilmenau",
            "post@sebastiansemper.de",
            "kein zentral betriebener Webdienst",
        ):
            self.assertIn(value, self.legal)
        for provider in ("GitHub Pages", "cdnjs", "jsDelivr"):
            self.assertIn(provider, self.legal)
        for license_name in ("MIT-Lizenz", "CC BY 4.0", "SIL Open Font License"):
            self.assertIn(license_name, self.legal)
        for wav_name in ("g_maj.wav", "g_bend.wav"):
            self.assertIn(wav_name, self.legal)
        self.assertNotIn("<script", self.legal)
        self.assertNotIn('rel="stylesheet"', self.legal)

    def test_vendored_font_assets_are_copied_unchanged(self):
        expected_hashes = {
            "InterVariable.woff2": "693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3",
            "FiraCode-VF.woff2": "408e876a202f15ea6ee307a70a65cf40ceb222c589a0b17e0a3a371db96dd49f",
            "Inter-OFL.txt": "262481e844521b326f5ecd053e59b98c8b2da78c8ee1bdbb6e8174305e54935a",
            "FiraCode-OFL.txt": "1d41e10031ab125302780a05ec4c91d218e47db0c7e37cf315cce5e608cdc25c",
        }
        source_dir = REPO_ROOT / "webpy" / "assets" / "fonts"
        output_dir = self.site_root / "dsv" / "assets" / "fonts"
        self.assertEqual({path.name for path in output_dir.iterdir()}, set(expected_hashes))
        for name, expected_hash in expected_hashes.items():
            source_bytes = (source_dir / name).read_bytes()
            output_bytes = (output_dir / name).read_bytes()
            self.assertEqual(source_bytes, output_bytes)
            self.assertEqual(hashlib.sha256(output_bytes).hexdigest(), expected_hash)
        self.assertTrue((output_dir / "InterVariable.woff2").read_bytes().startswith(b"wOF2"))
        self.assertTrue((output_dir / "FiraCode-VF.woff2").read_bytes().startswith(b"wOF2"))

    def test_build_is_deterministic(self):
        second_root = pathlib.Path(self.temp_dir.name) / "second"
        self._run_build(second_root)
        self.assertEqual(
            self._generated_tree(self.site_root),
            self._generated_tree(second_root),
        )

    def test_missing_repository_inputs_fail_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = pathlib.Path(directory)
            isolated_webpy = isolated_root / "webpy"
            isolated_webpy.mkdir()
            isolated_script = isolated_webpy / "build.py"
            shutil.copyfile(BUILD_SCRIPT, isolated_script)
            result = self._run_build(
                isolated_root / "site",
                build_script=isolated_script,
                cwd=isolated_root,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python source directory not found", result.stderr)

    def test_missing_required_wav_fails_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = pathlib.Path(directory)
            isolated_script = self._copy_isolated_repository(isolated_root)
            (isolated_root / "dsv" / "data" / "g_maj.wav").unlink()
            result = self._run_build(
                isolated_root / "site",
                build_script=isolated_script,
                cwd=isolated_root,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Required data file not found", result.stderr)

    def test_missing_web_source_fails_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = pathlib.Path(directory)
            isolated_script = self._copy_isolated_repository(isolated_root)
            (isolated_root / "webpy" / "src" / "root.html").unlink()
            result = self._run_build(
                isolated_root / "site",
                build_script=isolated_script,
                cwd=isolated_root,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Required web source not found", result.stderr)

    def test_duplicate_placeholder_fails_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = pathlib.Path(directory)
            isolated_script = self._copy_isolated_repository(isolated_root)
            template = isolated_root / "webpy" / "src" / "root.html"
            content = template.read_text(encoding="utf-8")
            template.write_text(
                content.replace("__ROOT_CSS__", "__ROOT_CSS____ROOT_CSS__"),
                encoding="utf-8",
            )
            result = self._run_build(
                isolated_root / "site",
                build_script=isolated_script,
                cwd=isolated_root,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exactly once; found 2", result.stderr)

    def test_generated_javascript_parses(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not installed")
        match = re.search(
            r"<!-- Main Application Logic -->\s*<script>(.*?)</script>",
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "Main JavaScript block not found")
        result = subprocess.run(
            [node, "--check", "-"],
            input=match.group(1),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
