"""Fixed, non-prescriptive wording displayed by the application."""

from __future__ import annotations


GENERAL_GUIDANCE: tuple[str, ...] = (
    "Write down when the symptoms started, how they are changing, and any possible triggers.",
    "Use the corrected transcript as a short note if you contact a healthcare professional.",
    "Seek professional advice if symptoms are new, persistent, worsening, or concerning to you.",
)

GUIDANCE_BY_TOPIC: dict[str, tuple[str, ...]] = {
    "headache_like": (
        "Note the onset, location, pattern, and anything that seems to make it better or worse.",
        "Avoid driving or hazardous activity if you feel unwell, dizzy, or unable to concentrate.",
        "Seek professional assessment if the symptom is new, worsening, severe, or disruptive.",
    ),
    "upper_respiratory_like": (
        "Track the onset, temperature changes, and whether the symptoms are improving or worsening.",
        "Consider reducing close contact with others if you feel unwell and follow applicable local guidance.",
        "Seek professional assessment if symptoms are worsening, persistent, or concerning.",
    ),
    "cough_like": (
        "Record when the cough started, whether it is dry or productive, and what seems to trigger it.",
        "Seek professional assessment if the cough is worsening, persistent, or interfering with daily life.",
        "Use the emergency services message immediately if breathing becomes difficult.",
    ),
    "digestive_like": (
        "Track the timing of discomfort, recent food or drink, and whether you can keep fluids down.",
        "Seek professional assessment if symptoms persist, worsen, or affect your ability to function.",
        "Use the prompt-care message immediately if blood-related symptoms or severe pain are present.",
    ),
    "skin_irritation_like": (
        "Record the location, onset, appearance, and any recent product or environmental exposures.",
        "Avoid using the app to decide whether a product or medicine is safe for you.",
        "Seek professional assessment if the area spreads quickly, becomes severe, or concerns you.",
    ),
    "urinary_like": (
        "Record when the symptoms began and whether they are worsening or accompanied by other symptoms.",
        "Seek professional assessment promptly rather than using this app to select treatment.",
        "A clinician or pharmacist needs your individual history before discussing medicines.",
    ),
    "fever_body_ache_like": (
        "Track the onset, temperature if you have measured it, and changes in the pattern of aches or fatigue.",
        "Use the corrected transcript to describe the symptom pattern to a healthcare professional.",
        "Seek professional assessment if symptoms worsen, persist, or concern you.",
    ),
}

EMERGENCY_ACTION: tuple[str, ...] = (
    "Do not rely on this application for an emergency assessment.",
    "Contact local emergency services now, or ask someone nearby to help you do so.",
    "If possible, do not stay alone while arranging urgent help.",
)

PROMPT_ACTION: tuple[str, ...] = (
    "This prototype cannot safely assess the wording that was detected.",
    "Contact a qualified healthcare professional or appropriate urgent-care service promptly.",
    "Do not use this application to delay seeking professional advice.",
)

MEDICATION_ACTION: tuple[str, ...] = (
    "This prototype cannot recommend a medicine or calculate a dose.",
    "Medicine selection and dosing depend on factors such as age, allergies, other medicines, and health history.",
    "Ask a qualified doctor or pharmacist for personalised medicine advice.",
)


def guidance_for_topic(topic_id: str | None) -> tuple[str, ...]:
    """Return only fixed educational next steps for a broad demo topic."""

    if topic_id is None:
        return GENERAL_GUIDANCE
    return GUIDANCE_BY_TOPIC.get(topic_id, GENERAL_GUIDANCE)

