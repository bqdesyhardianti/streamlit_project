import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MODEL_FAST = "gemini-2.5-flash-lite"

CONFIDENCE_THRESHOLD = 0.50

# import os
# import streamlit as st
# from dotenv import load_dotenv

# # Load .env untuk lokal
# load_dotenv()

# # Ambil API key:
# # 1. dari .env (lokal)
# # 2. dari Streamlit Secrets (cloud)

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     try:
#         GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
#     except Exception:
#         GEMINI_API_KEY = None

# # Model
# GEMINI_MODEL = "gemini-2.5-flash"
# GEMINI_MODEL_FAST = "gemini-2.5-flash-lite"

# # Threshold
# CONFIDENCE_THRESHOLD = 0.50
# import os
# from dotenv import load_dotenv


# load_dotenv()

# # ── Gemini (provider utama) ──────────────────────────────
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Responder + Safety → model terkuat
# GEMINI_MODEL      = "gemini-3.5-flash"

# # Extractor → lebih cepat dan hemat, cukup untuk output JSON
# GEMINI_MODEL_FAST = "gemini-3.1-flash-lite"

# # ── Threshold coverage ───────────────────────────────────
# CONFIDENCE_THRESHOLD = 0.50