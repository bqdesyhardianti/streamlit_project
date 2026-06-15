# projects/mental_health_bot/report_view.py
import streamlit as st

def render_report(
    phq9_score,
    phq9_severity,
    gad7_score,
    gad7_severity,
    risk_tier,
    recommendation,
):

    st.divider()

    st.markdown(
        """
        <h2 style="
            text-align:center;
            color:#6C4AB6;
            margin-bottom:20px;
        ">
            🧠 Mental Wellness Report
        </h2>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "PHQ-9",
            f"{phq9_score}/27",
            phq9_severity
        )

    with col2:

        st.metric(
            "GAD-7",
            f"{gad7_score}/21",
            gad7_severity
        )

    with col3:

        st.metric(
            "Risk Tier",
            risk_tier
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(recommendation)

    st.markdown("<br>", unsafe_allow_html=True)

    st.success(
        """
🌱 Remember:

This assessment is not a clinical diagnosis.

It is intended to help you reflect on your current emotional wellbeing
and identify whether additional support may be helpful.
        """
    )
# import streamlit as st


# def render_report(
#     phq9_score,
#     phq9_severity,
#     gad7_score,
#     gad7_severity,
#     risk_tier,
#     recommendation
# ):

#     st.divider()

#     st.subheader("🧠 Mental Wellness Summary")

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.metric(
#             "PHQ-9",
#             phq9_score,
#             phq9_severity
#         )

#     with col2:
#         st.metric(
#             "GAD-7",
#             gad7_score,
#             gad7_severity
#         )

#     with col3:
#         st.metric(
#             "Risk Tier",
#             risk_tier
#         )

#     st.divider()

#     st.markdown("### 🌱 Recommendation")

#     st.info(recommendation)