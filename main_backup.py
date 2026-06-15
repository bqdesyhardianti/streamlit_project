import streamlit as st
from modules import about_me, projects_gallery, contact
from projects.dunnhumby_customer_insight import view as dunnhumby_view
from projects.churn_analysis import view as churn_view
from projects.mental_health_bot import view as mental_health_view

# -----------------------------
# 1. LOAD CSS
# -----------------------------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------
# 2. CONFIG HALAMAN
# -----------------------------
st.set_page_config(
    page_title="Desy Portfolio 🚀",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 3. KONSTANTA WARNA UNGU ELEGAN
# -----------------------------
UNGU_PRIMARY = "#7C3AED"  # Ungu royal elegan
UNGU_SECONDARY = "#6D28D9" # Ungu sedikit lebih gelap untuk hover
UNGU_GRADIENT = "linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%)"

# -----------------------------
# 4. INITIALIZE SESSION STATE
# -----------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# -----------------------------
# 5. FUNGSI UNTUK NAVIGASI
# -----------------------------
def navigate_to(page):
    st.session_state.page = page
    st.query_params["page"] = page
    st.rerun()

# -----------------------------
# 6. BACA QUERY PARAMS
# -----------------------------
params = st.query_params
if "page" in params and params["page"] != st.session_state.page:
    st.session_state.page = params["page"]
    st.rerun()

# -----------------------------
# 7. SIDEBAR DENGAN AVATAR UNGU
# -----------------------------
with st.sidebar:
    # AVATAR DENGAN UI-AVATARS API - WARNA UNGU
    # Hapus background=FF69B4, ganti dengan background=7C3AED
    avatar_url = f"https://ui-avatars.com/api/?name=BQ+Desy+Hardianti&size=150&background=7C3AED&color=fff&bold=true&length=2&font-size=0.40"
    
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px; padding: 10px;">
            <img src="{avatar_url}" 
                 style="width: 100px; height: 100px; border-radius: 50%; 
                        border: 3px solid white; box-shadow: 0 4px 10px rgba(124, 58, 237, 0.3);
                        margin: 0 auto;">
            <h3 style="color: white; margin-top: 15px; margin-bottom: 5px;">BQ Desy Hardianti</h3>
            <p style="color: #7C3AED; font-size: 0.9rem;">Data Scientist & Analyst</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Menu navigasi dengan tombol Streamlit
    if st.button("🏠 Home", 
                 use_container_width=True,
                 type="primary" if st.session_state.page == "home" else "secondary"):
        navigate_to("home")
    
    if st.button("👤 About Me", 
                 use_container_width=True,
                 type="primary" if st.session_state.page == "about" else "secondary"):
        navigate_to("about")
    
    if st.button("📂 Projects", 
                 use_container_width=True,
                 type="primary" if st.session_state.page == "projects" else "secondary"):
        navigate_to("projects")
    
    if st.button("✉️ Contact", 
                 use_container_width=True,
                 type="primary" if st.session_state.page == "contact" else "secondary"):
        navigate_to("contact")
    
    st.divider()
    
    # Social media links
    st.markdown("### 🔗 Connect With Me")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("[![GitHub](https://img.icons8.com/glyph-neue/64/ffffff/github.png)](https://github.com/bqdesyhardianti)")
    with col2:
        st.markdown("[![LinkedIn](https://img.icons8.com/ios-filled/50/ffffff/linkedin.png)](https://www.linkedin.com/in/bq-desy-hardianti/)")
    with col3:
        st.markdown("[![Email](https://img.icons8.com/ios-filled/50/ffffff/email.png)](mailto:desyhamkar@gmail.com)")
    
    st.divider()
    st.markdown("""
    <p style="text-align: center; color: #666; font-size: 0.8rem; padding: 10px;">
        © 2026 Bq Desy Portfolio<br>Powered by Streamlit
    </p>
    """, unsafe_allow_html=True)

# -----------------------------
# 8. PAGE LOGIC
# -----------------------------
# Home Page
if st.session_state.page == "home":
    st.markdown('<a name="home"></a>', unsafe_allow_html=True)
    st.write("##")  # spacer atas
    
    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown('<p style="font-size: 1.5rem; color:#CCC; margin-bottom:0;">Hi, I\'m Desy</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="main-title">I\'m <span class="highlight">Data Scientist</span> & Data Analyst</h1>', unsafe_allow_html=True)
        st.markdown('''
        <p style="font-size: 1.2rem; color: #BBB; line-height: 1.6; margin-top:1rem;">
        I specialize in <strong>data analysis, machine learning, and predictive modeling</strong>, transforming complex datasets into actionable insights that drive business decisions.<br><br>
        My experience includes <strong>employee analytics, pricing optimization, product recommendation systems</strong>, and predictive modeling.<br><br>
        I am currently exploring <strong>cloud-based data solutions</strong> and scalable machine learning models.
        </p>
        ''', unsafe_allow_html=True)
        
        # Statistik singkat
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Projects", "5+", "+2")
        with col_stat2:
            st.metric("Experience", "2+ Years", "")
        with col_stat3:
            st.metric("Tools", "10+", "")
        
        st.write("##")
        if st.button("Check My Projects", use_container_width=True):
            navigate_to("projects")

    with col2:
        # AVATAR DI HOME PAGE - UKURAN BESAR DENGAN WARNA UNGU
        avatar_home_url = f"https://ui-avatars.com/api/?name=BQ+Desy+Hardianti&size=400&background=7C3AED&color=fff&bold=true&length=2&font-size=0.30"
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                <img src="{avatar_home_url}" 
                     style="width: 300px; height: 300px; border-radius: 50%; 
                            border: 5px solid #7C3AED; box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
                            object-fit: cover;">
            </div>
            """,
            unsafe_allow_html=True
        )

# Projects Page
elif st.session_state.page == "projects":
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Panggil gallery dengan callback
    projects_gallery.render_gallery(
        navigate_callback=navigate_to,
        project_callbacks={
            "Dunnhumby Customer Insight": lambda: navigate_to("project_dunnhumby"),
            "Churn Analysis": lambda: navigate_to("project_churn"),
            "Product Recommender System": lambda: navigate_to("project_prod_rec"),
            "TemanAI": lambda: navigate_to("project_mental_health")
        }
    )

# About Page
elif st.session_state.page == "about":
    st.markdown('<h1>👤 About Me</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Back", help="Kembali ke Home"):
            navigate_to("home")
    
    st.markdown("<br>", unsafe_allow_html=True)
    about_me.tentang_saya()

# Contact Page
elif st.session_state.page == "contact":
    st.markdown('<h1>✉️ Contact Me</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Back", help="Kembali ke Home"):
            navigate_to("home")
    
    st.markdown("<br>", unsafe_allow_html=True)
    contact.Kontak(
        nama="BQ Desy Hardianti",
        email="desyhamkar@gmail.com",
        github="https://github.com/bq-desyhardianti",
        linkedin="https://www.linkedin.com/in/bq-desy-hardianti/"
    ).show()

# Project Detail Pages
elif st.session_state.page == "project_dunnhumby":
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">🛒 Dunnhumby Customer Insight</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Back", help="Kembali ke Projects"):
            navigate_to("projects")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        dunnhumby_view.run()
    except Exception as e:
        st.error(f"Error loading project: {e}")
        st.info("file projects/dunnhumby_customer_insight/view.py")

elif st.session_state.page == "project_churn":
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;"> 🔮 Customer Churn Analysis </h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Back", help="Kembali ke Projects"):
            navigate_to("projects")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        from projects.churn_analysis.view import run as churn_run
        churn_run()
    except ImportError as e:
        st.error(f"❌ Error: Module tidak ditemukan")
        st.info("Pastikan file ada di: `projects/churn_analysis/view.py`")
        st.code("""
        Struktur folder yang benar:
        projects/
        └── churn_analysis/
            ├── view.py
            └── model/
                └── churn_model_final.pkl
        """)
    except FileNotFoundError as e:
        st.error(f"❌ Error: File model tidak ditemukan")
        st.info("Pastikan model ada di: `projects/churn_analysis/model/churn_model_final.pkl`")
    except Exception as e:
        st.error(f"❌ Error loading project: {e}")
        st.exception(e)

elif st.session_state.page == "project_prod_rec":
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;"> 🛍️ Product Recommendation System </h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Back", help="Kembali ke Projects"):
            navigate_to("projects")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        from projects.product_recommendation_system.view import run as prod_rec_run
        prod_rec_run()
    except ImportError as e:
        st.error(f"❌ Error: Module tidak ditemukan")
        st.info("Pastikan file ada di: `projects/product_recommendation_system/view.py`")
        st.code("""
        Struktur folder yang benar:
        projects/
        └── product_recommendation_system/
            ├── view.py
            └── model/
                └── retail_hybrid_recommender_final.pkl
        """)
    except FileNotFoundError as e:
        st.error(f"❌ Error: File model tidak ditemukan")
        st.info("Pastikan model ada di: `projects/product_recommendation_system/model/retail_hybrid_recommender_final.pkl`")
    except Exception as e:
        st.error(f"❌ Error loading project: {e}")
        st.exception(e)


elif st.session_state.page == "project_mental_health":

    st.markdown("""
    <div style="display:flex;
                align-items:center;
                gap:10px;
                margin-bottom:20px;">
        <h1 style="margin:0;">
        🌱 TemanAI
        </h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,8,1])

    with col1:
        if st.button("← Back"):
            navigate_to("projects")

    st.markdown("<br>", unsafe_allow_html=True)

    mental_health_view.run()
# -----------------------------
# 9. FOOTER
# -----------------------------
if st.session_state.page == "home":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p style='text-align: center; color: #555;'>© 2026 BQ Desy Portfolio. Powered by Streamlit</p>", unsafe_allow_html=True)