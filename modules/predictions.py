import streamlit as st
import pandas as pd
import os
import joblib

def show_prediction():
    st.title("Customer Churn Prediction 📊")
    st.write("Masukkan informasi pelanggan untuk memprediksi churn.")

    # -----------------------------
    # Form input (selalu tampil)
    # -----------------------------
    with st.form(key="churn_form"):
        gender = st.selectbox("Gender", ["Male", "Female"])
        senior_citizen = st.selectbox("Senior Citizen", [0, 1])
        partner = st.selectbox("Partner", ["Yes", "No"])
        dependents = st.selectbox("Dependents", ["Yes", "No"])
        tenure = st.number_input("Tenure (bulan)", min_value=0, step=1)
        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
        monthly_charges = st.number_input("Monthly Charges", min_value=0.0, step=1.0, format="%.2f")
        total_charges = st.number_input("Total Charges", min_value=0.0, step=1.0, format="%.2f")
        
        submit_button = st.form_submit_button("Predict Churn")

    # -----------------------------
    # Cek apakah model ada
    # -----------------------------
    model_path = "best_churn_model.pkl"
    if not os.path.exists(model_path):
        st.warning("⚠️ Model belum tersedia. Form input tetap bisa dicoba, tapi prediksi tidak dapat dilakukan.")
        return  # keluar dari fungsi agar prediksi tidak dijalankan

    # -----------------------------
    # Prediksi hanya jika model ada
    # -----------------------------
    if submit_button:
        model = joblib.load(model_path)
        
        input_data = pd.DataFrame({
            "gender": [gender],
            "SeniorCitizen": [senior_citizen],
            "Partner": [partner],
            "Dependents": [dependents],
            "tenure": [tenure],
            "PhoneService": [phone_service],
            "MultipleLines": [multiple_lines],
            "InternetService": [internet_service],
            "OnlineSecurity": [online_security],
            "OnlineBackup": [online_backup],
            "DeviceProtection": [device_protection],
            "TechSupport": [tech_support],
            "StreamingTV": [streaming_tv],
            "StreamingMovies": [streaming_movies],
            "Contract": [contract],
            "PaperlessBilling": [paperless_billing],
            "PaymentMethod": [payment_method],
            "MonthlyCharges": [monthly_charges],
            "TotalCharges": [total_charges]
        })

        prediction = model.predict(input_data)[0]
        prediction_proba = model.predict_proba(input_data)[0][1]

        st.subheader("Hasil Prediksi:")
        st.write(f"**Churn:** {'Yes' if prediction == 1 else 'No'}")
        st.write(f"**Probability:** {prediction_proba:.2%}")
