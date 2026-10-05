import base64
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


class WebBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.output = pathlib.Path(cls.temp_dir.name) / "site" / "index.html"
        cls._run_build(cls.output)
        cls.html_bytes = cls.output.read_bytes()
        cls.html = cls.html_bytes.decode("utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @staticmethod
    def _run_build(output):
        return subprocess.run(
            [sys.executable, str(BUILD_SCRIPT), "--output", str(output)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

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
            decoded = base64.b64decode(payload, validate=True)
            self.assertEqual(decoded, (REPO_ROOT / "dsv" / "data" / name).read_bytes())

    def test_generated_page_is_complete(self):
        self.assertNotRegex(self.html, r"__[A-Z_]+__")
        self.assertNotIn('http-equiv="refresh"', self.html)
        self.assertIn('const dataDirectories = ["/data", "../data"]', self.html)
        self.assertIn('class="run-indicator-card"', self.html)
        self.assertIn("requestAnimationFrame(resolve)", self.html)

    def test_build_is_deterministic(self):
        second_output = pathlib.Path(self.temp_dir.name) / "second" / "index.html"
        self._run_build(second_output)
        self.assertEqual(self.html_bytes, second_output.read_bytes())

    def test_missing_repository_inputs_fail_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = pathlib.Path(directory)
            isolated_webpy = isolated_root / "webpy"
            isolated_webpy.mkdir()
            isolated_script = isolated_webpy / "build.py"
            shutil.copyfile(BUILD_SCRIPT, isolated_script)
            result = subprocess.run(
                [sys.executable, str(isolated_script)],
                cwd=isolated_root,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python source directory not found", result.stderr)

    def test_missing_required_wav_fails_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = pathlib.Path(directory)
            isolated_webpy = isolated_root / "webpy"
            isolated_code = isolated_root / "dsv" / "code"
            isolated_webpy.mkdir(parents=True)
            isolated_code.mkdir(parents=True)
            isolated_script = isolated_webpy / "build.py"
            shutil.copyfile(BUILD_SCRIPT, isolated_script)
            source_code = REPO_ROOT / "dsv" / "code"
            for source in source_code.rglob("*.py"):
                destination = isolated_code / source.relative_to(source_code)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            result = subprocess.run(
                [sys.executable, str(isolated_script)],
                cwd=isolated_root,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Required data file not found", result.stderr)

    def test_generated_javascript_parses(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not installed")
        match = re.search(
            r"<!-- Main Playground Logic -->\s*<script>(.*?)</script>",
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
