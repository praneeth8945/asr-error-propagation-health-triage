# Data notes

This repository deliberately ships only small, project-authored synthetic data:

| File | Purpose |
| --- | --- |
| symptom_topics.json | Demonstrates broad educational text-topic matching. |
| follow_up_questions.json | Visible, fixed question flow for the multi-turn UI. |
| demo_navigation_scenarios.json | Synthetic examples for testing conversation routing. |

It contains no patient data, clinical recordings, medicine labels, or
prescribing data.

The included examples exist only to demonstrate preprocessing, a reproducible
TF-IDF classifier, safe question routing, and a factual handoff summary. They
cannot validate medical accuracy and must not be used for diagnosis, treatment,
medicine selection, or dosage decisions.

See [DATA_CARD.md](DATA_CARD.md) for intended use, fields, and limitations.

## Optional external resources

| Resource | Suitable use in this project | Access and licence notes |
| --- | --- | --- |
| [MedlinePlus Health Topic XML](https://medlineplus.gov/xml.html) | Source-linked educational health-topic cards after a human review | Health-topic summaries are public domain; follow the [content-use guidance](https://medlineplus.gov/about/using/usingcontent/) and exclude copyrighted A.D.A.M. and ASHP content. |
| [MeSH](https://www.nlm.nih.gov/databases/download/mesh.html) | Optional symptom-term normalisation and topic lookup | Acknowledge the U.S. National Library of Medicine and state the version used. It is not clinical validation. |
| [Synthea](https://github.com/synthetichealth/synthea) | Optional synthetic UI test fixtures | Apache-2.0; use only for non-real test data, not model targets or prescribing logic. |
| [LibriSpeech](https://www.openslr.org/12/) | General automatic-speech-recognition evaluation | CC BY 4.0; it is not medical speech and should not be committed to this repository. |
| [Mozilla Common Voice](https://commonvoice.mozilla.org/en/datasets) | General ASR evaluation | Download separately and follow the current dataset terms. It is not clinical speech. |

Record the resource version, access date, licence, preprocessing steps, and
split strategy if you conduct further experiments. Never commit identifiable
health records, restricted data, or unlicensed audio.

