# projects/mental_health_bot/feature_builder.py
import pandas as pd

FEATURE_COLUMNS = [
    "phq9_level",
    "overall_risk",
    "gad7_level",
    "mood_dysregulation_risk",
    "psychotic_risk",
    "awercap_score",
    "pwercap_score",
    "active_coping",
    "acceptance",
    "emotion_focused",
    "avoidance",
    "religious",

    "merasa_tidak_berharga",
    "sering_bersedih_menangis",
    "sulit_berpikir_jernih",
    "niat_bunuh_diri",
    "mudah_takut",
    "tangan_gemetaran",
    "merasa_tidak_berguna",
    "kehilangan_minat",
    "cemas_tegang_khawatir",
    "lelah_sepanjang_waktu",
    "kurang_bahagia",
    "sulit_menikmati_aktivitas",
    "pekerjaan_sebagai_beban",
    "sulit_mengambil_keputusan",
    "kurang_nafsu_makan",
    "tidur_tidak_nyenyak",
    "mudah_lelah",
    "sakit_kepala",
    "keluhan_bagian_perut",

    "status_pernikahan",
    "status_pegawai",

    # sisanya nanti kita isi
]


def build_feature_vector(state):
    features = {}
    # ==================================================
    # DEFAULT VALUE
    # ==================================================
    for col in FEATURE_COLUMNS:
        features[col] = 0
    # ==================================================
    # PHQ9
    # ==================================================
    features["phq9_level"] = 0
    # ==================================================
    # GAD7
    # ==================================================
    features["gad7_level"] = 0
    # ==================================================
    # OVERALL RISK
    # ==================================================
    features["overall_risk"] = 0

    # ==================================================
    # DEMO MAPPING
    # nanti kita isi dari tracker
    # ==================================================

    df = pd.DataFrame([features])

    return df