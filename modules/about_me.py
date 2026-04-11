import streamlit as st
from PIL import Image

def tentang_saya():
    st.subheader("Hi, I'm BQ Desy 👋")

    st.write("""
    I am a Big Data Analytics enthusiast with experience in Data Science, Digital Marketing, and SEO.  
    I work both independently and in teams to deliver professional, data-driven solutions.
    """)

    # =========================
    # 🔗 CONTACT & SOCIAL LINKS
    # =========================
    st.markdown("### 🌐 Connect with Me")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            "[📧 Email](mailto:desyhamkar@gmail.com)"
        )

    with col2:
        st.markdown(
            "[💼 LinkedIn](https://www.linkedin.com/in/bq-desy-hardianti/)"
        )

    with col3:
        st.markdown(
            "[💻 GitHub](https://github.com/bqdesyhardianti/)"
        )

    with col4:
        st.markdown(
            "[📊 Tableau](https://public.tableau.com/app/profile/bqdesyh/vizzes)"
        )

    # =========================
    # EXPERIENCES
    # =========================
    st.markdown("### 💼 Experiences")
    st.markdown("""
    1. Contributed to global pricing initiatives, built data pipelines, and delivered insights for strategic decision-making.  
    2. Delivered data analysis projects, predictive modeling, and dashboards to inform client strategies.
    """)

    # =========================
    # SKILLS
    # =========================
    st.markdown("### 🛠️ Skills")
    st.write("""
    Python | SQL | Machine Learning | Data Visualization | Product Recommender Systems | GCP
    """)

    # =========================
    # DASHBOARD SHOWCASE
    # =========================
    st.markdown("### 📊 My Dashboards & Projects")

    dashboard_links = [
        {
            "name": "📈 Product Recommender System",
            "link": "https://your-streamlit-app-link"
        },
        {
            "name": "📊 Sales Dashboard",
            "link": "https://your-tableau-dashboard"
        },
        {
            "name": "🧠 Mental Health Analytics",
            "link": "https://your-project-link"
        }
    ]

    for dash in dashboard_links:
        st.markdown(f"- [{dash['name']}]({dash['link']})")