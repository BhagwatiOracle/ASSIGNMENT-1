import streamlit as st
from datetime import date

from rag import ask


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Merchant Policy Assistant",
    page_icon="💳",
    layout="wide"
)


# -----------------------------
# Title
# -----------------------------

st.title("💳 Merchant Policy Assistant")

st.write(
    "Ask questions about merchant fees, refunds, "
    "settlements and limits."
)


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("Policy Settings")

as_of_date = st.sidebar.date_input(
    "Policy date",
    value=date(2026, 8, 15)
)


# -----------------------------
# Sample questions
# -----------------------------

st.subheader("Ask a question")

sample_questions = [
    "When does a small merchant receive UPI money?",
    "What is the MDR for a large merchant?",
    "Does GST apply to MDR?",
    "I requested a refund 3 hours after the sale. "
    "Do I get the MDR back?",
    "What does the FAQ say about the MDR cap?",
    "Can a merchant receive same-day settlement?"
]


question = st.selectbox(
    "Choose a sample question",
    sample_questions
)


# -----------------------------
# Ask button
# -----------------------------

if st.button("🔍 Ask"):

    with st.spinner("Searching policy documents..."):

        result = ask(
            question,
            str(as_of_date)
        )


    # -------------------------
    # Status
    # -------------------------

    if result["status"] == "ANSWERED":

        st.success("ANSWERED")

    elif result["status"] == "CONFLICT_RESOLVED":

        st.info("CONFLICT_RESOLVED")

    else:

        st.warning("CANNOT_ANSWER")


    # -------------------------
    # Answer
    # -------------------------

    st.subheader("Answer")

    st.write(result["answer"])


    # -------------------------
    # Citations
    # -------------------------

    st.subheader("📚 Sources")

    for citation in result["citations"]:

        st.write(
            f"• {citation}"
        )