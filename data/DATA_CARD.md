# Data card

## Intended use

The bundled JSON files demonstrate a local, multi-turn speech-processing
application:

1. a user describes a concern;
2. the application converts voice to editable text;
3. a small text model chooses a broad **question path**;
4. fixed questions collect non-identifying, factual responses;
5. safety rules can stop the flow and show escalation wording; and
6. the app creates a user-entered summary for a qualified clinician.

## Data origin

All bundled rows, prompts, and scenarios are project-authored synthetic
examples. They are not real patient records and do not represent clinical
guidance.

## Fields

| File | Key fields |
| --- | --- |
| symptom_topics.json | Broad topic id, display label, synthetic text examples |
| follow_up_questions.json | Question id, visible prompt, answer choices, fixed safety-routing key |
| demo_navigation_scenarios.json | Synthetic initial text, broad path, expected UI end state |

## Explicitly out of scope

- Diagnosing a disease or calculating a disease likelihood
- Selecting, comparing, recommending, or prescribing a medicine
- Calculating a dose from body weight, age, symptoms, or medical history
- Treating this question flow as a clinical protocol or emergency assessment

## Limitations

- The examples are small, incomplete, English-only, and non-representative.
- The topic model is only a reproducible TF-IDF demonstration.
- The safety rules detect a limited set of words and selected answers.
- A non-urgent result is not proof that a situation is safe.
- No question response is used to make a medication or dosage decision.

## Optional external sources

Optional use of MedlinePlus or MeSH must retain the source attribution and
licence obligations described in [README.md](README.md). Do not bundle
copyrighted MedlinePlus drug monographs, A.D.A.M. content, or images.

