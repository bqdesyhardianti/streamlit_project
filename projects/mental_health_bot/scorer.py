from .config import CONFIDENCE_THRESHOLD
# ──────────────────────────────────────────
# PENJELASAN: SCORING ENGINE
#
# Ini adalah komponen rule-based yang paling deterministik.
# Tidak ada LLM di sini — murni aritmatika dan kondisional.
#
# PHQ-9: jumlahkan 9 skor item (masing-masing 0-3) → total 0-27
# GAD-7: jumlahkan 7 skor item (masing-masing 0-3) → total 0-21
#
# Cutoff klinis berdasarkan literatur yang sudah tervalidasi.
# ──────────────────────────────────────────


def calculate_phq9(state):
    """
    Hitung skor PHQ-9 dari state.
    Hanya item yang confidence >= threshold yang dihitung.
    Item yang belum tercover dianggap 0 (konservatif / underestimate).
    """
    total = sum(data["score"] for data in state["phq9"].values())
    covered = sum(
        1 for data in state["phq9"].values()
        if data["confidence"] >= CONFIDENCE_THRESHOLD
    )
    return {
        "score":         total,
        "items_covered": covered,
        "total_items":   9,
        "is_complete":   covered == 9,
    }


def calculate_gad7(state):
    """Hitung skor GAD-7 dari state."""
    total = sum(data["score"] for data in state["gad7"].values())
    covered = sum(
        1 for data in state["gad7"].values()
        if data["confidence"] >= CONFIDENCE_THRESHOLD
    )
    return {
        "score":         total,
        "items_covered": covered,
        "total_items":   7,
        "is_complete":   covered == 7,
    }


def get_phq9_severity(score):
    """
    Interpretasi klinis PHQ-9.
    Cutoff dari: Kroenke et al. (2001) + validasi Asia.
    """
    if score <= 4:   return "Minimal"
    if score <= 9:   return "Mild (Ringan)"
    if score <= 14:  return "Moderate (Sedang)"
    if score <= 19:  return "Moderately Severe (Sedang-Berat)"
    return "Severe (Berat)"


def get_gad7_severity(score):
    """
    Interpretasi klinis GAD-7.
    Cutoff dari: Spitzer et al. (2006).
    """
    if score <= 4:   return "Minimal"
    if score <= 9:   return "Mild (Ringan)"
    if score <= 14:  return "Moderate (Sedang)"
    return "Severe (Berat)"


def get_risk_tier(state, phq9_result, gad7_result):
    """
    Tentukan risk tier berdasarkan skor dan sinyal klinis.

    Hierarki (urutan ini penting!):
    1. Crisis  → ada suicidal ideation (score >= 1) ATAU flag crisis_detected
    2. High    → PHQ-9 >= 15 ATAU GAD-7 >= 15
    3. Moderate→ PHQ-9 >= 10 ATAU GAD-7 >= 10
    4. Low     → semua di bawah threshold

    ⚠️ DISCLAIMER: Risk tier ini adalah OUTPUT SCREENING, bukan diagnosis klinis.
    Tidak boleh digunakan sebagai pengganti assessment profesional.
    """
    # Crisis check PERTAMA — tidak peduli skor lain
    if state["phq9"]["suicidal_ideation"]["score"] >= 1:
        return "Crisis"
    if state["crisis_detected"]:
        return "Crisis"

    phq9_score = phq9_result["score"]
    gad7_score  = gad7_result["score"]

    if phq9_score >= 15 or gad7_score >= 15:
        return "High"
    if phq9_score >= 10 or gad7_score >= 10:
        return "Moderate"
    return "Low"


def get_recommendation(risk_tier, phq9_result=None, gad7_result=None):
    """
    Rekomendasi personal berdasarkan risk tier.
    Bahasa untuk user — tidak ada angka skor, tidak ada nama skala.

    Kalau coverage terlalu rendah, berikan pesan partial screening
    daripada rekomendasi yang bisa menyesatkan.
    """
    # Guard: kalau data tidak cukup, jangan kasih rekomendasi definitif
    if phq9_result and gad7_result:
        total_covered = phq9_result["items_covered"] + gad7_result["items_covered"]
        if total_covered < 8 and risk_tier == "Low":
            return (
                "Dari percakapan kita yang singkat, aku belum bisa memberi "
                "gambaran lengkap — masih banyak yang belum sempat kita bahas. 😊\n\n"
                "Tapi dari yang kamu ceritakan, ada beberapa hal yang layak "
                "mendapat perhatian lebih:\n"
                "• Pertimbangkan bicara ke seseorang yang kamu percaya\n"
                "• Kalau perasaan ini terus berlanjut, jangan ragu ke konselor\n"
                "• Kamu bisa kembali kapan saja buat cerita lebih\n\n"
                "Makasih udah mau berbagi ya. 💙"
            )
    recs = {
        "Low": (
            "Dari percakapan kita, kondisimu secara keseluruhan terlihat cukup baik. 💙\n\n"
            "Beberapa hal yang bisa membantu menjaga wellbeing-mu:\n"
            "• Jaga rutinitas tidur dan makan\n"
            "• Luangkan waktu untuk hal yang kamu nikmati\n"
            "• Tetap terhubung dengan orang-orang yang suportif\n\n"
            "Kalau ada yang berubah atau kamu ingin cerita lagi, aku selalu ada."
        ),
        "Moderate": (
            "Terima kasih sudah mau cerita. Aku bisa lihat kamu sedang menanggung cukup banyak. 🤝\n\n"
            "Yang aku sarankan:\n"
            "• Pertimbangkan bicara dengan konselor atau psikolog — ini bukan tanda kelemahan\n"
            "• Coba ceritakan bebanmu ke orang terdekat yang kamu percaya\n"
            "• Jaga self-care dasar: tidur, makan, dan gerak\n\n"
            "Kamu tidak harus melewati ini sendirian."
        ),
        "High": (
            "Aku benar-benar menghargai kepercayaanmu untuk berbagi ini. 💙\n\n"
            "Apa yang kamu rasakan terdengar sangat berat, dan bantuan profesional tersedia:\n"
            "• Segera hubungi psikolog atau psikiater untuk dukungan lebih lanjut\n"
            "• Kalau perusahaanmu punya layanan konseling, ini saat yang tepat\n"
            "• Bicara ke seseorang yang kamu percaya tentang apa yang kamu rasakan\n\n"
            "Kamu sudah mengambil langkah pertama yang berani dengan mau bicara hari ini."
        ),
        "Crisis": (
            "Aku dengar kamu, dan aku sangat peduli dengan keselamatanmu sekarang.\n\n"
            "🆘 Tolong hubungi bantuan segera:\n"
            "   Into The Light Indonesia: 119 ext 8\n"
            "   (Tersedia 24 jam, gratis)\n\n"
            "Kalau kamu dalam bahaya langsung, hubungi 112 atau pergi ke UGD rumah sakit terdekat.\n\n"
            "Kamu tidak sendirian dalam ini. Ada orang yang peduli dan siap membantu."
        ),
    }
    return recs.get(risk_tier, recs["Low"])