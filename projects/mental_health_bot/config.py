import os
from dotenv import load_dotenv


load_dotenv()

# ── Gemini (provider utama) ──────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Responder + Safety → model terkuat
GEMINI_MODEL      = "gemini-3.5-flash"

# Extractor → lebih cepat dan hemat, cukup untuk output JSON
GEMINI_MODEL_FAST = "gemini-3.1-flash-lite"

# ── Threshold coverage ───────────────────────────────────
CONFIDENCE_THRESHOLD = 0.50