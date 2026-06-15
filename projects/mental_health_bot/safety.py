from google.genai import types
from .llm_call import generate
from .config import GEMINI_MODEL

CRISIS_ACTIVE = [
    "bunuh diri", "mau mati", "ingin mati",
    "mengakhiri hidup", "akhiri hidup", "akhirin hidup",
    "menyakiti diri", "nyakitin diri sendiri", "nyakiti diri",
    "overdosis", "gantung diri", "terjun",
    "pengen bunuh diri", "mau bunuh diri",
    "kepikiran buat nyakitin", "mau nyakitin diri",
]

CRISIS_PASSIVE = [
    "pengen ngilang", "pengen menghilang",
    "ga mau ada", "ga mau hidup", "udah ga mau hidup",
    "capek hidup", "bosen hidup",
    "mati aja", "mending mati", "mati aja deh",
    "ga ada gunanya hidup", "lebih baik ga ada",
    "mending aku gaada", "mending gaada aja",
]

_HOTLINE   = "🆘  Into The Light Indonesia: 119 ext 8\n    (Tersedia 24 jam, gratis)"
_GROUNDING = "Aku di sini. Kamu tidak sendirian."


def check_safety(text):
    text_lower = text.lower()
    for kw in CRISIS_ACTIVE:
        if kw in text_lower:
            return True, "active"
    for kw in CRISIS_PASSIVE:
        if kw in text_lower:
            return True, "passive"
    return False, None


def _generate_acknowledgment(user_message, conversation_history, crisis_level):
    if crisis_level == "active":
        instruction = (
            "User mengungkapkan pikiran untuk menyakiti diri atau mengakhiri hidupnya.\n"
            "Acknowledge SPESIFIK apa yang mereka ceritakan.\n"
            "Tunjukkan kamu hadir dan mendengar — tenang, bukan panik.\n"
            "JANGAN menyuruh apapun. JANGAN tanya 'apakah kamu aman?'.\n"
            "Maksimal 3 kalimat yang benar-benar manusiawi."
        )
    else:
        instruction = (
            "User mengungkapkan kelelahan yang sangat dalam atau keinginan menghilang.\n"
            "Acknowledge betapa beratnya yang mereka rasakan — spesifik.\n"
            "Hadir sepenuhnya, tidak panik, tidak ceramah.\n"
            "Maksimal 3 kalimat."
        )

    recent = [
        m["content"] for m in conversation_history[-6:]
        if m["role"] == "user"
    ][-3:]
    context_str = "\n".join(f"- {m}" for m in recent) if recent else "(awal percakapan)"

    system_prompt = (
        f"Kamu adalah Waras, teman bicara yang hangat.\n{instruction}\n\n"
        "Balas HANYA dengan kalimat acknowledgment.\n"
        "Bahasa Indonesia informal, hangat, manusiawi.\n"
        "JANGAN sertakan hotline, saran, atau pertanyaan. Pakai 'aku', bukan 'saya'."
    )

    contents = [
        types.Content(role="user", parts=[types.Part(
            text=(
                f"Konteks percakapan:\n{context_str}\n\n"
                f"Pesan terbaru user:\n\"{user_message}\""
            )
        )])
    ]

    result = generate(
        system_prompt=system_prompt,
        contents=contents,
        max_output_tokens=150,
        temperature=0.75,
    )

    return result or (
        "Aku dengar kamu, dan aku serius mendengarkan ini.\n"
        "Kamu tidak harus menanggung semua ini sendirian."
    )


def build_crisis_response(user_message, conversation_history, crisis_level):
    acknowledgment = _generate_acknowledgment(
        user_message, conversation_history, crisis_level
    )
    return (
        f"{acknowledgment}\n\n"
        f"Ada yang bisa menemanimu lebih jauh:\n"
        f"{_HOTLINE}\n\n"
        f"{_GROUNDING}"
    )


def get_crisis_response():
    return (
        "Aku dengar kamu, dan aku benar-benar peduli.\n\n"
        f"Ada yang bisa menemanimu:\n{_HOTLINE}\n\n"
        f"{_GROUNDING}"
    )