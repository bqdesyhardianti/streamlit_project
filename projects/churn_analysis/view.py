# =============================================================================
# projects/churn_analysis/view.py
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import joblib
from pathlib import Path

# =============================================================================
# KONFIGURASI PATH
# =============================================================================

CURRENT_DIR = Path(__file__).parent
MODEL_PATH = CURRENT_DIR / "model" / "churn_model_final.pkl"
FEATURES_PATH = CURRENT_DIR / "model" / "feature_names.pkl"
METRICS_PATH = CURRENT_DIR / "model" / "business_metrics.pkl"

# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================

default_values = {
    'frequency': 10,
    'monetary': 500_000,
    'unique_products': 20,
    'unique_departments': 8,
    'age': 3,          # 35-44
    'income': 5,       # 50-74K
    'hh': 2,           # 2 orang
    'marital': 1,      # Married
    'homeowner': 1     # Homeowner
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =============================================================================
# LOAD MODEL DAN METRICS
# =============================================================================

@st.cache_resource
def load_model():
    try:
        if not MODEL_PATH.exists():
            st.error(f"❌ File tidak ditemukan: {MODEL_PATH}")
            return None, None, None
        
        model = joblib.load(MODEL_PATH)
        features = joblib.load(FEATURES_PATH)
        
        try:
            metrics = joblib.load(METRICS_PATH)
        except:
            metrics = {
                'profit_per_1000': 42_040_000,
                'recall': 0.648,
                'precision': 0.448,
                'roc_auc': 0.796,
                'tp_per_1000': 126,
                'fp_per_1000': 156,
                'fn_per_1000': 69,
                'threshold': 0.37,  # UBAH JADI 37%!
                'customer_value': 1_000_000,
                'intervention_cost': 100_000
            }
        
        return model, features, metrics
        
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return None, None, None

model, selected_features, metrics = load_model()

# =============================================================================
# FUNGSI FEATURE IMPORTANCE
# =============================================================================

def get_feature_importance():
    if model is None or not hasattr(model, 'feature_importances_'):
        return None
    
    features = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else selected_features
    importances = model.feature_importances_
    
    feature_names_display = {
        'frequency': '📊 Frequency',
        'monetary': '💰 Monetary',
        'unique_products': '📦 Unique Products',
        'unique_departments': '🏬 Unique Departments',
        'age_group': '🎂 Age Group',
        'income_group': '💵 Income Group',
        'hh_size': '👥 Household Size',
        'marital': '💍 Marital',
        'homeowner': '🏠 Homeowner'
    }
    
    imp_df = pd.DataFrame({
        'Fitur': [feature_names_display.get(f, f) for f in features],
        'Importance': importances,
        'Nama Asli': features
    }).sort_values('Importance', ascending=False).reset_index(drop=True)
    
    return imp_df

# =============================================================================
# MAPPING
# =============================================================================

age_mapping = {1: '19-24', 2: '25-34', 3: '35-44', 4: '45-54', 5: '55-64', 6: '65+'}
age_mapping_rev = {v: k for k, v in age_mapping.items()}
income_mapping = {
    0: 'UNKNOWN',
    1: 'UNDER 15K',
    2: '15-24K',
    3: '25-34K',
    4: '35-49K',
    5: '50-74K',
    6: '75-99K',
    7: '100-124K',
    8: '125-149K',
    9: '150-174K',
    10: '175-199K',
    11: '200-249K',
    12: '250K+'
}
# income_mapping = {
#     0: 'Unemployeed',
#     1: 'Under 15K', 2: '15-24K', 3: '25-34K', 4: '35-49K', 5: '50-74K',
#     6: '75-99K', 7: '100-124K', 8: '125-149K', 9: '150-174K', 10: '175-199K', 11: '200K+'
# }
income_mapping_rev = {v: k for k, v in income_mapping.items()}

hh_mapping = {1: '1 orang', 2: '2 orang', 3: '3 orang', 4: '4 orang', 5: '5+ orang'}
hh_mapping_rev = {v: k for k, v in hh_mapping.items()}

marital_mapping = {1: 'Married', 2: 'Single', 3: 'UNKNOWN'}
marital_mapping_rev = {v: k for k, v in marital_mapping.items()}

homeowner_mapping = {1: 'Homeowner', 2: 'Renter'}
homeowner_mapping_rev = {v: k for k, v in homeowner_mapping.items()}

# =============================================================================
# FUNGSI PREDIKSI 
# =============================================================================

def predict_churn(input_data):
    """Prediksi churn dengan threshold 37% dan segmentasi"""
    if model is None:
        return None, None, None, None
    
    input_df = pd.DataFrame([input_data])
    if hasattr(model, 'feature_names_in_'):
        input_df = input_df[model.feature_names_in_]
    
    proba = model.predict_proba(input_df)[0][1]
    
    # Threshold 37% (kompromi terbaik)
    threshold = 0.37
    pred = 1 if proba >= threshold else 0
    
    # Tambahkan segmentasi
    if proba < 0.35:
        segment = "🌟 LOYAL SEJATI"
        action = "Biarkan, beri reward"
    elif proba < 0.45:
        segment = "⚠️ EARLY WARNING"
        action = "Intervensi ringan (email)"
    elif proba < 0.50:
        segment = "🔥 HIGH RISK"
        action = "Intervensi agresif (telepon + voucher)"
    else:
        segment = "💀 LOST"
        action = "Kampanye reaktivasi"
    
    return proba, pred, segment, action

# =============================================================================
# CSS CUSTOM
# =============================================================================

st.markdown("""
<style>
    .profit-badge {
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .result-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 2px solid #f0f0f0;
    }
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        border-radius: 10px;
    }
    .segment-badge {
        padding: 0.5rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def run():
    # HEADER dengan PROFIT BADGE
    if metrics:
        profit = metrics.get('profit_per_1000', 42_040_000)
        recall = metrics.get('recall', 0.648)
        roc_auc = metrics.get('roc_auc', 0.796)
        threshold_display = metrics.get('threshold', 0.37)  # Ambil dari metrics
        
    if model is None:
        st.warning("⚠️ Model tidak dapat dimuat")
        st.stop()
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔮 Prediksi Churn", 
        "📊 Business Impact", 
        "📈 Model Performance",
        "ℹ️ Tentang Model"
    ])
    
    # =========================================================================
    # TAB 1: PREDIKSI CHURN
    # =========================================================================
    
    with tab1:
        st.markdown("#### 📝 Form CHURN Prediction:")
        
        # =====================================================================
        # FORM INPUT - DEMOGRAFI DULU
        # =====================================================================
        
        # ROW 1: DEMOGRAFI
        st.markdown("**👤 Data Demografi**")
        demo_col1, demo_col2, demo_col3, demo_col4, demo_col5 = st.columns(5)
        
        with demo_col1:
            age_options = list(age_mapping.values())
            current_age = st.session_state.get('age', 3)
            age_default = age_mapping.get(current_age, '35-44')
            age_index = age_options.index(age_default) if age_default in age_options else 2
            age_label = st.selectbox("🎂 Umur", options=age_options, index=age_index, key="age_select")
            age = age_mapping_rev[age_label]
        
        with demo_col2:
            income_options = list(income_mapping.values())
            current_income = st.session_state.get('income', 5)
            income_default = income_mapping.get(current_income, '50-74K')
            income_index = income_options.index(income_default) if income_default in income_options else 4
            income_label = st.selectbox("💰 Pendapatan", options=income_options, index=income_index, key="inc_select")
            income = income_mapping_rev[income_label]
        
        with demo_col3:
            hh_options = list(hh_mapping.values())
            current_hh = st.session_state.get('hh', 2)
            hh_default = hh_mapping.get(current_hh, '2 orang')
            hh_index = hh_options.index(hh_default) if hh_default in hh_options else 1
            hh_label = st.selectbox("👥 Jml Keluarga", options=hh_options, index=hh_index, key="hh_select")
            hh = hh_mapping_rev[hh_label]
        
        with demo_col4:
            marital_options = list(marital_mapping.values())
            current_marital = st.session_state.get('marital', 1)
            marital_default = marital_mapping.get(current_marital, 'Married')
            marital_index = marital_options.index(marital_default) if marital_default in marital_options else 0
            marital_label = st.selectbox("💍 Status Nikah", options=marital_options, index=marital_index, key="mar_select")
            marital = marital_mapping_rev[marital_label]
        
        with demo_col5:
            homeowner_options = list(homeowner_mapping.values())
            current_homeowner = st.session_state.get('homeowner', 1)
            homeowner_default = homeowner_mapping.get(current_homeowner, 'Homeowner')
            homeowner_index = homeowner_options.index(homeowner_default) if homeowner_default in homeowner_options else 0
            homeowner_label = st.selectbox("🏠 Status Rumah", options=homeowner_options, index=homeowner_index, key="home_select")
            homeowner = homeowner_mapping_rev[homeowner_label]
        
        # ROW 2: PERILAKU BELANJA
        st.markdown("**📊 Perilaku Belanja**")
        behav_col1, behav_col2, behav_col3, behav_col4 = st.columns(4)
        
        with behav_col1:
            frequency = st.number_input(
                "🔄 Frequency (kali)",
                min_value=0, max_value=100,
                value=st.session_state.get('frequency', 10),
                step=1,
                key="freq_input"
            )
        
        with behav_col2:
            monetary = st.number_input(
                "💰 Monetary ($)",
                min_value=0, max_value=10_000_000,
                value=st.session_state.get('monetary', 500_000),
                step=50_000,
                key="mon_input"
            )
        
        with behav_col3:
            unique_products = st.number_input(
                "📦 Unique Products",
                min_value=0, max_value=200,
                value=st.session_state.get('unique_products', 20),
                step=1,
                key="prod_input"
            )
        
        with behav_col4:
            unique_departments = st.number_input(
                "🏬 Unique Departments",
                min_value=0, max_value=30,
                value=st.session_state.get('unique_departments', 8),
                step=1,
                key="dept_input"
            )
        
        # Tombol prediksi
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            predict_clicked = st.button("🔮 PREDIKSI CHURN", use_container_width=True, type="primary")
        
        # =====================================================================
        # HASIL PREDIKSI - FULL
        # =====================================================================
        if predict_clicked:
            # Update session state
            st.session_state.frequency = frequency
            st.session_state.monetary = monetary
            st.session_state.unique_products = unique_products
            st.session_state.unique_departments = unique_departments
            st.session_state.age = age
            st.session_state.income = income
            st.session_state.hh = hh
            st.session_state.marital = marital
            st.session_state.homeowner = homeowner
            
            input_data = {
                'frequency': frequency,
                'monetary': monetary,
                'unique_products': unique_products,
                'unique_departments': unique_departments,
                'age_group': age,
                'income_group': income,
                'hh_size': hh,
                'marital': marital,
                'homeowner': homeowner
            }
            
            # Panggil fungsi dengan 4 return value
            proba, pred, segment, action = predict_churn(input_data)
            
            if proba is not None:
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown("### 📊 Hasil Prediksi")
                
                # Tampilkan SEGMENTASI
                if proba < 0.35:
                    segment_color = "#4CAF50"
                elif proba < 0.45:
                    segment_color = "#FF9800"
                elif proba < 0.50:
                    segment_color = "#F44336"
                else:
                    segment_color = "#9C27B0"
                
                st.markdown(f"""
                <div style='background: {segment_color}20; padding: 1rem; border-radius: 10px; border-left: 5px solid {segment_color}; margin-bottom: 1rem;'>
                    <h4 style='color: {segment_color}; margin: 0;'>{segment}</h4>
                    <p style='color: #333333; margin: 0;'>{action}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 1. TAMPILAN UTAMA
                # 1. TAMPILAN UTAMA
                col_proba1, col_proba2, col_proba3 = st.columns(3)

                with col_proba1:
                    loyal_proba = 1 - proba
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                                border-radius: 15px; border: none; box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
                                height: 100%;'>
                        <h3 style='color: #333333; margin: 0; font-weight: 600;'>✅ LOYAL</h3>
                        <p style='font-size: 2.5rem; font-weight: bold; color: #1b5e20; margin: 0.5rem 0;'>{loyal_proba:.1%}</p>
                        <p style='color: #388e3c; margin: 0; font-size: 0.9rem;'>Probabilitas Loyal</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_proba2:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); 
                                border-radius: 15px; border: none; box-shadow: 0 4px 15px rgba(244, 67, 54, 0.2);
                                height: 100%;'>
                        <h3 style='color: #333333; margin: 0; font-weight: 600;'>🚨 CHURN</h3>
                        <p style='font-size: 2.5rem; font-weight: bold; color: #b71c1c; margin: 0.5rem 0;'>{proba:.1%}</p>
                        <p style='color: #d32f2f; margin: 0; font-size: 0.9rem;'>Probabilitas Churn</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_proba3:
                    threshold = metrics.get('threshold', 0.37)
                    winner = "CHURN" if proba >= threshold else "LOYAL"
                    
                    if winner == "CHURN":
                        # Merah elegan
                        bg_gradient = "linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)"
                        accent_color = "#b71c1c"
                        shadow_color = "rgba(244, 67, 54, 0.2)"
                    else:
                        # Hijau elegan
                        bg_gradient = "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)"
                        accent_color = "#1b5e20"
                        shadow_color = "rgba(76, 175, 80, 0.2)"
                    
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1.5rem; background: {bg_gradient}; 
                                border-radius: 15px; border: none; box-shadow: 0 4px 15px {shadow_color};
                                height: 100%;'>
                        <h3 style='color: #333333; margin: 0; font-weight: 500; letter-spacing: 1px;'>KEPUTUSAN</h3>
                        <h2 style='color: {accent_color}; margin: 0.5rem 0; font-size: 2.2rem; font-weight: 700;'>{winner}</h2>
                        <div style='background: rgba(255,255,255,0.5); padding: 0.3rem; border-radius: 20px; margin-top: 0.5rem;'>
                            <p style='color: #6a1b9a; margin: 0; font-weight: 500;'>Threshold: {threshold:.0%}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 2. METRICS
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    customer_value = metrics.get('customer_value', 1_000_000)
                    intervention_cost = metrics.get('intervention_cost', 100_000)
                    expected_value = proba * customer_value - (1-proba) * intervention_cost
                    st.metric("Expected Value", f"$ {expected_value:,.0f}")
                
                with col2:
                    confidence = max(proba, 1-proba)
                    st.metric("Confidence", f"{confidence:.1%}")
                
                with col3:
                    if proba < 0.3:
                        risk_level = "RENDAH"
                        risk_color = "#4CAF50"
                    elif proba < 0.6:
                        risk_level = "SEDANG"
                        risk_color = "#FF9800"
                    else:
                        risk_level = "TINGGI"
                        risk_color = "#F44336"
                    
                    st.markdown(f"""
                    <div style='text-align: center;'>
                        <p style='color: #666666; margin: 0;'>Risk Level:</p>
                        <h3 style='color: {risk_color}; margin: 0;'>{risk_level}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 3. PROGRESS BAR
                st.markdown("**📈 Risk Level:**")
                st.progress(proba, text=f"Churn: {proba:.1%} | Loyal: {(1-proba):.1%}")
                
                # 4. ANALISIS FAKTOR
                st.markdown("### 🔍 Analisis Faktor")
                
                col_risk1, col_risk2 = st.columns(2)
                
                with col_risk1:
                    st.markdown("**⚠️ Faktor Risiko:**")
                    risk_factors = []
                    if frequency < 5:
                        risk_factors.append("• 🔴 Frekuensi belanja rendah (<5x)")
                    if monetary < 500000:
                        risk_factors.append("• 🔴 Nilai belanja kecil (<$ 500rb)")
                    if unique_products < 10:
                        risk_factors.append("• 🔴 Variasi produk terbatas (<10)")
                    if unique_departments < 4:
                        risk_factors.append("• 🔴 Explorasi department rendah (<4)")
                    
                    if risk_factors:
                        for factor in risk_factors:
                            st.markdown(f"<span style='color: #FFFFFF;'>{factor}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #FFFFFF;'>• ✅ Tidak ada faktor risiko signifikan</span>", unsafe_allow_html=True)
                
                with col_risk2:
                    st.markdown("**🛡️ Faktor Protektif:**")
                    protective_factors = []
                    if frequency > 20:
                        protective_factors.append("• 🟢 Frekuensi belanja tinggi (>20x)")
                    if monetary > 2_000_000:
                        protective_factors.append("• 🟢 Nilai belanja besar (>$ 2jt)")
                    if unique_products > 30:
                        protective_factors.append("• 🟢 Variasi produk tinggi (>30)")
                    if unique_departments > 8:
                        protective_factors.append("• 🟢 Explorasi department luas (>8)")
                    
                    if protective_factors:
                        for factor in protective_factors:
                            st.markdown(f"<span style='color: #FFFFFF;'>{factor}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #FFFFFF;'>• ⚪ Tidak ada faktor protektif signifikan</span>", unsafe_allow_html=True)
                
                # 5. PENJELASAN THRESHOLD
                with st.expander("❓ Mengapa customer ini diprediksi CHURN?"):
                    col_exp1, col_exp2 = st.columns(2)
                    
                    with col_exp1:
                        st.markdown(f"**📊 Probabilitas Churn:** {proba:.1%}")
                    
                    with col_exp2:
                        threshold_display = metrics.get('threshold', 0.37)
                        st.markdown(f"**⚖️ Threshold:** {threshold_display:.0%}")
                        st.markdown(f"**Keputusan:** {'CHURN' if proba >= threshold_display else 'LOYAL'}")
                    
                    # Tabel threshold
                    thr_data = []
                    for thr in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.37, 0.40, 0.45, 0.50]:
                        thr_data.append({
                            "Threshold": f"{thr:.0%}",
                            "Prediksi": "CHURN" if proba >= thr else "LOYAL"
                        })
                    
                    thr_df = pd.DataFrame(thr_data)
                    st.dataframe(thr_df, use_container_width=True, hide_index=True)
                    
                    st.info("""
                    **💡 Penjelasan:**
                    - Model ini menggunakan threshold **37%** berdasarkan analisis data
                    - Threshold ini menyeimbangkan deteksi churn dan biaya intervensi
                    - Customer dengan probabilitas >37% akan direkomendasikan intervensi
                    """)
                
                # 6. REKOMENDASI
                st.markdown("### 💡 Rekomendasi")
                
                if pred == 1:
                    st.warning(f"""
                    **⚠️ {segment}**
                    
                    **Action Plan:**
                    - {action}
                    - 📧 Kirim email personalized
                    - 🎁 Voucher diskon 20-30%
                    
                    **💰 Jika berhasil:** $ {customer_value:,}
                    """)
                else:
                    st.success(f"""
                    **✅ {segment}**
                    
                    **Retention Strategy:**
                    - {action}
                    - 💎 Tawarkan produk premium
                    - 🏆 Berikan reward points
                    """)
                
                st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: BUSINESS IMPACT ( FULL )
    # =========================================================================
    
    with tab2:
        st.markdown("### 📊 Business Impact Analysis")
        
        if metrics:
            # KEY METRICS
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Profit per 1000", f"$ {metrics.get('profit_per_1000', 0):,.0f}")
            with col2:
                st.metric("Recall", f"{metrics.get('recall', 0):.1%}")
            with col3:
                st.metric("Precision", f"{metrics.get('precision', 0):.1%}")
            with col4:
                st.metric("ROC AUC", f"{metrics.get('roc_auc', 0):.3f}")
            
            # CONFUSION MATRIX VISUALIZATION
            st.markdown("#### 📊 Confusion Matrix (per 1000 customers)")
            
            tp = metrics.get('tp_per_1000', 126)
            fp = metrics.get('fp_per_1000', 156)
            fn = metrics.get('fn_per_1000', 69)
            tn = 1000 - (tp + fp + fn)
            
            # Create confusion matrix dataframe
            cm_data = {
                'Actual \\ Predicted': ['Loyal', 'Churn'],
                'Loyal': [tn, fp],
                'Churn': [fn, tp]
            }
            cm_df = pd.DataFrame(cm_data).set_index('Actual \\ Predicted')
            
            # Heatmap
            fig_cm = px.imshow(
                cm_df,
                text_auto=True,
                color_continuous_scale='Blues',
                aspect="auto",
                title="Confusion Matrix"
            )
            fig_cm.update_layout(height=400)
            st.plotly_chart(fig_cm, use_container_width=True)
            
            # BUSINESS IMPACT PIE CHART
            st.markdown("#### 💰 Distribution of Interventions")
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['✅ Customer Saved', '⚠️ False Alarm', '❌ Churn Missed'],
                values=[tp, fp, fn],
                marker_colors=['#4CAF50', '#FF9800', '#F44336'],
                textinfo='label+percent',
                hole=0.3
            )])
            fig_pie.update_layout(title="Hasil Intervensi per 1000 Customer")
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # PROFIT BREAKDOWN
            st.markdown("#### 💵 Profit Breakdown")
            
            saved_revenue = tp * metrics.get('customer_value', 1_000_000)
            lost_revenue = fn * metrics.get('customer_value', 1_000_000)
            intervention_cost = fp * metrics.get('intervention_cost', 100_000)
            net_profit = saved_revenue - lost_revenue - intervention_cost
            
            fig_waterfall = go.Figure(go.Waterfall(
                name="Profit",
                orientation="v",
                measure=["relative", "relative", "relative", "total"],
                x=["Revenue Saved", "Revenue Lost", "Intervention Cost", "NET PROFIT"],
                y=[saved_revenue, -lost_revenue, -intervention_cost, net_profit],
                text=[f"$ {saved_revenue:,.0f}", f"$ {lost_revenue:,.0f}", 
                      f"$ {intervention_cost:,.0f}", f"$ {net_profit:,.0f}"],
                textposition="outside",
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))
            fig_waterfall.update_layout(title="Profit Breakdown per 1000 Customers")
            st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # =========================================================================
    # TAB 3: MODEL PERFORMANCE
    # =========================================================================
    
    with tab3:
        st.markdown("### 📈 Model Performance Metrics")
        
        # METRICS CARDS
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Accuracy", f"{metrics.get('accuracy', 0.776):.1%}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Precision", f"{metrics.get('precision', 0.448):.1%}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("F1 Score", f"{metrics.get('f1', 0.53):.1%}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # FEATURE IMPORTANCE
        st.markdown("#### 📊 Feature Importance")
        
        imp_df = get_feature_importance()
        if imp_df is not None:
            fig_imp = px.bar(
                imp_df,
                x='Importance',
                y='Fitur',
                orientation='h',
                color='Importance',
                color_continuous_scale='viridis',
                title="Pengaruh Fitur terhadap Prediksi Churn",
                text=imp_df['Importance'].apply(lambda x: f'{x:.3f}')
            )
            fig_imp.update_layout(
                height=500,
                yaxis={'categoryorder':'total ascending'}
            )
            fig_imp.update_traces(textposition='outside')
            st.plotly_chart(fig_imp, use_container_width=True)
            
            # Top features insight
            top_3 = imp_df.head(3)['Fitur'].tolist()
            st.info(f"**💡 Insight:** 3 fitur paling berpengaruh: **{', '.join(top_3)}**")
        ##########
        # #### CONTOH KASUS ### 
        
        # =====================================================================
        # STUDI KASUS BUTTONS
        # =====================================================================
        # =====================================================================
        # STUDI KASUS - PROFIL CUSTOMER (BOX TANPA TOMBOL)
        # =====================================================================
        
        st.markdown("#### 🎯 Profil Customer & Interpretasi Threshold")
        
        # ROW 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='profile-box profile-super-loyal'>
                <div class='profile-title'>
                    <span style='font-size: 1.8rem;'>🌟</span> 
                    <span class='text-green-dark'>Super Loyal</span>
                </div>
                <div class='profile-detail text-green-dark'>
                    <p><strong>📊 Perilaku Belanja:</strong><br>
                    • Frekuensi: 45x | Belanja: Rp 9.5jt<br>
                    • Produk: 48 | Department: 14</p>
                    <p><strong>👤 Demografi:</strong><br>
                    • Umur: 45-54 | Income: 200K+<br>
                    • Menikah | 4 Keluarga | Homeowner</p>
                    <p><strong>📈 Probabilitas Churn:</strong> 33-35%</p>
                    <div class='info-badge'>
                        <span style='font-weight: bold;'>Threshold 37%:</span> 
                        <span class='text-green-dark' style='font-weight: bold;'>⬇️ DI BAWAH → LOYAL</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='profile-box profile-early-warning'>
                <div class='profile-title'>
                    <span style='font-size: 1.8rem;'>⚠️</span> 
                    <span class='text-orange-dark'>Early Warning</span>
                </div>
                <div class='profile-detail text-orange-dark'>
                    <p><strong>📊 Perilaku Belanja:</strong><br>
                    • Frekuensi: 15x | Belanja: Rp 1.2jt<br>
                    • Produk: 18 | Department: 5</p>
                    <p><strong>👤 Demografi:</strong><br>
                    • Umur: 35-44 | Income: 50-74K<br>
                    • Menikah | 3 Keluarga | Homeowner</p>
                    <p><strong>📈 Probabilitas Churn:</strong> 38-44%</p>
                    <div class='info-badge'>
                        <span style='font-weight: bold;'>Threshold 37%:</span> 
                        <span class='text-red-dark' style='font-weight: bold;'>⬆️ DI ATAS → CHURN</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ROW 2
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            <div class='profile-box profile-high-risk'>
                <div class='profile-title'>
                    <span style='font-size: 1.8rem;'>🔥</span> 
                    <span class='text-red-dark'>High Risk</span>
                </div>
                <div class='profile-detail text-red-dark'>
                    <p><strong>📊 Perilaku Belanja:</strong><br>
                    • Frekuensi: 3x | Belanja: Rp 150rb<br>
                    • Produk: 5 | Department: 2</p>
                    <p><strong>👤 Demografi:</strong><br>
                    • Umur: 19-24 | Income: Under 15K<br>
                    • Single | 1 Keluarga | Renter</p>
                    <p><strong>📈 Probabilitas Churn:</strong> 45-49%</p>
                    <div class='info-badge'>
                        <span style='font-weight: bold;'>Threshold 37%:</span> 
                        <span class='text-red-dark' style='font-weight: bold;'>⬆️ DI ATAS → CHURN</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class='profile-box profile-lost'>
                <div class='profile-title'>
                    <span style='font-size: 1.8rem;'>💀</span> 
                    <span class='text-gray-dark'>Lost Customer</span>
                </div>
                <div class='profile-detail text-gray-dark'>
                    <p><strong>📊 Perilaku Belanja:</strong><br>
                    • Frekuensi: 0x | Belanja: Rp 0<br>
                    • Produk: 0 | Department: 0</p>
                    <p><strong>👤 Demografi:</strong><br>
                    • Umur: 19-24 | Income: Unknown<br>
                    • Single | 1 Keluarga | Renter</p>
                    <p><strong>📈 Probabilitas Churn:</strong> >50%</p>
                    <div class='info-badge'>
                        <span style='font-weight: bold;'>Threshold 37%:</span> 
                        <span class='text-red-dark' style='font-weight: bold;'>⬆️ DI ATAS → CHURN</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    
    # =========================================================================
    # TAB 4: TENTANG MODEL
    # =========================================================================
    
    with tab4:
        st.markdown("### ℹ️ Tentang Model")
        st.markdown("""
            **Dataset:** Dunnhumby - The Complete Journey
            
            Dataset ini berisi data transaksi riil dari **2,500 rumah tangga** selama 2 tahun dari jaringan ritel di AS. 
            Data ini mencakup seluruh pembelian rumah tangga, tidak hanya dari kategori terbatas.
            
            **Sumber Data:** [Kaggle - Dunnhumby The Complete Journey](https://www.kaggle.com/datasets/frtgnn/dunnhumby-the-complete-journey/)
            
            **Karakteristik Dataset:**
            - **Periode:** 2 tahun data transaksi
            - **Jumlah Rumah Tangga:** 2,500
            - **Total Transaksi:** ± 250,000 transaksi
            - **Jumlah Produk:** ± 90,000 produk unik
            
            **Tabel yang digunakan:**
            - `transaction_data.csv` - Data transaksi (quantity, sales, diskon)
            - `hh_demographic.csv` - Data demografi rumah tangga
            - `product.csv` - Informasi produk (departemen, brand)
            """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🤖 Algoritma:** Random Forest Classifier
            
            **📊 9 Fitur:**
            - Frequency (Frekuensi belanja)
            - Monetary (Total belanja)
            - Unique Products (Variasi produk)
            - Unique Departments (Variasi department)
            - Age Group (Kelompok umur)
            - Income Group (Pendapatan)
            - Household Size (Jumlah keluarga)
            - Marital Status (Status pernikahan)
            - Homeowner (Status rumah)
            """)
        
        with col2:
            threshold_display = metrics.get('threshold', 0.37)
            st.markdown(f"""
            **⚙️ Parameter Model:**
            - n_estimators: 200
            - max_depth: 10
            - min_samples_split: 20
            - min_samples_leaf: 10
            - class_weight: balanced
            
            **🎯 Threshold:** {threshold_display:.0%}
            
            **📈 Performa (5-Fold CV):**
            - Recall: {metrics.get('recall', 0.648):.1%}
            - Precision: {metrics.get('precision', 0.448):.1%}
            - ROC AUC: {metrics.get('roc_auc', 0.796):.3f}
            
            **💰 Business Impact:**
            - Profit: $ {metrics.get('profit_per_1000', 42_040_000):,}/1000
            """)
        
        st.markdown("---")
        st.markdown("#### 🎯 Cara Interpretasi Hasil")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**< 35%**\n🌟 Loyal Sejati\n✅ Biarkan")
        with col2:
            st.warning("**35% - 45%**\n⚠️ Early Warning\n📧 Intervensi Ringan")
        with col3:
            st.error("**45% - 50%**\n🔥 High Risk\n📞 Intervensi Agresif")

# =============================================================================
# UNTUK DIPANGGIL DARI MAIN.PY
# =============================================================================

def show():
    run()

__all__ = ['run', 'show']