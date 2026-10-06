# Dependencies

 - `biber`
 - `pygments` for minted
 - `latexmk` for maximum convenience
 - run `pdflatex` with `-shell-escape` flag

## DSV Codeschnippsel

The GitHub Pages application is generated from the Python examples
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

Then open <http://localhost:8000/>; the root redirects to
<http://localhost:8000/dsv/> while preserving a selected `script` query. Use
`python3 webpy/build.py --site-root PATH` to build elsewhere. The generated
`docs/index.html` and `docs/dsv/` tree are ignored by Git and rebuilt for every
deployment. The build copies the locally hosted Inter and Fira Code fonts from
`webpy/assets/fonts/` into the generated DSV site.

## Licensing

The repository's own software is available under the MIT License. Original
teaching content and media are available under CC BY 4.0. See [LICENSE.md](LICENSE.md)
for the exact scope and exceptions, and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
for the software and fonts used by DSV Codeschnippsel.
