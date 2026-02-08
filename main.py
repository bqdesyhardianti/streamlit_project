import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import datetime
from modules import about_me, dunnhumby_dashboard, churn_analysis_dashboard
from modules import predictions,contact  # pastikan path sesuai


st.set_page_config(
    page_title="My Portfolio 🚀",
    page_icon="💼",
    layout="wide"
)

# -----------------------------
# Sidebar menu (tetap interaktif & semua opsi terlihat)
# -----------------------------
st.sidebar.markdown("## 🗂 Menu")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["Home", "About Me", "Projects", "Predictions", "Kontak"]
)

# -----------------------------
# Render halaman sesuai menu
# -----------------------------
if menu == "Home":
    st.title("Hello! 👋")
    st.subheader("Welcome to my portfolio")
    st.write("""
    My name is BQ Desy Hardianti. I am a big data analytics enthusiast with experience in data science, digital marketing, and SEO.  
    I work well independently or in teams, delivering professional, data-driven solutions.
    """)

elif menu == "About Me":
    about_me.tentang_saya()

elif menu == "Projects":
    st.subheader("Projects")
    project_choice = st.selectbox(
        "Pilih Project",
        ["Dunnhumby Customer Insight", "Churn Analysis"]
    )

    if project_choice == "Dunnhumby Customer Insight":
        dunnhumby_dashboard.show()
    elif project_choice == "Churn Analysis":
        churn_analysis_dashboard.show()

elif menu == "Predictions":
    st.header("Predictions")
    predictions.show_prediction()
    # st.write("Contoh prediksi ML")


elif menu == "Kontak":
    my_contact = contact.Kontak(
        nama="BQ Desy Hardianti",
        email="desyhamkar@gmail.com",
        github="https://github.com/bqdesyhardianti",
        linkedin="https://www.linkedin.com/in/bq-desy-hardianti/"
    )
    my_contact.show()