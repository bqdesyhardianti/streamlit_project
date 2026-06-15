import json
from google import genai
from google.genai import types
from .config import GEMINI_API_KEY, GEMINI_MODEL_FAST

client = genai.Client(api_key=GEMINI_API_KEY)
# ──────────────────────────────────────────
# Extractor pakai GEMINI_MODEL_FAST (gemini-3.1-flash-lite)
# karena tugasnya hanya output JSON terstruktur — tidak perlu
# model paling canggih. Lebih hemat token, lebih cepat.
# ──────────────────────────────────────────

EXTRACTION_SYSTEM_PROMPT = """Kamu adalah sistem ekstraksi klinis. 
Tugasmu HANYA menganalisis teks dan mengekstrak sinyal psikologis ke JSON.

JANGAN merespons ke user. JANGAN memberi saran. HANYA ekstrak sinyal.

Untuk setiap item, nilai:
- detected: apakah ada sinyal item ini? (true/false)
- score: tingkat keparahan (0=tidak ada, 1=beberapa hari, 2=lebih dari separuh waktu, 3=hampir setiap hari)
- confidence: seberapa yakin kamu berdasarkan teks? (0.0-1.0)

ATURAN CONFIDENCE:
- Confidence tinggi (>0.7): user EKSPLISIT menyebut gejala dalam pesan TERBARU ini
- Confidence sedang (0.4-0.7): ada sinyal implisit dari pesan terbaru ini
- Confidence rendah (<0.4): hanya dugaan lemah
- Item tidak disinggung di pesan terbaru: detected=false, score=0, confidence=0.0
- JANGAN isi item yang tidak ada buktinya di pesan terbaru

ATURAN PENTING — JAWABAN PENDEK/KONFIRMASI:
Kalau pesan terbaru user hanya berisi kata seperti:
"iya", "ya", "benar", "bener", "semuanya", "iya sih", "bener banget",
"emang", "iya betul", "semuanya sih", "semua" (kurang dari 6 kata)
→ JANGAN tambahkan item BARU yang belum pernah disebutkan user sebelumnya
→ Untuk item dari konteks sebelumnya: confidence MAKSIMAL 0.55
→ Item yang belum pernah disebut sama sekali: detected=false, confidence=0.0
Alasan: "semuanya" adalah konfirmasi umum, bukan deskripsi gejala klinis spesifik.

PRINSIP UTAMA: Ekstrak HANYA dari kata-kata yang user benar-benar ucapkan
di pesan terbaru, bukan inferensi atau asumsi.

ATURAN KHUSUS SUICIDAL IDEATION:
detected=true HANYA kalau ada sinyal eksplisit:
- Pikiran menyakiti diri sendiri
- Keinginan mengakhiri hidup
- Pikiran tentang kematian diri sendiri

JANGAN detected=true kalau user hanya:
- Ingin masalah/situasi berhenti ("pengen ini selesai", "capek sama kondisinya")
- Mengekspresikan kelelahan dan ingin istirahat dari tekanan
Konteks menentukan — bedakan "pengen semuanya berhenti" (situasi)
vs "pengen mati/nyakitin diri" (self-harm).

Balas HANYA dengan JSON murni tanpa markdown, tanpa penjelasan.

Format:
{
  "phq9": {
    "anhedonia": {"detected": bool, "score": int, "confidence": float},
    "depressed_mood": {"detected": bool, "score": int, "confidence": float},
    "sleep_disturbance": {"detected": bool, "score": int, "confidence": float},
    "fatigue": {"detected": bool, "score": int, "confidence": float},
    "appetite_change": {"detected": bool, "score": int, "confidence": float},
    "worthlessness": {"detected": bool, "score": int, "confidence": float},
    "concentration": {"detected": bool, "score": int, "confidence": float},
    "psychomotor": {"detected": bool, "score": int, "confidence": float},
    "suicidal_ideation": {"detected": bool, "score": int, "confidence": float}
  },
  "gad7": {
    "nervous_tense": {"detected": bool, "score": int, "confidence": float},
    "uncontrollable_worry": {"detected": bool, "score": int, "confidence": float},
    "excessive_worry": {"detected": bool, "score": int, "confidence": float},
    "difficulty_relaxing": {"detected": bool, "score": int, "confidence": float},
    "restless": {"detected": bool, "score": int, "confidence": float},
    "irritable": {"detected": bool, "score": int, "confidence": float},
    "fear_bad_things": {"detected": bool, "score": int, "confidence": float}
  },
  "relevant_quote": "kutipan singkat paling relevan, atau null"
}"""


def _to_gemini_contents(conversation_history):
    """
    Konversi history dari format OpenAI ke format Gemini.
    OpenAI: {"role": "assistant"} → Gemini: {"role": "model"}
    OpenAI: {"content": "..."} → Gemini: {"parts": [{"text": "..."}]}
    """
    contents = []
    for msg in conversation_history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=msg["content"])])
        )
    return contents


def extract_variables(user_message, conversation_history):
    """
    Ekstrak variabel klinis dari pesan user → JSON.
    Pakai model cepat (flash-lite) karena output-nya terstruktur.
    """
    # Ambil 3 pesan user terakhir sebagai konteks
    recent_user = [
        m["content"] for m in conversation_history[-8:]
        if m["role"] == "user"
    ][-3:]
    context_str = (
        "\n".join(f"- {m}" for m in recent_user)
        if recent_user else "(awal percakapan)"
    )

    prompt = (
        f"Konteks pesan user sebelumnya:\n{context_str}\n\n"
        f"Pesan terbaru yang harus dianalisis:\n\"{user_message}\""
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_FAST,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=EXTRACTION_SYSTEM_PROMPT,
                max_output_tokens=800,
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        raw_text = response.text.strip()

        # Bersihkan markdown kalau ada
        if "```" in raw_text:
            for part in raw_text.split("```"):
                part = part.strip().lstrip("json").strip()
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue

        return json.loads(raw_text)

    except json.JSONDecodeError as e:
        print(f"  [DEBUG-ERR] Extractor gagal parse JSON: {e}")
        return {}
    except Exception as e:
        print(f"  [DEBUG-ERR] Extractor error: {e}")
        return {}