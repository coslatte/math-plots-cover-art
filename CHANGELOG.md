# Changelog

## Unreleased

- Raised the default CLI render size to HD.
- Changed `generate all` to default to 5 images per generator.
- Added automatic dated run folders for `generate all` when no output directory is provided.
- Replaced the legacy menu loop with a standard subcommand-based CLI.
- Added named generator, palette, and template registries.
- Added template-driven batch runs and configurable output organization.
- Threaded DPI and palette selection through the rendering pipeline.
- Added CLI coverage and kept the existing rendering tests green.
