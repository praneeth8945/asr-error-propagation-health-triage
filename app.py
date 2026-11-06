"""Streamlit UI for a safe, multi-turn voice symptom check-in demonstration."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.conversation import (
    SKIPPED_RESPONSE,
    ConversationOutcome,
    GuidedConversation,
    begin_guided_conversation,
    record_response,
)
from src.speech import TranscriptionError, transcribe_audio


st.set_page_config(
    page_title="Voice Health Navigator",
    page_icon="🩺",
    layout="centered",
)


def _audio_suffix(name: str | None) -> str:
    suffix = Path(name or "recording.wav").suffix.lower()
    return suffix if suffix else ".wav"


def _microphone_input(label: str):
    """Use the stable or 1.39-era experimental microphone widget.

    Streamlit 1.39 exposes experimental_audio_input, while later releases use
    audio_input. Supporting both keeps the pinned 2024-era dependency usable.
    """

    stable_widget = getattr(st, "audio_input", None)
    if callable(stable_widget):
        return stable_widget(label)

    experimental_widget = getattr(st, "experimental_audio_input", None)
    if callable(experimental_widget):
        return experimental_widget(label)

    st.info(
        "Microphone recording is unavailable in this Streamlit version. "
        "Use audio upload or typed text, or reinstall the project requirements."
    )
    return None


def _clear_session() -> None:
    """Clear locally-held session state, including every conversation response."""

    for key in list(st.session_state):
        if key in {"transcript", "conversation", "last_audio_name"} or key.startswith(
            "answer_"
        ):
            st.session_state.pop(key, None)


def _clear_conversation_for_edited_transcript() -> None:
    st.session_state.pop("conversation", None)


def _render_outcome(outcome: ConversationOutcome) -> None:
    if outcome.triage.level == "emergency":
        st.error(
            "Emergency wording or an emergency warning answer was detected. "
            "Do not wait for this app to assess the situation."
        )
        for flag in outcome.triage.flags:
            st.write(f"• {flag.title}: {flag.message}")
    elif outcome.triage.level == "prompt":
        st.warning(
            "Concerning wording or an answer needing professional assessment was detected."
        )
        for flag in outcome.triage.flags:
            st.write(f"• {flag.title}: {flag.message}")
    elif outcome.medication_request_detected:
        st.warning(
            "This app cannot select a medicine, prescribe treatment, or calculate a dose."
        )
    elif outcome.topic_label:
        st.success(
            f"Broad educational topic: {outcome.topic_label}. This is not a diagnosis."
        )
    else:
        st.info(
            "No clear educational topic was found. That is uncertainty, not reassurance."
        )

    st.subheader("Recommended next step")
    for step in outcome.next_steps:
        st.write(f"• {step}")

    st.subheader("Clinician-ready factual note")
    st.caption(
        "This note only repeats what was entered or selected. It adds no diagnosis or treatment."
    )
    st.code(outcome.clinician_note, language=None)
    st.download_button(
        "Download clinician note",
        data=outcome.clinician_note,
        file_name="voice_health_navigator_note.txt",
        mime="text/plain",
    )


def _render_guided_conversation(conversation: GuidedConversation) -> None:
    """Render each assistant question and user response in a chat-like UI."""

    with st.chat_message("user"):
        st.write(conversation.initial.transcript)

    if conversation.is_initially_blocked:
        with st.chat_message("assistant"):
            st.write(
                "The initial message needs a safety response, so I will not ask more questions."
            )
        outcome = conversation.outcome()
        if outcome:
            _render_outcome(outcome)
        return

    with st.chat_message("assistant"):
        st.write(
            "I can ask a short set of fixed follow-up questions to organise a factual note. "
            "The answers are not used to prescribe medicines or doses."
        )

    for answer in conversation.answers:
        with st.chat_message("assistant"):
            st.write(answer.prompt)
        with st.chat_message("user"):
            st.write(answer.response)

    outcome = conversation.outcome()
    if outcome:
        with st.chat_message("assistant"):
            st.write("The check-in is complete.")
        _render_outcome(outcome)
        return

    question = conversation.current_question
    if question is None:
        return

    st.progress(len(conversation.answers) / len(conversation.questions))
    with st.chat_message("assistant"):
        st.write(question.prompt)
        st.caption("Choose the closest answer. You can skip any question.")

        key_prefix = f"answer_{question.identifier}_{len(conversation.answers)}"
        if question.input_type == "choice":
            response = st.selectbox(
                "Your response",
                options=("Choose an answer...",) + question.choices + (SKIPPED_RESPONSE,),
                key=f"{key_prefix}_choice",
                label_visibility="collapsed",
            )
        else:
            response = st.text_area(
                "Your optional note",
                max_chars=question.max_length,
                key=f"{key_prefix}_text",
                placeholder="Do not include names, contact details, or identifiers.",
                label_visibility="collapsed",
            )
            skip = st.checkbox("Skip this optional note", key=f"{key_prefix}_skip")
            if skip:
                response = SKIPPED_RESPONSE

        if st.button("Continue", key=f"{key_prefix}_continue"):
            if response == "Choose an answer...":
                st.warning("Choose an answer or skip this question.")
                return
            try:
                st.session_state["conversation"] = record_response(
                    conversation,
                    question.identifier,
                    response,
                )
                st.rerun()
            except ValueError as error:
                st.warning(str(error))


def _render_intake(model_size: str, consent: bool) -> None:
    """Render initial voice/text input until a guided conversation begins."""

    st.subheader("1. Describe the concern")
    st.markdown(
        "You may record, upload, or type a short description. Review the transcript "
        "before starting the question flow."
    )
    recorded_audio = _microphone_input("Record a short description")
    uploaded_audio = st.file_uploader(
        "Or upload audio",
        type=["wav", "mp3", "m4a", "mp4", "webm", "ogg", "flac"],
        help="The file is used only in a temporary local file during transcription.",
    )

    chosen_audio = recorded_audio if recorded_audio is not None else uploaded_audio
    if chosen_audio is not None:
        st.audio(chosen_audio)
        if st.button("Transcribe audio", disabled=not consent):
            try:
                with st.spinner(
                    "Transcribing locally. The first run may download a speech model."
                ):
                    transcription = transcribe_audio(
                        chosen_audio.getvalue(),
                        suffix=_audio_suffix(getattr(chosen_audio, "name", None)),
                        model_size=model_size,
                    )
                st.session_state["transcript"] = transcription.text
                _clear_conversation_for_edited_transcript()
                st.session_state["last_audio_name"] = getattr(
                    chosen_audio, "name", "recording"
                )
                st.success("Transcription complete. Please review and correct it below.")
            except TranscriptionError as error:
                st.error(str(error))

    transcript = st.text_area(
        "Editable transcript or typed description",
        key="transcript",
        max_chars=1_200,
        height=150,
        placeholder="Example: I have had a blocked nose and scratchy throat since yesterday.",
        on_change=_clear_conversation_for_edited_transcript,
    )

    if st.button(
        "Start guided check-in",
        type="primary",
        disabled=not consent or not transcript.strip(),
    ):
        try:
            st.session_state["conversation"] = begin_guided_conversation(transcript)
            st.rerun()
        except ValueError as error:
            st.error(str(error))


def main() -> None:
    if "transcript" not in st.session_state:
        st.session_state["transcript"] = ""

    st.title("Voice Health Navigator")
    st.caption(
        "Educational speech-processing prototype • guided questions • no diagnosis, medicines, or doses"
    )
    st.error(
        "For emergencies, do not use this app. If you may be in immediate danger, "
        "contact local emergency services now."
    )

    with st.sidebar:
        st.header("Session controls")
        model_size = st.selectbox(
            "Speech model",
            options=("base.en", "tiny.en"),
            help="The model downloads once on first audio use and is stored locally.",
        )
        st.caption("Audio and text are not logged or saved by this app.")
        st.caption(
            "Exact body weight, medicine lists, allergies, and medical history are not "
            "requested or used to choose treatment."
        )
        if st.button("Clear all session data"):
            _clear_session()
            st.rerun()

    consent = st.checkbox(
        "I understand this is an academic demo, not a medical service. It cannot diagnose conditions, prescribe medicines, or calculate doses."
    )

    conversation = st.session_state.get("conversation")
    if isinstance(conversation, GuidedConversation):
        st.subheader("Guided conversation")
        _render_guided_conversation(conversation)
        if conversation.outcome() is not None and st.button("Start a new check-in"):
            _clear_session()
            st.rerun()
    else:
        _render_intake(model_size, consent)

    with st.expander("Privacy, scope, and limitations"):
        st.markdown(
            "- No raw audio, transcript, or follow-up answer is written to application logs or files.\n"
            "- The question bank and scenarios are synthetic academic data.\n"
            "- The app checks each turn for a limited set of explicit caution phrases and selected warning answers.\n"
            "- High-level context can only route to professional assessment; it never determines treatment.\n"
            "- It cannot assess body weight, age, pregnancy, allergies, current medicines, medical history, examinations, or tests.\n"
            "- It never recommends a medicine, treatment, or dosage."
        )


if __name__ == "__main__":
    main()
