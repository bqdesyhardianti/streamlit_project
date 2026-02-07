# modules/contact.py
import streamlit as st

class Kontak:
    def __init__(self, nama, email, github=None, linkedin=None):
        self.nama = nama
        self.email = email
        self.github = github
        self.linkedin = linkedin

    def show(self):
        st.header("Kontak")
        st.write(f"**Nama:** {self.nama}")
        st.write(f"**Email:** {self.email}")
        if self.github:
            st.write(f"**GitHub:** {self.github}")
        if self.linkedin:
            st.write(f"**LinkedIn:** {self.linkedin}")

# Contoh penggunaan jika jalankan contact.py langsung
if __name__ == "__main__":
    saya = Kontak(
        nama="BQ Desy Hardianti",
        email="desyhamkar@gmail.com",
        github="https://github.com/bqdesyhardianti",
        linkedin="https://www.linkedin.com/in/bq-desy-hardianti/"
    )
    saya.show()
