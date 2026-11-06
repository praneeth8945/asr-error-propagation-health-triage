# Changelog

All notable changes to this repository are documented in this file.

## [Unreleased]

### Planned

- Improve documentation and test coverage while preserving the educational,
  non-diagnostic scope.

## [1.0.0] - 2026-09-23

### Added

- Local Streamlit interface with typed, uploaded-audio, and microphone-input
  paths.
- Local faster-whisper transcription with an editable transcript.
- A reproducible TF-IDF and Logistic Regression broad-topic matcher trained
  only from bundled synthetic examples.
- A visible JSON question bank, per-turn safety checks, medicine/dose request
  guard, and factual clinician-note generator.
- Synthetic dataset documentation, unit tests, Docker configuration, and
  GitHub Actions test workflow.

### Safety

- The application does not diagnose, prescribe, recommend medicines, or
  calculate doses.
- Explicit emergency and prompt-professional-assessment wording takes priority
  over topic routing.
