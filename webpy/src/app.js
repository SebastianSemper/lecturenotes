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
          stdout: (text) => appendTerminal(text + "\n"),
          stderr: (text) => appendTerminal(text + "\n", "terminal-err")
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
        appendTerminal("Fehler beim Initialisieren der Python-Umgebung:\n" + formatError(err), "terminal-err");
      }
    }

    // Accept repository paths from PDF links as well as catalog-relative paths.
    function normalizeScriptName(scriptName) {
      return scriptName.replace(/^\/?(?:dsv\/)?code\//, "");
    }

    // Load Script Code from Catalog or URL
    async function loadScript(scriptName) {
      scriptName = normalizeScriptName(scriptName);
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
      appendTerminal("▶ Starte " + currentScriptKey + "...\n", "terminal-info");

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
        appendTerminal(`\n✔ Erfolgreich beendet in ${elapsed}s\n`, "terminal-info");

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
        appendTerminal("\n" + formatError(err) + "\n", "terminal-err");

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

