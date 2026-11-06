# Voice Health Navigator

An educational AI-in-Speech-Processing project that lets a person describe a
health concern by voice or text, then guides them through a short set of
transparent follow-up questions. It creates a factual note that can be shared
with a qualified healthcare professional.

> **Safety notice**
>
> This is an academic demonstration, not a medical device or clinical service.
> It does not diagnose diseases, choose treatment, recommend medicines, or
> calculate doses. For severe, sudden, worsening, or potentially
> life-threatening symptoms, contact local emergency services or a qualified
> healthcare professional immediately.

## Problem statement

People often describe symptoms in natural speech rather than structured forms.
This project demonstrates a safe local pipeline for:

- converting spoken descriptions into editable text;
- identifying a broad educational text topic;
- asking fixed, relevant follow-up questions one at a time;
- checking every turn for a small set of explicit danger phrases;
- stopping the normal flow when an urgent warning appears; and
- producing a factual, user-entered summary for a clinician.

The broad topic model selects a **question path only**. It never claims a
disease or decides treatment.

## What the app does

1. The user records, uploads, or types a concern.
2. faster-whisper converts audio to text locally.
3. The user reviews and edits the transcript.
4. Deterministic red-flag rules check the initial message.
5. A small TF-IDF plus Logistic Regression model selects a broad question path
   from synthetic examples.
6. The UI asks fixed follow-up questions in a chat-like flow.
7. Each selected or typed answer is checked separately for safety wording.
8. The app either:
   - displays an emergency or prompt-professional-assessment message,
   - refuses a medicine/dose request, or
   - creates a non-diagnostic factual note with general next steps.

## Safety boundaries

- No diagnosis, prescription, medicine selection, drug comparison, or dose
  calculation.
- Exact body weight, medicine lists, allergies, and medical history are not
  requested or used to choose treatment.
- Emergency and concerning wording suppress the topic-model output and stop
  the remaining questions.
- The question flow is visible JSON data, not a generative medical chatbot.
- A non-urgent result is not proof that a situation is safe.
- Audio uses a temporary local file during transcription and is then removed.
  The app does not write raw audio, transcripts, or answers to application
  logs or files.

## Architecture

~~~
Voice / audio upload / typed concern
                |
                v
  faster-whisper local transcription
                |
                v
      editable user transcript
                |
                v
initial safety rules -> warning / medicine-request guard
                |
                v
TF-IDF + Logistic Regression broad topic matcher
                |
                v
fixed question bank -> safety check on every answer
                |
                v
factual clinician note + fixed next-step guidance
~~~

## Technology stack

| Area | Technology | Purpose |
| --- | --- | --- |
| Language | Python 3.10 or 3.11 | Main development language |
| UI | Streamlit | Local browser interface and chat-style flow |
| Speech-to-text | faster-whisper | Local English audio transcription |
| NLP | TF-IDF | Converts text into numerical features |
| ML | Logistic Regression | Selects a broad question path |
| Safety layer | Deterministic Python rules | Routes explicit red flags and medicine requests |
| Data | JSON | Synthetic topics, questions, and routing scenarios |
| Tests | Python unittest | Validates model, conversation, safety, and cleanup behavior |
| Deployment | Docker | Runs the Streamlit app in a container |

## Quick start

### Prerequisites

- Python 3.10 or 3.11
- An internet connection for the first faster-whisper model download
- A modern browser for microphone input

### Windows Command Prompt

~~~
cd /d "C:\path\to\voice-symptom-support-assistant"
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
~~~

If Windows does not recognize python, install Python 3.11 and tick
**Add python.exe to PATH**, then reopen Command Prompt.

### macOS or Linux

~~~
cd voice-symptom-support-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
~~~

Open the URL printed in the terminal, normally http://127.0.0.1:8501.

The default base.en speech model downloads automatically on the first audio
transcription. Typed-text mode works without downloading that model.

### Pre-download the speech model

~~~
python scripts/download_speech_model.py --model base.en
~~~

### Command-line text-only demo

~~~
python cli.py --text "I have a blocked nose and a scratchy throat"
python cli.py --text "I have chest pain and cannot breathe"
~~~

The second command must return emergency-routing text instead of a topic
prediction.

### Tests and data validation

~~~
python -m pip install -r requirements-dev.txt
python scripts/validate_dataset.py
python -m unittest discover -s tests -v
~~~

## Publish this project to GitHub

Use the complete Windows guide in
[docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md). The short version is:

1. On GitHub, create a **new empty repository** named, for example,
   "voice-health-navigator". Do not select "Add a README", "Add .gitignore",
   or "Choose a license"; those files are already in this project.
2. Open Command Prompt inside the extracted project folder and run the
   following commands. Replace "YOUR-USERNAME" with the GitHub username and
   use the repository name chosen in step 1.

~~~
cd /d "C:\path\to\voice-symptom-support-assistant"
git init
git add .
git status
git commit -m "Initial commit: Voice Health Navigator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/voice-health-navigator.git
git push -u origin main
~~~

If "git" is not recognized, install Git for Windows from
[git-scm.com](https://git-scm.com/download/win), then close and reopen Command
Prompt. When GitHub asks you to authenticate, use the browser sign-in flow or
a GitHub personal access token; do not enter a GitHub account password into
the terminal.

The "git status" command is an important check: it shows the exact files that
will be uploaded and confirms that private virtual-environment files, local
speech models, logs, and secrets are excluded by ".gitignore".

## Documentation

| Document | What it explains |
| --- | --- |
| [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md) | Git installation, first push, authentication, common errors, and later updates |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Components, data flow, model boundaries, privacy behavior, and safety precedence |
| [docs/TESTING.md](docs/TESTING.md) | Dataset validation, unit-test commands, and test scope |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Safe contributions, branch workflow, review checklist, and data rules |
| [SECURITY.md](SECURITY.md) | Security and privacy reporting guidance |
| [CHANGELOG.md](CHANGELOG.md) | Public release history |

## Data

The project includes only small, synthetic, project-authored JSON files:

| File | Role |
| --- | --- |
| data/symptom_topics.json | Broad text-topic examples for the TF-IDF baseline |
| data/follow_up_questions.json | Fixed, visible guided-question flow and safety mappings |
| data/demo_navigation_scenarios.json | Synthetic conversation-routing scenarios |

Read [data/DATA_CARD.md](data/DATA_CARD.md) and
[data/README.md](data/README.md) before replacing or extending this data.

### Optional external resources

These resources are optional and are not required for the app to run:

| Resource | Safe project use |
| --- | --- |
| [MedlinePlus Health Topic XML](https://medlineplus.gov/xml.html) | Add source-linked educational topic cards after human review and attribution |
| [MeSH](https://www.nlm.nih.gov/databases/download/mesh.html) | Normalise symptom terms or topic lookup only |
| [Synthea](https://github.com/synthetichealth/synthea) | Generate synthetic UI test fixtures only |
| [LibriSpeech](https://www.openslr.org/12/) or [Mozilla Common Voice](https://commonvoice.mozilla.org/en/datasets) | General speech-recognition evaluation only |

Do not use health datasets, online drug labels, or synthetic records to infer a
medicine or dose. Do not commit identifiable health data, restricted data, or
unlicensed audio.

## Repository layout

~~~
app.py                         Streamlit multi-turn UI
cli.py                         Single-turn text or audio command-line demo
src/
  classifier.py                Reproducible broad topic matcher
  conversation.py              Question flow, answer validation, factual summary
  triage.py                    Safety and medicine-request checks
  speech.py                    Temporary-file faster-whisper wrapper
  content.py                   Fixed escalation and educational wording
data/
  symptom_topics.json          Synthetic ML examples
  follow_up_questions.json    Synthetic question-bank data
  demo_navigation_scenarios.json
  DATA_CARD.md                 Intended use and limitations
tests/                         Unit tests
Dockerfile                     Container launch configuration
.github/                       Continuous integration and GitHub templates
docs/                          GitHub, architecture, and testing documentation
CONTRIBUTING.md                Contribution and safety rules
SECURITY.md                    Security and privacy reporting policy
CHANGELOG.md                   Release history
~~~

## Docker

~~~
docker build -t voice-health-navigator .
docker run --rm -p 8501:8501 voice-health-navigator
~~~

The image needs internet access when it downloads a Whisper model for the first
time. For an offline deployment, pre-download the model into models/whisper
before building and remove models from .dockerignore.

## Project provenance

The concept comes from B.Tech coursework in AI in Speech Processing. This
repository is a later reconstruction created in 2026 with a 2024-era local
Python stack, improved tests, and explicit safety guardrails. It should be
presented as a reconstruction, not as the original historical coursework
submission.

## Licence

The code and project-authored synthetic data are released under the
[MIT License](LICENSE). Third-party models and optional resources retain their
own licences and terms.
