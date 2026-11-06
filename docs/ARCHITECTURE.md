# Architecture

## Purpose

This application demonstrates an AI-in-Speech-Processing workflow in which a
person can express a health concern by voice or text and receive a structured,
non-diagnostic check-in. The output is a factual note containing only the
user's supplied information and fixed general guidance.

## Component map

~~~
Streamlit browser UI
        |
        +-- typed concern
        +-- microphone recording
        +-- audio-file upload
                 |
                 v
        faster-whisper wrapper
                 |
                 v
        editable transcript
                 |
                 v
        deterministic safety routing
                 |
        +--------+--------+
        |                 |
        v                 v
 warning / stop     topic matcher
                          |
                          v
                  JSON question bank
                          |
                          v
             safety routing on every answer
                          |
                          v
                factual clinician note
~~~

## Modules

| Location | Responsibility |
| --- | --- |
| app.py | Streamlit pages, consent, browser-state handling, audio/text intake, and note display |
| cli.py | A small non-UI demonstration for text or audio inputs |
| src/speech.py | Converts an uploaded or recorded audio object into a temporary file, transcribes it locally, then removes the temporary file |
| src/classifier.py | Trains and uses the bundled TF-IDF plus Logistic Regression text-topic model |
| src/triage.py | Deterministic checks for explicit urgent wording and requests for medicine or dose advice |
| src/conversation.py | Loads the question path, validates answers, and creates a factual user-entered summary |
| src/content.py | Fixed warning and general next-step wording |
| src/service.py | Coordinates the initial message, topic path, and follow-up answers |
| data/*.json | Project-authored synthetic examples, questions, and routing scenarios |

## Processing sequence

1. The user consents and records, uploads, or types a short concern.
2. For audio, faster-whisper transcribes the input on the local machine. The
   user can correct the text before the app continues.
3. The initial text is checked by deterministic safety rules.
4. An urgent route or a medicine/dose request stops the normal conversation.
5. Otherwise, the classifier assigns one broad navigation topic based on
   synthetic training examples.
6. The app asks the fixed questions assigned to that topic, one at a time.
7. Every free-text answer is checked again before another question is shown.
8. If no guard is triggered, the app creates a factual note from the entered
   concern and answers.

## Safety precedence

Safety checks override the classifier and question path:

1. Emergency wording routes to emergency guidance.
2. Concerning wording routes to prompt professional assessment guidance.
3. Medicine or dose requests receive a boundary response.
4. Only then can the topic matcher choose a question path.

The classifier is therefore a user-interface navigation component, not a
diagnosis model. It does not use body weight, medical history, allergies, or
medicine lists to make treatment decisions.

## Model and data

The baseline model is a scikit-learn pipeline:

~~~
Synthetic text examples
      |
      v
TF-IDF vectorizer
      |
      v
Logistic Regression
      |
      v
Broad question-path label
~~~

The JSON files are intentionally small and synthetic so the project can be
shared and run without restricted clinical data. See data/DATA_CARD.md for
the coverage, limitations, and rules for extending the examples.

## Local privacy behavior

- Audio is written to a temporary local file only while it is transcribed, then
  removed.
- The application does not intentionally save recordings, transcripts, or
  answers to project files or application logs.
- Browser session state exists while the Streamlit session is open; it is not a
  secure patient-record system.
- A production deployment would require separate security, consent, privacy,
  legal, and clinical review.

## What this architecture does not do

- It does not identify a disease.
- It does not prescribe, compare, select, or dose medicines.
- It does not replace a healthcare professional or emergency service.
- It does not train on or ship patient records.
