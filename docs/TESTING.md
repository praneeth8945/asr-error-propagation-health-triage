# Testing guide

## Install test dependencies

Use a virtual environment and install the development dependency file:

~~~bash
python -m pip install -r requirements-dev.txt
~~~

## Run the checks

~~~bash
python scripts/validate_dataset.py
python -m unittest discover -s tests -v
~~~

The same commands run automatically in GitHub Actions for pushes and pull
requests through ".github/workflows/tests.yml".

## What is covered

| Area | Example behavior checked |
| --- | --- |
| Classifier | The broad-topic matcher trains from the bundled synthetic data and returns a valid navigation label |
| Conversation flow | Fixed questions are loaded, answers are validated, and factual notes include user-entered information |
| Safety routing | Explicit emergency, concerning, and medicine/dose-request wording takes priority over normal topic routing |
| Speech wrapper | Temporary audio files are cleaned up after transcription handling |
| Dataset | JSON structure, known labels, question paths, and demo scenarios remain valid |

## Manual smoke test

After starting the app with "python -m streamlit run app.py":

1. Select the consent checkbox.
2. Enter a non-urgent typed concern such as "I have a blocked nose and a
   scratchy throat."
3. Confirm that the app shows an editable transcript and follows a fixed
   question path.
4. Complete the questions and confirm that the final note contains the
   entered details without a diagnosis or prescription.
5. Start a new check-in and enter a clearly urgent phrase. Confirm that a
   warning appears and the standard question flow stops.
6. Try a request for a medicine or dose. Confirm that the app maintains its
   boundary rather than making a recommendation.

## Important limitation

Passing these tests only shows that the software matches the documented
educational behavior. The tests do not prove medical safety, clinical
accuracy, legal compliance, or suitability for real patient use.
