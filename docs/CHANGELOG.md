# Changelog

## Unreleased

- Added a pure-math layer for image generation so tests can validate functions without rendering.
- Added an optional GPU-aware array backend with a clean full-canvas export path.
- Added unit tests for the mathematical helpers and a render batch smoke test.
- Generated 3 validation image sets under `output/validation_runs_20260412/` to exercise every generator before finalizing the work.
- Hardened image export paths against unsafe names and made batch rendering continue when one generator fails.
- Added a guard for missing music folders so audio-driven art falls back cleanly instead of crashing.
- Ensured figures are always closed after save attempts to avoid leaking resources during long batch runs.
- Added workspace Python settings so the editor resolves the venv and `src/` paths without import noise.
