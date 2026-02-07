import streamlit as st
from PIL import Image

def tentang_saya():
    # Load foto
    image = Image.open("/Users/bqdesy/streamlit_project/images/DSC05557.jpg")  # ganti dengan nama file fotomu

    # Buat layout 2 kolom
    col1, col2 = st.columns([1, 2])  # col1 untuk foto, col2 untuk teks

    with col1:
        st.image(image, width=400)  # foto di kiri

    with col2:
        st.subheader("Hi, I'm BQ Desy Hardianti 👋")
        st.write("""
        I am a big data analytics enthusiast with experience in data science, digital marketing, and SEO.  
        I work well independently or in teams, delivering professional, data-driven solutions.
        """)

        # Ringkasan pengalaman
        st.markdown("### Experiences")
        st.markdown("""
  
        1. Contributed to global pricing initiatives, built data pipelines, and delivered insights for strategic decision-making.
        2. Delivered data analysis projects, predictive modeling, and dashboards to inform client strategies.
        """)

        # Skill singkat (opsional)
        st.markdown("### Skills")
        st.write("Python | Git | Machine Learning | Data Visualization | Product Recommender Systems")

