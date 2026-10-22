# Automated PDF Release Workflow

## Summary

Add a separate GitHub Actions workflow that builds `dsv/dsv_script.tex` in a
complete TeX Live environment. Pull requests and manual runs validate the build
and expose the PDF as a temporary workflow artifact; pushing a `v*` tag
additionally publishes it as a GitHub Release asset.

Estimated effort: **1–2 hours**, or up to half a day if TeX package
incompatibilities appear.

## Implementation Changes

- Add a dedicated PDF workflow without changing the existing Pages workflow.
- Use `xu-cheng/latex-action@v4` with:
  - Working directory `dsv`
  - Root file `dsv_script.tex`
  - `latexmk`
  - Shell escape enabled for `minted`
  - Existing `.latexmkrc` for glossaries and bibliography processing
- Trigger builds on:
  - Pull requests affecting LaTeX sources, images, bibliography, or the workflow
  - Manual `workflow_dispatch`
  - Tags matching `v*`
- Verify that the resulting PDF exists and is nonempty.
- Upload every successful build as a workflow artifact named
  `DSV-Codeschnippsel`.
- On `v*` tags, create a GitHub Release with generated release notes and attach
  the PDF as `DSV-Codeschnippsel.pdf`.
- Grant `contents: write` only to the release job.
- Keep the currently tracked `dsv/dsv_script.pdf` unchanged; the release asset
  becomes the authoritative published build without having CI commit binaries
  back into the repository.
- Document the release procedure: create and push a tag such as `v2026.1`.

## Test Plan

- Run the workflow manually on the feature branch and download the workflow
  artifact.
- Confirm the PDF opens, has the expected page count, and includes minted code,
  bibliography, glossary, images, and links.
- Verify a pull request builds the PDF but cannot create a Release.
- Push a temporary test tag and confirm that one Release is created with
  `DSV-Codeschnippsel.pdf`.
- Delete the test release/tag after verification if it should not remain public.
- Confirm an intentional LaTeX error fails before artifact or release
  publication.

## Assumptions

- Releases are immutable and tag-driven using `v*`; ordinary `main` pushes do
  not replace a rolling release.
- Only `dsv/dsv_script.tex` is released; slides remain outside this workflow.
- No repository secrets are required because publication uses the standard
  GitHub token.
- The third-party LaTeX and release actions are version-pinned and reviewed
  before merging.
