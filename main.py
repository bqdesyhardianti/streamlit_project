import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import datetime
from modules import about_me, dunnhumby_dashboard, churn_analysis_dashboard
from modules import predictions  # pastikan path sesuai


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
    I am a big data analytics enthusiast with experience in data science, digital marketing, and SEO.  
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
    st.header("Kontak")
    st.write("📧 Email: desyhamkar@gmail.com")

# st.set_page_config(
#     page_title="My Portfolio 🚀",
#     page_icon="💼",
#     layout="wide"
# )

# # -----------------------------
# # Layout utama: kolom kiri untuk menu, kanan untuk konten
# # -----------------------------
# col1, col2 = st.columns([1, 4])

# with col1:
#     st.markdown("## 🗂 Menu")
#     # Radio button di kiri, selalu terlihat semua opsi
#     menu = st.radio(
#         "Pilih Halaman:",
#         ["Home", "About Me", "Projects", "Predictions", "Kontak"]
#     )

# with col2:
#     # -----------------------------
#     # Render halaman sesuai pilihan
#     # -----------------------------
#     if menu == "Home":
#         st.title("Hello! 👋")
#         st.subheader("Welcome to my portfolio")
#         st.write("""
#         I am a big data analytics enthusiast with experience in data science, digital marketing, and SEO.  
#         I work well independently or in teams, delivering professional, data-driven solutions.
#         """)

#     elif menu == "About Me":
#         about_me.tentang_saya()

#     elif menu == "Projects":
#         st.subheader("Projects")
#         project_choice = st.selectbox(
#             "Pilih Project",
#             ["Dunnhumby Customer Insight", "Churn Analysis"]
#         )

#         if project_choice == "Dunnhumby Customer Insight":
#             dunnhumby_dashboard.show()
#         elif project_choice == "Churn Analysis":
#             churn_analysis_dashboard.show()

#     elif menu == "Predictions":
#         st.header("Predictions")
#         st.write("Contoh prediksi ML")

#     elif menu == "Kontak":
#         st.header("Kontak")
#         st.write("📧 Email: desyhamkar@gmail.com")


# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.figure_factory as ff
# import datetime
# from modules import about_me, dunnhumby_dashboard, churn_analysis_dashboard

# st.set_page_config(
#     page_title="My Portfolio 🚀",
#     page_icon="💼",
#     layout="wide"
# )

# # -----------------------------
# # Sidebar menu
# # -----------------------------
# st.sidebar.markdown("## 🗂 Menu")
# menu = st.sidebar.selectbox(
#     "Pilih Halaman",
#     ["Home", "About Me", "Projects", "Predictions", "Kontak"]
# )

# # -----------------------------
# # Render halaman sesuai menu
# # -----------------------------
# if menu == "Home":
#     st.title("Hello! 👋")
#     st.subheader("Welcome to my portfolio")
#     st.write("""
#         I am a big data analytics enthusiast with experience in data science, digital marketing, and SEO.  
#         I work well independently or in teams, delivering professional, data-driven solutions.
#         """)

# elif menu == "About Me":
#     about_me.tentang_saya()

# elif menu == "Projects":
#     st.subheader("Projects")
#     project_choice = st.selectbox(
#         "Pilih Project",
#         ["Dunnhumby Customer Insight", "Churn Analysis"]
#     )

#     if project_choice == "Dunnhumby Customer Insight":
#         dunnhumby_dashboard.show()
#     elif project_choice == "Churn Analysis":
#         churn_analysis_dashboard.show()

# elif menu == "Predictions":
#     st.header("Predictions")
#     st.write("Contoh prediksi ML")

# elif menu == "Kontak":
#     st.header("Kontak")
#     st.write("📧 Email: desyhamkar@gmail.com")


# # Page config
# st.set_page_config(
#     page_title="Portfolio 🚀",
#     page_icon="💼",
#     layout="wide",
# )

# # -----------------------------
# # Sidebar menu (drop-down)
# # -----------------------------
# st.sidebar.markdown("## 🗂 Menu")
# menu = st.sidebar.selectbox(
#     "Pilih Halaman",
#     ["Home", "About Me", "Projects", "Predictions", "Kontak"]
# )

# # -----------------------------
# # Render halaman sesuai menu
# # -----------------------------
# if menu == "Home":
#     st.title("Hello! 👋")
#     st.subheader("Saya seorang Data Scientist")
#     st.write("""
#     Selamat datang di portofolio saya.  
#     Di sini kamu bisa melihat projek, analisis data, dan contoh prediksi yang saya kerjakan menggunakan Python, Streamlit, dan Machine Learning.
#     """)
# elif menu == "About Me":
#     about_me.tentang_saya()
# elif menu == "Projects":
#     projects.show()
# elif menu == "Predictions":
#     st.header("Predictions")
#     st.write("Contoh prediksi ML")
# elif menu == "Kontak":
#     st.header("Kontak")
#     st.write("📧 Email: desyhamkar@gmail.com")


# # # Set layout halaman
# # st.set_page_config(
# #     page_title="My Portfolio 🚀",
# #     page_icon="💼",
# #     layout='wide'
# # )

# # # --- Judul Utama ---
# # st.title("Hello! 👋")
# # st.subheader("Saya seorang Data Scientist")
# # st.write("""
# # Selamat datang di portofolio saya.  
# # Di sini kamu bisa melihat projek, analisis data, dan contoh prediksi yang saya kerjakan menggunakan Python, Streamlit, dan Machine Learning.
# # """)

# # # --- Sidebar Navigasi ---
# # st.sidebar.title('Navigasi')
# # page = st.sidebar.radio('Pilih halaman', ['About Me','Projects','Predictions','Kontak'])


# # # --- Konten berdasarkan halaman ---
# # if page == 'About Me':
# #     about_me.tentang_saya()
# # elif page == 'Projects':
# #     st.header("Projects")
# #     st.write("Di sini akan ditampilkan project saya dengan deskripsi, dataset, dan visualisasi.")
# #     projects.show()
# # elif page == 'Predictions':
# #     st.header("Predictions")
# #     st.write("Di sini akan ditampilkan contoh prediksi dari model ML yang saya buat.")
# # elif page == 'Kontak':
# #     st.header("Kontak")
# #     st.write("📧 Email: desyhamkar@gmail.com") 
# #     st.write("💼 LinkedIn: [My Profile](https://www.linkedin.com/in/bq-desy-hardianti/30002043)")


# import streamlit as st
# from pages import about_me, projects  # pastikan folder pages berisi about_me.py & projects.py

# # Set page
# st.set_page_config(
#     page_title="Portfolio 🚀",
#     page_icon="💼",
#     layout="wide",
# )

# # -----------------------------
# # Sidebar Menu (mirip tab)
# # -----------------------------
# st.sidebar.markdown("## 🗂 Menu")
# menu = st.sidebar.selectbox(
#     "",
#     ["About Me", "Projects", "Predictions", "Kontak"]
# )

# # -----------------------------
# # Render halaman sesuai menu
# # -----------------------------
# if menu == "About Me":
#     about_me.tentang_saya()
# elif menu == "Projects":
#     projects.show()
# elif menu == "Predictions":
#     st.header("Predictions")
#     st.write("Contoh prediksi ML")
# elif menu == "Kontak":
#     st.header("Kontak")
#     st.write("📧 Email: desyhamkar@gmail.com")
