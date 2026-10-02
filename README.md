# Dependencies

 - `biber`
 - `pygments` for minted
 - `latexmk` for maximum convenience
 - run `pdflatex` with `-shell-escape` flag

## Web playground

The standalone GitHub Pages application is generated from the Python examples
in `dsv/code/` and the WAV files in `dsv/data/`.

Run the same build tests used by CI before opening a pull request:

```bash
python3 -m unittest discover -s webpy/tests -v
```

Build and preview the site locally:

```bash
python3 webpy/build.py
python3 -m http.server 8000 --directory docs
```

Then open <http://localhost:8000/>. The generated `docs/index.html` is ignored
by Git and is rebuilt by the GitHub Pages workflow for every deployment.
