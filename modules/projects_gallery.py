import streamlit as st

# --- DATA PROJECTS ---
projects = [
    {
        "id": "dunnhumby_cust_insight",
        "title": "Customer Insight",
        "category": "Predictive Analytics",
        "desc": "Comprehensive analysis of customer journeys and shopping behavior prediction using the Dunnhumby dataset.",
        "status": "Active",
        "icon": "🛒",
        "page": "project_dunnhumby"
    },
    {
        "id": "dunnhumby_customer_churn",
        "title": "Churn Analysis",
        "category": "Classification",
        "desc": "Predicting customers at risk of churn with high accuracy to support retention strategies .",
        "status": "Active",
        "icon": "🏦",
        "page": "project_churn"
    }
]

# --- RENDER GALLERY FUNCTION ---
def render_gallery(navigate_callback=None, project_callbacks=None):
    st.markdown("""
    <h1 style="font-size: 2.5rem; margin-bottom: 0;">💼 Project Showcase</h1>
    <p style="color: #BBB; font-size: 1.1rem; margin-bottom: 30px;">
    Explore a selection of my data science and analytics projects. Each project highlights
    the problem, methodology, and insights generated from the analysis.
    Click the "View Case Study" button to see more details about each project.
    </p>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Filter hanya project active
    active_projects = [p for p in projects if p['status'] == "Active"]
    
    # Tampilkan dalam grid 2 kolom agar lebih lega
    for i in range(0, len(active_projects), 2):
        cols = st.columns(2, gap="large")
        
        for j in range(2):
            if i + j < len(active_projects):
                project = active_projects[i + j]
                
                with cols[j]:
                    # Card dengan styling lebih baik
                    st.markdown(f"""
                    <div class="project-card" style="padding: 25px;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <div style="font-size: 3rem;">{project['icon']}</div>
                            <div>
                                <div class="card-category" style="margin-bottom: 5px;">{project['category']}</div>
                                <div class="card-title" style="font-size: 1.5rem;">{project['title']}</div>
                            </div>
                        </div>
                        <div class="card-desc" style="font-size: 1rem; margin-bottom: 25px;">
                            {project['desc']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Tombol dengan callback
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if navigate_callback and project_callbacks:
                            if st.button(f"🔍 View Case Study", 
                                       key=f"btn_{project['id']}", 
                                       use_container_width=True):
                                # Panggil callback yang sesuai
                                if project['title'] in project_callbacks:
                                    project_callbacks[project['title']]()
                    
                    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Project coming soon (jika ada)
    coming_soon = [p for p in projects if p['status'] != "Active"]
    if coming_soon:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🚧 Project Coming Soon")
        st.write("---")
        
        cols = st.columns(3)
        for i, project in enumerate(coming_soon):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="project-card" style="opacity: 0.7;">
                    <div style="font-size:2.5rem;">{project['icon']}</div>
                    <div class="card-category">{project['category']}</div>
                    <div class="card-title">{project['title']}</div>
                    <div class="card-desc">{project['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"🚧 {project['status']}", 
                         key=f"btn_{project['id']}_disabled", 
                         disabled=True, 
                         use_container_width=True)

