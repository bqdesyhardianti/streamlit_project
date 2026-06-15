from google.genai import types
from .llm_call import generate

# ══════════════════════════════════════════════════════════
# WARAS — Wrap-up Layer 1 + Layer 3
#
# Layer 1: Personal Summary
#   Pantulkan apa yang didengar menggunakan kata user sendiri.
#   Bukan angka, bukan nama skala, bukan interpretasi baru.
#
# Layer 3: Rekomendasi Personal
#   Lahir dari protective factors yang user sebut + intensitas sinyal.
#   Bukan template — dibangun dari percakapan itu sendiri.
#
# Layer 2 (ML Model → Dashboard) belum diimplementasi.
# Data dari tracker akan diteruskan ke sana di Fase berikutnya.
# ══════════════════════════════════════════════════════════

_CRISIS_WRAPUP = (
    "Aku benar-benar menghargai kepercayaanmu untuk berbagi semua ini tadi. "
    "Yang kamu rasakan itu nyata dan berat — dan kamu tidak harus menanggungnya sendirian.\n\n"
    "Langkah yang paling penting sekarang: tolong hubungi seseorang yang bisa "
    "menemanimu lebih jauh.\n"
    "🆘  Into The Light Indonesia: 119 ext 8\n"
    "    (Tersedia 24 jam, gratis)\n\n"
    "Kalau kamu dalam situasi darurat, pergi ke UGD rumah sakit terdekat atau hubungi 112."
)

WRAPUP_SYSTEM_PROMPT = """Kamu adalah Waras — teman bicara AI yang hangat dan peduli.
Sesi percakapan baru saja selesai. Tugasmu: buat wrap-up yang terasa personal dan bermakna,
bukan seperti laporan atau diagnosis.

Wrap-up terdiri dari DUA bagian yang mengalir natural — tidak perlu label atau header.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BAGIAN 1 — REFLEKSI (3-4 kalimat)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pantulkan apa yang kamu dengar menggunakan kata-kata dan tema
yang USER SENDIRI sudah ucapkan dalam percakapan.

ATURAN KETAT — WAJIB DIIKUTI:
✓ HANYA gunakan kata, situasi, dan tema yang user eksplisit sebutkan
✓ Kalau user bilang "capek", pakai "capek" — bukan "kelelahan" atau "fatigue"
✓ Kalau user bilang "bos galak", sebut itu — jangan digeneralisasi
✗ JANGAN sebut nama skala, skor, atau istilah klinis apapun
✗ JANGAN buat interpretasi atau kesimpulan yang tidak ada buktinya
✗ JANGAN bilang "kondisimu baik" atau "tidak ada yang perlu dikhawatirkan"
   kecuali memang benar-benar tidak ada sinyal apapun
✗ JANGAN mulai dengan "Jadi kamu..." atau kalimat diagnosis
✓ Akui beratnya tanpa mendramatisasi
✓ Mulai dengan situasi konkret yang user ceritakan

Contoh BAGUS:
"Dari yang kamu ceritain tadi, kamu lagi ngelewatin masa yang cukup padat —
beban kerja yang terus numpuk, bos yang sering bikin nggak nyaman, dan rasa
sendirian di lingkungan yang harusnya suportif. Ditambah tidur yang mulai
keganggu dan energi yang makin terkuras hari demi hari. Itu bukan hal kecil."

Contoh BURUK:
"Berdasarkan percakapan kita, kamu mengalami gejala depresi..."
"Skor kamu menunjukkan adanya kecemasan yang..."
"Kamu mungkin mengalami burnout..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BAGIAN 2 — LANGKAH KE DEPAN (2-3 kalimat)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rekomendasi yang lahir dari apa yang user sendiri ceritakan.

Prioritas:
1. Kalau user menyebut orang/hal yang suportif (sahabat, keluarga, iman, komunitas, hobi)
   → jadikan itu titik start yang natural
   → Contoh: "Kamu tadi cerita soal sahabat lama yang kamu percaya —
              itu modal besar. Mungkin mulai dari sana?"
2. Kalau sinyal cukup berat (risk=High) → arahkan ke profesional
   dengan framing suportif, bukan menakutkan
   → "bukan karena ada yang salah, tapi karena kamu layak dapat support yang proper"
3. Kalau tidak ada protective factor yang teridentifikasi
   → fokus pada langkah kecil yang terasa manageable hari ini

JANGAN:
- Template generik seperti "jaga tidur dan makan" tanpa ada konteks
- Sebut nama institusi atau layanan spesifik kecuali memang dibutuhkan
- Bilang "segera hubungi psikolog" dengan nada mendesak (kecuali risk=High/Crisis)

Pisahkan kedua bagian dengan baris kosong.
Bahasa Indonesia informal, hangat, seperti teman yang benar-benar mendengarkan.
Selalu gunakan "aku", tidak pernah "saya"."""


def generate_personal_wrapup(state, conversation_history, risk_tier):
    """
    Generate wrap-up personal Layer 1 + Layer 3.

    Input:
    - state              : session state lengkap (phq9, gad7, dll)
    - conversation_history : list pesan {"role": ..., "content": ...}
    - risk_tier          : "Crisis" | "High" | "Moderate" | "Low"

    Output: string teks wrap-up untuk ditampilkan ke user.
    """
    if risk_tier == "Crisis":
        return _CRISIS_WRAPUP

    # Kumpulkan semua ucapan user — ini sumber kebenaran
    user_messages = [
        m["content"] for m in conversation_history
        if m["role"] == "user"
    ]

    if not user_messages:
        return (
            "Makasih ya udah mampir. Kalau ada yang mau diceritakan, "
            "aku selalu ada di sini. 💙"
        )

    user_context = "\n".join(f'- "{m}"' for m in user_messages)

    risk_calibration = {
        "High": (
            "Sinyal yang muncul cukup berat. "
            "Arahkan ke profesional dengan framing suportif — "
            "'kamu layak dapat support yang lebih', bukan 'kamu harus segera ke dokter'."
        ),
        "Moderate": (
            "Ada beberapa hal yang perlu perhatian. "
            "Sarankan langkah kecil dulu, singgung opsi profesional sebagai pilihan, bukan keharusan."
        ),
        "Low": (
            "Sinyal ringan. Fokus validasi dan langkah self-care konkret "
            "yang lahir dari apa yang user ceritakan."
        ),
    }.get(risk_tier, "")

    prompt = (
        f"Berikut semua hal yang user ceritakan dalam sesi ini "
        f"(gunakan HANYA ini sebagai sumber):\n\n"
        f"{user_context}\n\n"
        f"Panduan kalibrasi rekomendasi: {risk_calibration}\n\n"
        f"Buat wrap-up personal sesuai instruksi sistem. "
        f"Pantulkan kata-kata user sendiri. Jangan tambah interpretasi baru."
    )

    contents = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]

    result = generate(
        system_prompt=WRAPUP_SYSTEM_PROMPT,
        contents=contents,
        max_output_tokens=380,
        temperature=0.68,
    )

    return result or (
        "Makasih ya udah mau berbagi sebanyak ini tadi. "
        "Yang kamu rasakan itu nyata, dan kamu layak mendapat dukungan yang lebih dari sekadar ngobrol.\n\n"
        "Kalau ada yang berat terus berlanjut, jangan ragu untuk cerita ke orang yang kamu percaya — "
        "atau pertimbangkan bicara sama profesional. Bukan karena ada yang salah, "
        "tapi karena kamu layak dapat support yang proper."
    )