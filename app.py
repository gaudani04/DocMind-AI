import streamlit as st

from rag import (
    process_pdf,
    ask_question,
    generate_quiz,
    generate_flashcards
)

st.title(
    "DocMind AI - Chat with PDF"
)


# ==========================
# Upload PDF
# ==========================
uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type="pdf"
)


# ==========================
# Process PDF
# ==========================
if uploaded_file:

    if st.sidebar.button(
        "Process PDF"
    ):

        pdf_name = process_pdf(
            uploaded_file
        )

        st.session_state.pdf_name = (
            pdf_name
        )

        st.sidebar.success(
            "PDF processed!"
        )


# ==========================
# Generate Quiz
# ==========================
if "pdf_name" in st.session_state:

    if st.sidebar.button(
        "Generate Quiz"
    ):

        with st.spinner(
            "Generating quiz..."
        ):

            quiz = generate_quiz(
                st.session_state.pdf_name
            )

            st.session_state.quiz = (
                quiz
            )


# Show quiz if exists
if "quiz" in st.session_state:

    st.subheader(
        "Generated Quiz"
    )

    st.write(
        st.session_state.quiz
    )

if "pdf_name" in st.session_state:

    if st.sidebar.button(
        "Generate Flashcards"
    ):

        with st.spinner(
            "Generating flashcards..."
        ):

            flashcards = generate_flashcards(
                st.session_state.pdf_name
            )

            st.session_state.flashcards = (
                flashcards
            )
if "flashcards" in st.session_state:

    st.subheader(
        "Study Flashcards"
    )

    st.write(
        st.session_state.flashcards
    )
# ==========================
# Chat Memory UI
# ==========================
if "messages" not in st.session_state:

    st.session_state.messages = []


for msg in st.session_state.messages:

    st.chat_message(
        msg["role"]
    ).write(
        msg["content"]
    )


# ==========================
# Chat Input
# ==========================
user_input = st.chat_input(
    "Ask something..."
)


if (
    user_input
    and "pdf_name" in st.session_state
):

    # User message
    st.chat_message(
        "user"
    ).write(
        user_input
    )

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # AI response
    with st.spinner(
        "Thinking..."
    ):

        response = ask_question(
            user_input,
            st.session_state.pdf_name
        )

    st.chat_message(
        "assistant"
    ).write(
        response
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )