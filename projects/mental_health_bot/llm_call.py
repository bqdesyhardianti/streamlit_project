import time
from google import genai
from google.genai import types

from .config import GEMINI_API_KEY, GEMINI_MODEL
client = genai.Client(api_key=GEMINI_API_KEY)

# ──────────────────────────────────────────
# Helper terpusat untuk semua Gemini API call.
# Menangani 2 masalah sekaligus:
#   1. Retry otomatis kalau 503 (server overload)
#   2. Fallback ke model lebih stabil kalau tetap gagal
#
# Hierarki model:
#   gemini-3.5-flash         ← terbaik, tapi sering 503
#       ↓ (kalau gagal 3x)
#   gemini-3.1-flash         ← stabil, kualitas hampir sama
#       ↓ (kalau gagal lagi)
#   gemini-3.1-flash-lite    ← paling stabil, backup terakhir
# ──────────────────────────────────────────

FALLBACK_MODELS = [
    GEMINI_MODEL,              # gemini-3.5-flash (utama)
    "gemini-3.1-flash",        # fallback 1
    "gemini-3.1-flash-lite",   # fallback 2
]

MAX_RETRIES   = 3
RETRY_DELAY   = 2  # detik, naik 2x tiap retry (exponential backoff)


def generate(
    system_prompt: str,
    contents,
    max_output_tokens: int = 300,
    temperature: float = 0.75,
) -> str:
    """
    Wrapper terpusat untuk semua LLM call di Waras.

    Cara kerja:
    1. Coba model utama (3.5-flash) sampai MAX_RETRIES kali
    2. Kalau masih gagal, turun ke fallback berikutnya
    3. Ulangi sampai semua model dicoba
    4. Kalau semua gagal → return None (caller handle sendiri)

    Parameters:
    - system_prompt : instruksi ke LLM
    - contents      : list types.Content (history + pesan user)
    - max_output_tokens, temperature : seperti biasa
    """
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    for model in FALLBACK_MODELS:
        delay = RETRY_DELAY

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                # Berhasil — log kalau pakai fallback
                if model != GEMINI_MODEL:
                    print(f"  [DEBUG] Pakai fallback model: {model}")
                return response.text.strip()

            except Exception as e:
                err_str = str(e)
                is_503  = "503" in err_str or "UNAVAILABLE" in err_str
                is_429  = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str

                if is_503:
                    # Server overload → retry dengan backoff
                    if attempt < MAX_RETRIES:
                        print(f"  [DEBUG] 503 model {model}, "
                              f"retry {attempt}/{MAX_RETRIES} "
                              f"dalam {delay}s...")
                        time.sleep(delay)
                        delay *= 2  # exponential backoff: 2s, 4s, 8s
                    else:
                        print(f"  [DEBUG] {model} gagal {MAX_RETRIES}x, "
                              f"coba fallback...")
                        break  # keluar dari retry loop, coba model berikutnya

                elif is_429:
                    # Rate limit (RPM) → tunggu 60 detik lalu retry
                    # Kalau daily limit, retry tidak akan berhasil tapi tidak ada pilihan lain
                    if attempt < MAX_RETRIES:
                        wait = 60
                        print(f"  [DEBUG] Rate limit 429, tunggu {wait}s lalu retry...")
                        time.sleep(wait)
                    else:
                        print(f"  [DEBUG-ERR] Rate limit masih hit setelah retry, coba model lain...")
                        break

                else:
                    # Error lain (auth, dll) → langsung fail
                    print(f"  [DEBUG-ERR] API error: {err_str[:120]}")
                    return None

    # Semua model gagal
    print("  [DEBUG-ERR] Semua model gagal.")
    return None