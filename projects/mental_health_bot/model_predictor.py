import joblib
import streamlit as st

MODEL_PATH = "projects/mental_health_bot/model/best_model.pkl"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

def predict_stress(features_df):

    model = load_model()

    prediction = model.predict(features_df)[0]
    probability = model.predict_proba(features_df)[0]

    return prediction, probability
# import joblib


# MODEL_PATH = "projects/mental_health_bot/model/best_model.pkl"
# model = joblib.load(MODEL_PATH)

# def predict_stress(features_df):
#     prediction = model.predict(features_df)[0]
#     probability = model.predict_proba(features_df)[0]
#     return prediction, probability


