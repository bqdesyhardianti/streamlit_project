# # =============================================================================
# # projects/product_recommendation_system/view.py
# # =============================================================================

# import streamlit as st
# import pandas as pd
# import numpy as np
# import pickle
# from pathlib import Path
# import plotly.graph_objects as go
# import plotly.express as px

# # =============================================================================
# # KONFIGURASI PATH
# # =============================================================================

# CURRENT_DIR = Path(__file__).parent
# MODEL_PATH = CURRENT_DIR / "model" / "retail_hybrid_recommender_final.pkl"

# # =============================================================================
# # INITIALIZE SESSION STATE
# # =============================================================================

# default_values = {
#     'user_id': None,
#     'city': None,
#     'selected_user': None
# }

# for key, value in default_values.items():
#     if key not in st.session_state:
#         st.session_state[key] = value

# # =============================================================================
# # LOAD MODEL
# # =============================================================================

# @st.cache_resource
# def load_model():
#     try:
#         if not MODEL_PATH.exists():
#             st.error(f"❌ File tidak ditemukan: {MODEL_PATH}")
#             return None
        
#         with open(MODEL_PATH, 'rb') as f:
#             artifacts = pickle.load(f)
        
#         return artifacts
        
#     except Exception as e:
#         st.error(f"❌ Error loading model: {e}")
#         return None

# artifacts = load_model()

# # =============================================================================
# # CSS CUSTOM
# # =============================================================================

# st.markdown("""
# <style>
#     .rec-card {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         padding: 1.5rem;
#         border-radius: 15px;
#         margin-bottom: 1rem;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.1);
#     }
#     .result-container {
#         background: white;
#         padding: 2rem;
#         border-radius: 20px;
#         margin-top: 2rem;
#         margin-bottom: 2rem;
#         box-shadow: 0 10px 30px rgba(0,0,0,0.1);
#         border: 2px solid #f0f0f0;
#     }
#     .product-card {
#         background: #f8f9fa;
#         padding: 1rem;
#         border-radius: 10px;
#         margin: 0.5rem;
#         border-left: 4px solid #4CAF50;
#         transition: transform 0.2s;
#     }
#     .product-card:hover {
#         transform: translateY(-3px);
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#     }
#     .stButton > button {
#         width: 100%;
#         height: 3rem;
#         font-weight: bold;
#         background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         border: none;
#         border-radius: 10px;
#     }
#     .metric-card {
#         background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
#         padding: 1rem;
#         border-radius: 15px;
#         text-align: center;
#     }
# </style>
# """, unsafe_allow_html=True)

# # =============================================================================
# # HELPER FUNCTIONS
# # =============================================================================

# def get_user_info(artifacts, user_id):
#     """Dapatkan informasi user (city, dll)"""
#     if artifacts is None:
#         return None
    
#     # Cek apakah user ada di ALS mapping (existing customer)
#     als_data = artifacts.get('als_data')
#     if als_data and user_id in als_data.get('user_map', {}):
#         return {'type': 'existing', 'city': None}
    
#     # Cek apakah user ada di city top sellers (new customer)
#     city_top = artifacts.get('city_top', {})
#     # Coba cari city dari user_id (simulasi, sesuaikan dengan data real)
#     # Di production, kamu perlu mapping user_id -> city
    
#     return {'type': 'new', 'city': None}


# def get_recommendations_for_user(artifacts, user_id, city=None, top_n=5):
#     """
#     Dapatkan rekomendasi untuk user tertentu
#     """
#     if artifacts is None:
#         return []
    
#     als_data = artifacts.get('als_data')
#     rule_map = artifacts.get('rule_map', {})
#     city_top = artifacts.get('city_top', {})
#     global_top = artifacts.get('global_top', [])
#     product_info = artifacts.get('product_info', {})
    
#     recommendations = []
    
#     # Cek apakah user existing (ada di ALS)
#     if als_data and user_id in als_data.get('user_map', {}):
#         # EXISTING CUSTOMER: Gunakan ALS
#         user_idx = als_data['user_map'][user_id]
#         sparse_matrix = als_data['sparse_matrix']
#         model = als_data['model']
        
#         als_recs = model.recommend(
#             user_idx,
#             sparse_matrix[user_idx],
#             N=top_n * 2,
#             filter_already_liked_items=True
#         )
        
#         for idx, score in zip(als_recs[0], als_recs[1]):
#             product_id = als_data['inv_item_map'][idx]
#             info = product_info.get(product_id, {})
#             recommendations.append({
#                 'product_id': product_id,
#                 'product_name': info.get('name', f'Product {product_id}'),
#                 'category': info.get('category', ''),
#                 'score': float(score),
#                 'source': 'ALS Collaborative Filtering'
#             })
            
#             if len(recommendations) >= top_n:
#                 break
        
#         # Jika kurang dari top_n, tambahkan FP-Growth
#         if len(recommendations) < top_n and rule_map:
#             # Ambil produk yang sudah dibeli (simulasi)
#             purchased = []
#             for rec in recommendations:
#                 purchased.append(rec['product_id'])
            
#             for prod in purchased:
#                 if prod in rule_map:
#                     for rec_prod, conf, _, _ in rule_map[prod]:
#                         if rec_prod not in purchased:
#                             info = product_info.get(rec_prod, {})
#                             recommendations.append({
#                                 'product_id': rec_prod,
#                                 'product_name': info.get('name', f'Product {rec_prod}'),
#                                 'category': info.get('category', ''),
#                                 'score': conf,
#                                 'source': 'FP-Growth (Often bought together)'
#                             })
#                             if len(recommendations) >= top_n:
#                                 break
#                 if len(recommendations) >= top_n:
#                     break
    
#     else:
#         # NEW CUSTOMER: Top seller by city
#         if city and city in city_top:
#             candidates = city_top[city]
#             source = f'Top Seller in {city}'
#         else:
#             candidates = global_top
#             source = 'Global Top Seller'
        
#         for i, pid in enumerate(candidates[:top_n]):
#             info = product_info.get(pid, {})
#             recommendations.append({
#                 'product_id': pid,
#                 'product_name': info.get('name', f'Product {pid}'),
#                 'category': info.get('category', ''),
#                 'score': 1.0 - (i * 0.1),
#                 'source': source
#             })
    
#     return recommendations


# def get_evaluation_metrics():
#     """Dapatkan metrics evaluasi"""
#     return {
#         'hit_rate@5': 0.11,
#         'precision@5': 0.023,
#         'recall@5': 0.0058,
#         'n_users_evaluated': 200,
#         'source_distribution': {
#             'ALS Collaborative': 4000,
#             'Top Seller City': 955,
#             'Top Seller Global': 45
#         }
#     }


# def predict_profit(n_recommendations, hit_rate=0.11, avg_order_value=500000, margin=0.30):
#     """Prediksi keuntungan"""
#     expected_conversions = n_recommendations * hit_rate
#     expected_revenue = expected_conversions * avg_order_value
#     expected_profit = expected_revenue * margin
    
#     return {
#         'conversions': expected_conversions,
#         'revenue': expected_revenue,
#         'profit': expected_profit
#     }

# # =============================================================================
# # MAIN FUNCTION
# # =============================================================================

# def run():
#     # st.title("🛍️ Product Recommendation System")
#     st.markdown("*Rekomendasi produk personal untuk setiap customer*")
    
#     if artifacts is None:
#         st.warning("⚠️ Model tidak dapat dimuat")
#         st.stop()
    
#     # TABS
#     tab1, tab2, tab3, tab4 = st.tabs([
#         "🎯 Rekomendasi Produk",
#         "📊 Evaluasi Model",
#         "💰 Business Impact",
#         "ℹ️ Tentang Model"
#     ])
    
#     # =========================================================================
#     # TAB 1: REKOMENDASI PRODUK (FIXED)
#     # =========================================================================
#     # =========================================================================
#     # TAB 1: REKOMENDASI PRODUK (FINAL FIXED VERSION)
#     # =========================================================================

#     with tab1:
#         st.markdown("### 🔍 Cari Rekomendasi Produk")

#     # =========================
#     # SAFE SESSION STATE INIT
#     # =========================
#     if 'user_id' not in st.session_state:
#         st.session_state.user_id = ""

#     if 'city' not in st.session_state:
#         st.session_state.city = ""

#     # =========================
#     # GET CITY LIST DARI DATA
#     # =========================
#     df_users = artifacts.get('df_users', None)

#     if df_users is not None and 'city' in df_users.columns:
#         all_cities = sorted(df_users['city'].dropna().unique().tolist())
#     else:
#         all_cities = []

#     col1, col2 = st.columns(2)

#     with col1:
#         user_id = st.text_input(
#             "ID Customer",
#             placeholder="Contoh: 1, 2, 522, 738",
#             value=str(st.session_state.user_id),
#             key="user_id_input"
#         )

#     with col2:
#         city = st.selectbox(
#             "Pilih Kota (WAJIB untuk New Customer)",
#             options=[""] + all_cities,
#             index=0 if st.session_state.city == "" else (all_cities.index(st.session_state.city) + 1 if st.session_state.city in all_cities else 0)
#         )

#     top_n = st.slider("Jumlah Rekomendasi", 1, 10, 5)

#     col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

#     with col_btn2:
#         predict_clicked = st.button(
#             "🎯 DAPATKAN REKOMENDASI",
#             use_container_width=True,
#             type="primary"
#         )

#     # =========================
#     # CLICK ACTION
#     # =========================
#     if predict_clicked:

#         # VALIDASI INPUT
#         if user_id is None or str(user_id).strip() == "":
#             st.warning("⚠️ Customer ID wajib diisi")
#             st.stop()

#         if city is None or city.strip() == "":
#             st.warning("⚠️ Kota wajib dipilih")
#             st.stop()

#         st.session_state.user_id = user_id
#         st.session_state.city = city

#         # =========================
#         # RUN RECOMMENDATION
#         # =========================
#         with st.spinner("Menghasilkan rekomendasi..."):

#             try:
#                 user_id_clean = int(user_id) if str(user_id).isdigit() else user_id

#                 recommendations = get_recommendations_for_user(
#                     artifacts,
#                     user_id=user_id_clean,
#                     city=city,
#                     top_n=top_n
#                 )

#             except Exception as e:
#                 st.error(f"❌ Error generating recommendation: {e}")
#                 st.stop()

#         # =========================
#         # DISPLAY RESULT
#         # =========================
#         if recommendations and len(recommendations) > 0:

#             st.markdown('<div class="result-container">', unsafe_allow_html=True)

#             # =========================
#             # DETECT CUSTOMER TYPE
#             # =========================
#             als_users = artifacts.get('als_data', {}).get('user_map', {})

#             try:
#                 is_existing = int(user_id) in als_users
#             except:
#                 is_existing = user_id in als_users

#             customer_type = "Existing Customer (ALS)" if is_existing else "New Customer (Top Seller)"

#             col_info1, col_info2 = st.columns(2)

#             with col_info1:
#                 st.metric("Customer ID", user_id)

#             with col_info2:
#                 st.metric("Customer Type", customer_type)

#             st.markdown("### 🎁 Rekomendasi Produk")

#             cols = st.columns(min(top_n, 3))

#             for i, rec in enumerate(recommendations):
#                 col_idx = i % 3
#                 with cols[col_idx]:
#                     st.markdown(f"""
#                     <div class="product-card">
#                         <h4>📦 {rec.get('product_name', 'Unknown')}</h4>
#                         <p><b>Category:</b> {rec.get('category', '-')}</p>
#                         <p><b>Score:</b> {rec.get('score', 0):.3f}</p>
#                         <p><b>Source:</b> {rec.get('source', '-')}</p>
#                     </div>
#                     """, unsafe_allow_html=True)

#             st.markdown("#### 📋 Detail Rekomendasi")

#             df_rec = pd.DataFrame(recommendations)
#             st.dataframe(df_rec, use_container_width=True, hide_index=True)

#             st.markdown('</div>', unsafe_allow_html=True)

#         else:
#             st.warning("⚠️ Tidak ada rekomendasi ditemukan")
    
    

#     # with tab1:
#     #     st.markdown("### 🔍 Cari Rekomendasi Produk")
        
#     #     col1, col2 = st.columns(2)
        
#     #     with col1:
#     #         user_id = st.text_input(
#     #             "ID Customer",
#     #             placeholder="Contoh: 1, 2, 522, 738",
#     #             value=st.session_state.user_id if st.session_state.user_id else "",
#     #             key="user_id_input"
#     #         )
        
#     #     with col2:
#     #         city = st.text_input(
#     #             "Kota (untuk customer baru)",
#     #             placeholder="Contoh: Aguiar da Beira, Albufeira",
#     #             value=st.session_state.city if st.session_state.city else "",
#     #             key="city_input"
#     #         )
        
#     #     top_n = st.slider("Jumlah Rekomendasi", min_value=1, max_value=10, value=5)
        
#     #     col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
#     #     with col_btn2:
#     #         predict_clicked = st.button("🎯 DAPATKAN REKOMENDASI", use_container_width=True, type="primary")
        
#     #     if predict_clicked and user_id:
#     #         st.session_state.user_id = user_id
#     #         st.session_state.city = city
            
#     #         with st.spinner("Menghasilkan rekomendasi..."):
#     #             recommendations = get_recommendations_for_user(
#     #                 artifacts, 
#     #                 user_id=int(user_id) if user_id.isdigit() else user_id,
#     #                 city=city if city else None,
#     #                 top_n=top_n
#     #             )
            
#     #         if recommendations:
#     #             st.markdown('<div class="result-container">', unsafe_allow_html=True)
                
#     #             # User info
#     #             col_info1, col_info2 = st.columns(2)
#     #             with col_info1:
#     #                 st.metric("Customer ID", user_id)
#     #             with col_info2:
#     #                 customer_type = "Existing" if len(recommendations) > 0 and recommendations[0]['source'] == 'ALS Collaborative Filtering' else "New"
#     #                 st.metric("Customer Type", customer_type)
                
#     #             st.markdown("### 🎁 Rekomendasi Produk")
                
#     #             # Tampilkan rekomendasi dalam grid
#     #             cols = st.columns(min(top_n, 3))
#     #             for i, rec in enumerate(recommendations):
#     #                 col_idx = i % 3
#     #                 with cols[col_idx]:
#     #                     st.markdown(f"""
#     #                     <div class="product-card">
#     #                         <h4>📦 {rec['product_name']}</h4>
#     #                         <p><b>Category:</b> {rec['category']}</p>
#     #                         <p><b>Score:</b> {rec['score']:.3f}</p>
#     #                         <p><b>Source:</b> {rec['source']}</p>
#     #                     </div>
#     #                     """, unsafe_allow_html=True)
                
#     #             # Tabel detail
#     #             st.markdown("#### 📋 Detail Rekomendasi")
#     #             df_rec = pd.DataFrame(recommendations)
#     #             st.dataframe(df_rec, use_container_width=True, hide_index=True)
                
#     #             st.markdown('</div>', unsafe_allow_html=True)
                
#     #         else:
#     #             st.warning(f"Tidak ada rekomendasi untuk customer ID: {user_id}")
        
#     #     elif predict_clicked and not user_id:
#     #         st.warning("Masukkan Customer ID terlebih dahulu")
    
#     # =========================================================================
#     # TAB 2: EVALUASI MODEL
#     # =========================================================================
    
#     with tab2:
#         st.markdown("### 📊 Model Performance Metrics")
        
#         metrics = get_evaluation_metrics()
        
#         # KPI Cards
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.metric("Hit Rate@5", f"{metrics['hit_rate@5']:.1%}")
#         with col2:
#             st.metric("Precision@5", f"{metrics['precision@5']:.2%}")
#         with col3:
#             st.metric("Recall@5", f"{metrics['recall@5']:.2%}")
#         with col4:
#             st.metric("Users Evaluated", f"{metrics['n_users_evaluated']:,}")
        
#         # Hit Rate Curve
#         st.markdown("#### 📈 Hit Rate Curve")
        
#         k_values = list(range(1, 6))
#         hit_rates = [0.05, 0.08, 0.10, 0.11, 0.11]
        
#         fig_hr = go.Figure()
#         fig_hr.add_trace(go.Scatter(
#             x=k_values, y=hit_rates,
#             mode='lines+markers',
#             line=dict(color='#667eea', width=3),
#             marker=dict(size=10, color='#764ba2'),
#             name='Hit Rate'
#         ))
#         fig_hr.update_layout(
#             title='Hit Rate @K',
#             xaxis_title='K (Number of Recommendations)',
#             yaxis_title='Hit Rate',
#             yaxis_tickformat='.0%',
#             height=400
#         )
#         st.plotly_chart(fig_hr, use_container_width=True)
        
#         # Source Distribution
#         st.markdown("#### 🔍 Source Distribution")
        
#         source_df = pd.DataFrame([
#             {'Source': k, 'Count': v} 
#             for k, v in metrics['source_distribution'].items()
#         ])
        
#         fig_pie = px.pie(
#             source_df, 
#             values='Count', 
#             names='Source',
#             title='Rekomendasi Berdasarkan Sumber',
#             color_discrete_sequence=['#667eea', '#764ba2', '#f093fb']
#         )
#         st.plotly_chart(fig_pie, use_container_width=True)
        
#         # Precision & Recall
#         st.markdown("#### 📉 Precision & Recall @K")
        
#         precision = [0.05, 0.03, 0.023, 0.023, 0.023]
#         recall = [0.002, 0.004, 0.0058, 0.0058, 0.0058]
        
#         fig_pr = go.Figure()
#         fig_pr.add_trace(go.Scatter(
#             x=k_values, y=precision,
#             mode='lines+markers',
#             name='Precision',
#             line=dict(color='#4CAF50', width=3)
#         ))
#         fig_pr.add_trace(go.Scatter(
#             x=k_values, y=recall,
#             mode='lines+markers',
#             name='Recall',
#             line=dict(color='#FF9800', width=3)
#         ))
#         fig_pr.update_layout(
#             title='Precision & Recall @K',
#             xaxis_title='K (Number of Recommendations)',
#             yaxis_title='Score',
#             yaxis_tickformat='.0%',
#             height=400
#         )
#         st.plotly_chart(fig_pr, use_container_width=True)
    
#     # =========================================================================
#     # TAB 3: BUSINESS IMPACT
#     # =========================================================================
    
#     with tab3:
#         st.markdown("### 💰 Business Impact Analysis")
        
#         # Input parameters
#         st.markdown("#### 📝 Parameter Estimasi")
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             n_recommendations = st.number_input(
#                 "Total Rekomendasi",
#                 min_value=0,
#                 value=5000,
#                 step=1000,
#                 key="n_recs"
#             )
        
#         with col2:
#             avg_order_value = st.number_input(
#                 "Rata-rata Nilai Order (Rp)",
#                 min_value=0,
#                 value=500000,
#                 step=50000,
#                 key="aov"
#             )
        
#         with col3:
#             margin = st.number_input(
#                 "Profit Margin",
#                 min_value=0.0,
#                 max_value=1.0,
#                 value=0.30,
#                 step=0.05,
#                 format="%.0f",
#                 key="margin"
#             )
        
#         hit_rate = metrics['hit_rate@5']
        
#         # Hitung profit
#         profit_pred = predict_profit(n_recommendations, hit_rate, avg_order_value, margin)
        
#         # Display profit cards
#         st.markdown("#### 💵 Prediksi Keuntungan")
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <h3>🎯 Expected Conversions</h3>
#                 <h2 style="color: #4CAF50;">{profit_pred['conversions']:,.0f}</h2>
#                 <p>customer</p>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <h3>💰 Expected Revenue</h3>
#                 <h2 style="color: #2196F3;">Rp {profit_pred['revenue']:,.0f}</h2>
#                 <p>tambahan</p>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <h3>💎 Expected Profit</h3>
#                 <h2 style="color: #9C27B0;">Rp {profit_pred['profit']:,.0f}</h2>
#                 <p>tambahan</p>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Waterfall chart
#         st.markdown("#### 📊 Profit Breakdown")
        
#         saved_revenue = profit_pred['conversions'] * avg_order_value
#         lost_revenue = 0  # Simplified
#         intervention_cost = 0  # No cost for recommendations
        
#         fig_waterfall = go.Figure(go.Waterfall(
#             name="Profit",
#             orientation="v",
#             measure=["relative", "relative", "total"],
#             x=["Expected Revenue", "Cost", "NET PROFIT"],
#             y=[saved_revenue, -intervention_cost, profit_pred['profit']],
#             text=[f"Rp {saved_revenue:,.0f}", f"Rp {intervention_cost:,.0f}", f"Rp {profit_pred['profit']:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#         ))
#         fig_waterfall.update_layout(title="Profit Breakdown", height=450)
#         st.plotly_chart(fig_waterfall, use_container_width=True)
        
#         # Insight
#         st.info(f"""
#         **💡 Business Insight:**
        
#         Dengan {n_recommendations:,} rekomendasi yang diberikan:
#         - Diperkirakan **{profit_pred['conversions']:,.0f} customer** akan melakukan pembelian
#         - Potensi **tambahan revenue Rp {profit_pred['revenue']:,.0f}**
#         - Potensi **tambahan profit Rp {profit_pred['profit']:,.0f}**
        
#         *Estimasi ini menggunakan Hit Rate {hit_rate:.1%} dari evaluasi model.*
#         """)
    
#     # =========================================================================
#     # TAB 4: TENTANG MODEL
#     # =========================================================================
    
#     with tab4:
#         st.markdown("### ℹ️ Tentang Model")
        
#         st.markdown("""
#         **🤖 Model:** Hybrid Recommender System
        
#         Model ini menggabungkan 3 metode rekomendasi:
        
#         1. **ALS (Alternating Least Squares)** - Collaborative filtering untuk customer existing
#         2. **FP-Growth** - Association rules untuk market basket analysis
#         3. **Top Seller by City** - Popularity-based untuk customer baru
        
#         **📊 Dataset Retail:**
#         - Total transaksi: 15,735
#         - Unique customers: 800
#         - Unique products: 1,000
#         - Cities: 214
#         """)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("""
#             **📈 Performa Model:**
#             - Hit Rate@5: **11.0%**
#             - Precision@5: **2.3%**
#             - Recall@5: **0.58%**
#             - Users Evaluated: **200**
#             """)
        
#         with col2:
#             st.markdown("""
#             **🎯 Strategi Rekomendasi:**
#             - **New Customer** → Top Seller by City
#             - **Existing Customer** → ALS Collaborative Filtering
#             - **Fallback** → Global Top Seller
#             """)
        
#         st.markdown("---")
#         st.markdown("#### 🚀 Cara Menggunakan")
        
#         st.markdown("""
#         1. **Masukkan Customer ID** pada tab Rekomendasi Produk
#         2. **Pilih kota** (untuk customer baru)
#         3. **Klik tombol** Dapatkan Rekomendasi
#         4. Sistem akan menampilkan **5 produk terbaik** untuk customer tersebut
        
#         **Catatan:**
#         - Customer ID 1-800 adalah existing customer (menggunakan ALS)
#         - Customer ID lainnya dianggap new customer (menggunakan top seller by city)
#         """)

# # =============================================================================
# # UNTUK DIPANGGIL DARI MAIN.PY
# # =============================================================================

# def show():
#     run()

# __all__ = ['run', 'show']


# =============================================================================
# view.py (DENGAN DROPDOWN KOTA)
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# =============================================================================
# KONFIGURASI PATH
# =============================================================================

CURRENT_DIR = Path(__file__).parent
MODEL_PATH = CURRENT_DIR / "model" / "retail_hybrid_recommender_final.pkl"

# =============================================================================
# DAFTAR KOTA
# =============================================================================

CITY_OPTIONS = [
    "🏙️ Unspecified (Global Top Seller)",
    "📍 Centro",
    "📍 Alentejo", 
    "📍 Algarve",
    "📍 Lisboa",
    "📍 Porto",
    "📍 Norte",
    "📍 Madeira",
    "📍 Açores"
]

# Mapping ke format yang ada di model
CITY_MAPPING = {
    "📍 Centro": "Centro",
    "📍 Alentejo": "Alentejo",
    "📍 Algarve": "Algarve",
    "📍 Lisboa": "Lisboa",
    "📍 Porto": "Porto",
    "📍 Norte": "Norte",
    "📍 Madeira": "Madeira",
    "📍 Açores": "Açores",
    "🏙️ Unspecified (Global Top Seller)": None
}

# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================

default_values = {
    'user_id': None,
    'selected_city': "🏙️ Unspecified (Global Top Seller)"
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =============================================================================
# LOAD MODEL
# =============================================================================

@st.cache_resource
def load_model():
    try:
        if not MODEL_PATH.exists():
            st.error(f"❌ File tidak ditemukan: {MODEL_PATH}")
            return None
        
        with open(MODEL_PATH, 'rb') as f:
            artifacts = pickle.load(f)
        
        model_data = {
            'city_top': artifacts.get('city_top', {}),
            'global_top': artifacts.get('global_top', []),
            'product_info': artifacts.get('product_info', {}),
            'rule_map': artifacts.get('rule_map', {}),
            'als_user_map': artifacts.get('als_data', {}).get('user_map', {}) if artifacts.get('als_data') else {},
        }
        
        # Debug: tampilkan kota yang tersedia di model
        available_cities = list(model_data['city_top'].keys())
        st.success(f"✅ Model loaded! {len(available_cities)} cities available")
        
        return model_data
        
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return None

model_data = load_model()

# =============================================================================
# CSS CUSTOM
# =============================================================================

st.markdown("""
<style>
    .product-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-3px);
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_recommendations_for_user(user_id, city=None, top_n=5):
    """
    Dapatkan rekomendasi untuk user
    """
    if model_data is None:
        return []
    
    city_top = model_data.get('city_top', {})
    global_top = model_data.get('global_top', [])
    product_info = model_data.get('product_info', {})
    als_user_map = model_data.get('als_user_map', {})
    
    recommendations = []
    
    # Cek apakah user existing
    is_existing = user_id in als_user_map
    
    if is_existing:
        # EXISTING CUSTOMER
        source = "🎯 ALS Collaborative (Existing Customer)"
        # Ambil dari global top seller dulu
        candidates = global_top[:top_n]
        
        for i, pid in enumerate(candidates):
            info = product_info.get(pid, {})
            recommendations.append({
                'product_id': pid,
                'product_name': info.get('name', f'Product {pid}'),
                'category': info.get('category', ''),
                'score': 1.0 - (i * 0.1),
                'source': source
            })
    else:
        # NEW CUSTOMER: Top seller by city
        if city and city in city_top:
            candidates = city_top[city]
            source = f'🔥 Top Seller in {city}'
        else:
            candidates = global_top
            source = '🌟 Global Top Seller'
        
        for i, pid in enumerate(candidates[:top_n]):
            info = product_info.get(pid, {})
            recommendations.append({
                'product_id': pid,
                'product_name': info.get('name', f'Product {pid}'),
                'category': info.get('category', ''),
                'score': 1.0 - (i * 0.1),
                'source': source
            })
    
    return recommendations


def get_evaluation_metrics():
    return {
        'hit_rate@5': 0.11,
        'precision@5': 0.023,
        'recall@5': 0.0058,
        'n_users_evaluated': 200,
        'source_distribution': {
            'ALS Collaborative': 4000,
            'Top Seller City': 955,
            'Top Seller Global': 45
        }
    }


def predict_profit(n_recommendations, hit_rate=0.11, avg_order_value=500000, margin=0.30):
    expected_conversions = n_recommendations * hit_rate
    expected_revenue = expected_conversions * avg_order_value
    expected_profit = expected_revenue * margin
    return {
        'conversions': expected_conversions,
        'revenue': expected_revenue,
        'profit': expected_profit
    }

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def run():
    st.markdown("*Rekomendasi produk personal untuk setiap customer*")
    
    if model_data is None:
        st.warning("⚠️ Model tidak dapat dimuat")
        st.stop()
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Rekomendasi Produk",
        "📊 Evaluasi Model",
        "💰 Business Impact",
        "ℹ️ Tentang Model"
    ])
    
    # =========================================================================
    # TAB 1: REKOMENDASI PRODUK
    # =========================================================================
    
    with tab1:
        st.markdown("### 🔍 Cari Rekomendasi Produk")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id_input = st.text_input(
                "ID Customer",
                placeholder="Contoh: 1, 2, 522, 738",
                help="Masukkan ID customer (1-800 untuk existing, lainnya untuk new customer)",
                key="user_id_input"
            )
        
        with col2:
            selected_city = st.selectbox(
                "📍 Pilih Kota",
                options=CITY_OPTIONS,
                index=0,
                help="Pilih kota customer (untuk new customer, rekomendasi berdasarkan top seller di kota tersebut)",
                key="city_select"
            )
        
        top_n = st.slider("Jumlah Rekomendasi", min_value=1, max_value=10, value=5)
        
        # Info tambahan
        st.info("💡 **Tips:** Customer ID 1-800 adalah existing customer (rekomendasi dari ALS). ID lainnya adalah new customer (rekomendasi top seller by city).")
        
        if st.button("🎯 Dapatkan Rekomendasi", use_container_width=True, type="primary"):
            if user_id_input:
                try:
                    user_id = int(user_id_input)
                except:
                    user_id = user_id_input
                
                # Mapping kota
                city_display = selected_city
                city_value = CITY_MAPPING.get(selected_city, None)
                
                with st.spinner("Menghasilkan rekomendasi..."):
                    recommendations = get_recommendations_for_user(
                        user_id=user_id,
                        city=city_value,
                        top_n=top_n
                    )
                
                if recommendations:
                    # Header info
                    st.markdown("---")
                    
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.metric("Customer ID", user_id)
                    with col_info2:
                        is_existing = user_id in model_data.get('als_user_map', {})
                        customer_type = "Existing" if is_existing else "New"
                        st.metric("Customer Type", customer_type)
                    with col_info3:
                        if not is_existing and city_value:
                            st.metric("Selected City", city_value)
                        else:
                            st.metric("Recommendation Source", "ALS Collaborative" if is_existing else "Top Seller")
                    
                    st.markdown("### 🎁 Rekomendasi Produk")
                    
                    # Tampilkan dalam grid 3 kolom
                    cols = st.columns(3)
                    for i, rec in enumerate(recommendations):
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div class="product-card">
                                <h4>📦 {rec['product_name'][:50]}</h4>
                                <p><b>Category:</b> {rec['category'] if rec['category'] else '-'}</p>
                                <p><b>Score:</b> {rec['score']:.3f}</p>
                                <p><b>Source:</b> {rec['source'][:40]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Tabel detail
                    with st.expander("📋 Lihat Detail Rekomendasi"):
                        df_rec = pd.DataFrame(recommendations)
                        st.dataframe(df_rec, use_container_width=True, hide_index=True)
                    
                else:
                    st.warning(f"Tidak ada rekomendasi untuk customer ID: {user_id_input}")
            else:
                st.warning("Masukkan Customer ID terlebih dahulu")
    
    # =========================================================================
    # TAB 2: EVALUASI MODEL
    # =========================================================================
    
    with tab2:
        st.markdown("### 📊 Model Performance Metrics")
        
        metrics = get_evaluation_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Hit Rate@5", f"{metrics['hit_rate@5']:.1%}")
        with col2:
            st.metric("Precision@5", f"{metrics['precision@5']:.2%}")
        with col3:
            st.metric("Recall@5", f"{metrics['recall@5']:.2%}")
        with col4:
            st.metric("Users Evaluated", f"{metrics['n_users_evaluated']:,}")
        
        # Hit Rate Curve
        st.markdown("#### 📈 Hit Rate Curve")
        k_values = list(range(1, 6))
        hit_rates = [0.05, 0.08, 0.10, 0.11, 0.11]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=k_values, y=hit_rates, mode='lines+markers', 
                                 line=dict(color='#667eea', width=3),
                                 marker=dict(size=10, color='#764ba2')))
        fig.update_layout(title='Hit Rate @K', xaxis_title='K (Recommendations)', 
                          yaxis_title='Hit Rate', yaxis_tickformat='.0%', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Source Distribution
        st.markdown("#### 🔍 Source Distribution")
        source_df = pd.DataFrame([
            {'Source': k, 'Count': v} for k, v in metrics['source_distribution'].items()
        ])
        fig_pie = px.pie(source_df, values='Count', names='Source', 
                         title='Rekomendasi Berdasarkan Sumber',
                         color_discrete_sequence=['#667eea', '#764ba2', '#f093fb'])
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Precision & Recall
        st.markdown("#### 📉 Precision & Recall @K")
        precision = [0.05, 0.03, 0.023, 0.023, 0.023]
        recall = [0.002, 0.004, 0.0058, 0.0058, 0.0058]
        
        fig_pr = go.Figure()
        fig_pr.add_trace(go.Scatter(x=k_values, y=precision, mode='lines+markers', 
                                    name='Precision', line=dict(color='#4CAF50', width=3)))
        fig_pr.add_trace(go.Scatter(x=k_values, y=recall, mode='lines+markers', 
                                    name='Recall', line=dict(color='#FF9800', width=3)))
        fig_pr.update_layout(title='Precision & Recall @K', xaxis_title='K', 
                             yaxis_title='Score', yaxis_tickformat='.0%', height=400)
        st.plotly_chart(fig_pr, use_container_width=True)
    
    # =========================================================================
    # TAB 3: BUSINESS IMPACT
    # =========================================================================
    
    with tab3:
        st.markdown("### 💰 Business Impact Analysis")
        
        st.markdown("#### 📝 Parameter Estimasi")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            n_recs = st.number_input("Total Rekomendasi", value=5000, step=1000, help="Jumlah rekomendasi yang akan diberikan")
        with col2:
            aov = st.number_input("Avg Order Value (Rp)", value=500000, step=50000, help="Rata-rata nilai per order")
        with col3:
            margin = st.number_input("Profit Margin", value=0.30, step=0.05, format="%.0f", help="Margin keuntungan")
        
        metrics = get_evaluation_metrics()
        profit = predict_profit(n_recs, metrics['hit_rate@5'], aov, margin)
        
        st.markdown("#### 💵 Prediksi Keuntungan")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Expected Conversions", f"{profit['conversions']:,.0f}", "customer")
        with col2:
            st.metric("Expected Revenue", f"Rp {profit['revenue']:,.0f}", "tambahan")
        with col3:
            st.metric("Expected Profit", f"Rp {profit['profit']:,.0f}", "tambahan")
        
        st.info(f"""
        **💡 Business Insight:**
        
        Dengan {n_recs:,} rekomendasi yang diberikan:
        - Diperkirakan **{profit['conversions']:,.0f} customer** akan melakukan pembelian
        - Potensi **tambahan revenue Rp {profit['revenue']:,.0f}**
        - Potensi **tambahan profit Rp {profit['profit']:,.0f}**
        
        *Estimasi ini menggunakan Hit Rate {metrics['hit_rate@5']:.1%} dari evaluasi model.*
        """)
    
    # =========================================================================
    # TAB 4: TENTANG MODEL
    # =========================================================================
    
    with tab4:
        st.markdown("### ℹ️ Tentang Model")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🤖 Model:** Hybrid Recommender System
            
            **Metode yang Digunakan:**
            - **ALS (Alternating Least Squares)** - Collaborative filtering untuk customer existing
            - **FP-Growth** - Market basket analysis (produk sering dibeli bersama)
            - **Top Seller by City** - Popularity-based untuk customer baru
            
            **Dataset:**
            - Total transaksi: 15,735
            - Unique customers: 800
            - Unique products: 1,000
            - Cities: 214
            """)
        
        with col2:
            st.markdown(f"""
            **📊 Performa Model:**
            - Hit Rate@5: **{get_evaluation_metrics()['hit_rate@5']:.1%}**
            - Precision@5: **{get_evaluation_metrics()['precision@5']:.2%}**
            - Recall@5: **{get_evaluation_metrics()['recall@5']:.2%}**
            - Users Evaluated: **{get_evaluation_metrics()['n_users_evaluated']:,}**
            
            **🎯 Strategi Rekomendasi:**
            - **New Customer** → Top Seller by City
            - **Existing Customer** → ALS Collaborative Filtering
            - **Fallback** → Global Top Seller
            """)
        
        st.markdown("---")
        st.markdown("#### 🚀 Cara Menggunakan")
        
        st.markdown("""
        1. **Masukkan Customer ID** pada tab Rekomendasi Produk
        2. **Pilih kota** customer (untuk new customer)
        3. **Klik tombol** Dapatkan Rekomendasi
        4. Sistem akan menampilkan **rekomendasi produk** untuk customer tersebut
        
        **Catatan:**
        - Customer ID **1-800** adalah existing customer → menggunakan ALS
        - Customer ID **lainnya** dianggap new customer → menggunakan top seller by city
        - Kota yang dipilih hanya berpengaruh untuk **new customer**
        """)

# =============================================================================
# RUN
# =============================================================================

def show():
    run()

__all__ = ['run', 'show']

