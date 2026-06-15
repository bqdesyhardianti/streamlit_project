from .config import CONFIDENCE_THRESHOLD
# ──────────────────────────────────────────
# PENJELASAN STRUKTUR DATA
#
# State sesi adalah sebuah dictionary Python.
# Anggap ini sebagai "memori" chatbot selama satu sesi percakapan.
#
# Untuk setiap item klinis (misal: anhedonia), kita simpan 3 hal:
#   - detected   : apakah sinyal ini terdeteksi? (True/False)
#   - score      : seberapa parah? (0=tidak ada, 1=beberapa hari,
#                  2=lebih dari separuh waktu, 3=hampir setiap hari)
#   - confidence : seberapa yakin LLM? (0.0 sampai 1.0)
#
# Item hanya dianggap "covered" kalau confidence >= CONFIDENCE_THRESHOLD (0.65)
# ──────────────────────────────────────────


def create_session():
    """
    Inisialisasi state baru untuk satu sesi percakapan.
    Dipanggil sekali di awal, sebelum percakapan dimulai.
    """
    return {
        # 9 item PHQ-9 (skala depresi, skor total 0-27)
        "phq9": {
            "anhedonia":         {"detected": False, "score": 0, "confidence": 0.0},  # kehilangan minat
            "depressed_mood":    {"detected": False, "score": 0, "confidence": 0.0},  # sedih/hopeless
            "sleep_disturbance": {"detected": False, "score": 0, "confidence": 0.0},  # gangguan tidur
            "fatigue":           {"detected": False, "score": 0, "confidence": 0.0},  # kelelahan
            "appetite_change":   {"detected": False, "score": 0, "confidence": 0.0},  # perubahan nafsu makan
            "worthlessness":     {"detected": False, "score": 0, "confidence": 0.0},  # tidak berharga/rasa bersalah
            "concentration":     {"detected": False, "score": 0, "confidence": 0.0},  # sulit fokus/keputusan
            "psychomotor":       {"detected": False, "score": 0, "confidence": 0.0},  # gerak/bicara lebih lambat/gelisah
            "suicidal_ideation": {"detected": False, "score": 0, "confidence": 0.0},  # ⚠️ WAJIB selalu dicek
        },

        # 7 item GAD-7 (skala kecemasan, skor total 0-21)
        "gad7": {
            "nervous_tense":        {"detected": False, "score": 0, "confidence": 0.0},  # gugup/tegang
            "uncontrollable_worry": {"detected": False, "score": 0, "confidence": 0.0},  # khawatir tak terkontrol
            "excessive_worry":      {"detected": False, "score": 0, "confidence": 0.0},  # khawatir berlebih
            "difficulty_relaxing":  {"detected": False, "score": 0, "confidence": 0.0},  # sulit rileks
            "restless":             {"detected": False, "score": 0, "confidence": 0.0},  # gelisah
            "irritable":            {"detected": False, "score": 0, "confidence": 0.0},  # mudah marah
            "fear_bad_things":      {"detected": False, "score": 0, "confidence": 0.0},  # mudah takut hal buruk
        },

        # Metadata sesi
        "conversation_history": [],   # riwayat percakapan (format OpenAI)
        "turn_count": 0,              # hitungan giliran percakapan
        "crisis_detected": False,     # flag jika ada sinyal krisis
    }


def update_tracker(state, extraction_result):
    """
    Update state berdasarkan hasil ekstraksi LLM.

    Aturan update: hanya overwrite kalau confidence baru LEBIH TINGGI
    dari yang sudah tersimpan. Ini mencegah data yang sudah confident
    ditimpa oleh hasil ekstraksi yang lebih lemah.
    """
    for scale in ["phq9", "gad7"]:
        if scale not in extraction_result:
            continue

        for item, data in extraction_result[scale].items():
            if item not in state[scale]:
                continue  # abaikan item yang tidak dikenal

            new_confidence = data.get("confidence", 0.0)
            current_confidence = state[scale][item]["confidence"]

            # Hanya update kalau confidence baru lebih tinggi
            if new_confidence > current_confidence:
                state[scale][item]["detected"]   = data.get("detected", False)
                state[scale][item]["score"]       = data.get("score", 0)
                state[scale][item]["confidence"]  = new_confidence

    return state


def get_coverage_summary(state):
    """
    Hitung berapa item yang sudah tercover (confidence >= threshold).

    Fungsi ini dipanggil setelah setiap update untuk menentukan:
    - Apa yang sudah diketahui
    - Apa yang masih perlu digali
    - Apakah sesi sudah bisa diselesaikan
    """
    phq9_covered = [
        item for item, data in state["phq9"].items()
        if data["confidence"] >= CONFIDENCE_THRESHOLD
    ]
    phq9_missing = [
        item for item in state["phq9"]
        if state["phq9"][item]["confidence"] < CONFIDENCE_THRESHOLD
    ]
    gad7_covered = [
        item for item, data in state["gad7"].items()
        if data["confidence"] >= CONFIDENCE_THRESHOLD
    ]
    gad7_missing = [
        item for item in state["gad7"]
        if state["gad7"][item]["confidence"] < CONFIDENCE_THRESHOLD
    ]

    return {
        "phq9_covered":    phq9_covered,
        "phq9_missing":    phq9_missing,
        "gad7_covered":    gad7_covered,
        "gad7_missing":    gad7_missing,
        "phq9_progress":   f"{len(phq9_covered)}/9",
        "gad7_progress":   f"{len(gad7_covered)}/7",
        "suicidal_covered": state["phq9"]["suicidal_ideation"]["confidence"] >= CONFIDENCE_THRESHOLD,
        "total_covered":   len(phq9_covered) + len(gad7_covered),
        "total_items":     16,
        "is_complete":     len(phq9_covered) == 9 and len(gad7_covered) == 7,
    }