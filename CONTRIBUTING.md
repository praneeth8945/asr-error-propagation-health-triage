# Contributing to Voice Health Navigator

Thank you for improving this educational project. Contributions must preserve
the project's safety boundary: it is a speech-processing and guided-navigation
demo, not a clinical decision system.

## Before making a change

1. Read the safety notice and data documentation in README.md and
   data/DATA_CARD.md.
2. Create a branch with a clear name, for example
   "docs/improve-windows-setup" or "fix/audio-cleanup".
3. Create and activate a Python virtual environment.
4. Install development dependencies:

~~~
python -m pip install -r requirements-dev.txt
~~~

## Required checks

Run these commands before opening a pull request:

~~~
python scripts/validate_dataset.py
python -m unittest discover -s tests -v
~~~

Describe the user-visible effect of the change and include or update tests
when behavior changes.

## Safety and data rules

- Do not add code that diagnoses a condition, recommends a medicine, selects a
  treatment, or calculates a dose.
- Do not add personal health information, identifiable audio, patient records,
  credentials, tokens, or secrets to the repository.
- Use only project-authored synthetic data unless the source, licence,
  consent, and permitted use have been checked and documented.
- Treat the broad text-topic classifier as navigation only. It must not be
  described as a diagnostic model.
- If a change affects warnings, question routing, medicine-request handling,
  data, or the factual summary, explain the safety impact in the pull request.

## Pull-request checklist

- [ ] The application still starts locally.
- [ ] Dataset validation and unit tests pass.
- [ ] No local models, virtual environments, secrets, logs, or archives are
      staged for commit.
- [ ] Documentation matches the implementation.
- [ ] The change preserves the non-diagnostic, non-prescribing project scope.

## Commit messages

Use a short, descriptive imperative message, such as:

~~~
docs: add GitHub publishing guide
fix: support older Streamlit audio widget
test: cover safety wording in a follow-up answer
~~~
