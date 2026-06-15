import streamlit as st
import random
from pathlib import Path
from projects.mental_health_bot.tracker import create_session
from projects.mental_health_bot.chat_engine import process_message
from projects.mental_health_bot.report_view import render_report

from projects.mental_health_bot.scorer import (
    calculate_phq9,
    calculate_gad7,
    get_phq9_severity,
    get_gad7_severity,
    get_risk_tier,
    get_recommendation,
)

# =====================================
# LOAD CSS
# =====================================
def load_css():
    with open("assets/main.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"]{
        background: linear-gradient(
            180deg,
            #F7F1FF 0%,
            #E7D9FF 50%,
            #F9F6FF 100%
        );
    }
    </style>
    """,
    unsafe_allow_html=True)


# =====================================
# WELCOME SCREEN
# =====================================

def render_welcome():
    quotes = [
        "🤗 Every journey begins with a conversation.",
        "💜 It's okay to not feel okay every day.",
        "🌿 You don't have to carry everything alone.",
        "🧠 Understanding yourself is a form of strength."
    ]

    # quotes = [
    #     "🌱 Terima kasih sudah datang hari ini.",
    #     "💜 Tidak semua hari harus sempurna.",
    #     "🤗 Kadang kita hanya butuh didengar.",
    #     "🌿 Aku siap menemanimu berbicara."
    # ]

    st.markdown(
        """
        <div class="temanai-wrapper">
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
        </div>
        """, unsafe_allow_html=True)

    # ========= MASCOT =========

    left, center, right = st.columns([3, 2, 3])

    with center:

        st.image(
            "assets/mascot.PNG",
            width=220
        )

    # ========= TITLE =========
    st.markdown(
    """
    <h1 class="temanai-title"
        style="
            color:#6C4AB6;
            text-align:center;
        ">
        🌱 TemanAI
    </h1>
    """,
    unsafe_allow_html=True
    )

    # st.markdown(
    #     """
    #     <h1 class="temanai-title">
    #         🌱 TemanAI
    #     </h1>
    #     """,
    #     unsafe_allow_html=True
    # )

    # ========= SUBTITLE =========

    st.markdown(
        """
        <p class="temanai-subtitle">
            A safe space to share your thoughts,
feel heard, and better understand yourself.
        </p>
        """,
        unsafe_allow_html=True
    )

    # ========= QUOTE =========

    st.markdown(
        f"""
        <div class="temanai-quote">
            {random.choice(quotes)}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ========= FEATURE CARDS =========

    col1, col2, col3 = st.columns(3)

    with col1:
        

        st.markdown(
            """
            <div class="temanai-card">
                <h3>❤️</h3>
                <b>Safe Space</b>
                <p>
                    Share your thoughts freely
                    without fear of judgment.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown("""
            <div class="temanai-card">
                <div class="temanai-icon">🛡️</div>
                <b>Privacy First</b>
                <p>
                    Your conversations stay private
                    and secure within the session.
                </p>
            </div>
            """, unsafe_allow_html=True)

    with col3:

        st.markdown(
            """
            <div class="temanai-card">
                <h3>🧠</h3>
                <b>AI Companion</b>
                <p>Combining Machine Learning and Large Language Models[LLM]
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ========= START BUTTON =========

    if st.button(
        "💬 ✨ Begin Your Journey",
        use_container_width=True
    ):

        st.session_state.teman_ai_started = True

        st.rerun()

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True
    )
# =====================================
# CHAT PAGE
# =====================================
def render_chat():

    st.markdown(
        """
        <h1 class="temanai-title"
        style="
            color:#6C4AB6;
            text-align:center;
        ">
            💬 TemanAI
        </h1>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # INIT WARAS SESSION
    # =====================================

    if "waras_state" not in st.session_state:

        st.session_state.waras_state = create_session()

    # =====================================
    # INIT CHAT HISTORY
    # =====================================

    if "messages" not in st.session_state:

        st.session_state.messages = [

            {
                "role": "assistant",
                "content": """
Hai! Aku TemanAI 🌱

Aku siap mendengarkan.

Gimana hari-harimu belakangan ini?

Bebas cerita apa aja ya 😊
                """
            }

        ]

    # =====================================
    # SHOW CHAT HISTORY
    # =====================================

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # =====================================
    # USER INPUT
    # =====================================
    # st.write("CHAT INPUT SHOULD APPEAR BELOW 👇")
    
    st.markdown(
    """
    <p class="temanai-debug">
        CHAT INPUT SHOULD APPEAR BELOW 👇
    </p>
    """,
    unsafe_allow_html=True
    )
    user_input = st.chat_input(
        "Share what's on your mind..."
    )

    # =====================================
    # SEND MESSAGE
    # =====================================

    if user_input:

        # tampilkan pesan user

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        # panggil engine chatbot

        response, updated_state = process_message(
            user_input,
            st.session_state.waras_state
        )

        # update state

        st.session_state.waras_state = updated_state

        # simpan response bot

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.rerun()

    # =====================================
    # NEW SESSION
    # =====================================

    # st.divider()
    # col1, col2, col3 = st.columns([2, 3, 2])
    # with col2:
    #     if st.button(
    #         "🌱 Start New Check-In",
    #         use_container_width=True
    #     ):
    #         if "messages" in st.session_state:
    #             del st.session_state.messages
    #         if "waras_state" in st.session_state:
    #             del st.session_state.waras_state
    #         st.session_state.teman_ai_started = False
    #         st.rerun()
    if st.button(
        "📊 View Assessment Report",
        use_container_width=True
    ):

        state = st.session_state.waras_state

        phq9 = calculate_phq9(state)

        gad7 = calculate_gad7(state)

        risk_tier = get_risk_tier(
            state,
            phq9,
            gad7
        )

        recommendation = get_recommendation(
            risk_tier,
            phq9,
            gad7
        )

        render_report(
            phq9_score=phq9["score"],
            phq9_severity=get_phq9_severity(
                phq9["score"]
            ),
            gad7_score=gad7["score"],
            gad7_severity=get_gad7_severity(
                gad7["score"]
            ),
            risk_tier=risk_tier,
            recommendation=recommendation,
        )

# =====================================
# MAIN
# =====================================
def run():
    load_css()
    if "teman_ai_started" not in st.session_state:
        st.session_state.teman_ai_started = False
    if st.session_state.teman_ai_started:
        render_chat()
    else:
        render_welcome()