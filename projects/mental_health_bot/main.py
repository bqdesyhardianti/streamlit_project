import re
from .tracker   import create_session, update_tracker, get_coverage_summary
from .safety    import check_safety, build_crisis_response
from .extractor import extract_variables
from .responder import generate_response, is_short_answer
from .scorer    import (
    calculate_phq9, calculate_gad7,
    get_phq9_severity, get_gad7_severity,
    get_risk_tier, get_recommendation,
)
from wrapup    import generate_personal_wrapup

# ══════════════════════════════════════════════════════════
# WARAS v0.9 — Main Loop
#
# Merged dari versi user + v0.9 improvements:
# + wrapup.py integration: Layer 1 + Layer 3 personal summary
# + Stagnation: min coverage 12/16 (naik dari 10)
# + Hard limit turn 20 (naik dari 15)
# + Extraction tetap jalan di fase wrap-up
# + WRAPUP_WITH_PROBE: fire untuk semua trigger, bukan hanya is_done
# + Versi: v0.9
# ══════════════════════════════════════════════════════════

SHOW_DEBUG = True

DONE_SIGNALS = [
    "sudah cukup", "cukup sih", "cukup deh", "makasih",
    "terima kasih", "udah ya", "udah deh", "segini aja",
    "oke deh", "okay deh", "mau selesai", "mau keluar",
    "cukup ya", "sampai sini", "sampe sini", "itu aja sih",
    "itu aja", "udah itu aja",
]

WRAPUP_OFFER = (
    "Dari yang kamu ceritakan tadi, ada cukup banyak yang lagi "
    "kamu rasakan. Boleh aku share sedikit apa yang aku tangkep "
    "dari obrolan kita? Santai aja, kamu bebas mau dengerin "
    "atau engga. 😊"
)

WRAPUP_OFFER_WITH_PROBE = (
    "Makasih udah mau cerita ya — aku dengerin semua yang kamu "
    "bagi tadi. Sebelum aku share apa yang aku tangkep, boleh "
    "aku tanya satu hal dulu? Di tengah semua beban ini... "
    "kadang ada nggak pikiran yang lebih gelap, kayak pengen "
    "semuanya berhenti aja? Bebas jawab atau nggak. 😊"
)

WRAPUP_CLOSE = (
    "Oke, nggak apa-apa. Kapanpun mau cerita lagi, aku di sini ya. "
    "Semoga hari-harimu segera lebih ringan. 💙"
)


def detect_done(text):
    t = text.lower().strip()
    return any(s in t for s in DONE_SIGNALS)


def detect_wrapup_response(text):
    """
    Deteksi jawaban user terhadap wrap-up offer.
    NO dicek lebih dulu. 'ya' hanya valid di awal kalimat atau pesan pendek.
    """
    t = text.lower().strip()
    words = t.split()
    if not words:
        return 'unclear'

    YES_EXACT = {'iya', 'ya', 'oke', 'ok', 'boleh', 'mau', 'yuk',
                 'silakan', 'gas', 'lanjut', 'monggo', 'iyaa', 'yaa',
                 'okay', 'oke deh', 'iya deh', 'boleh dong', 'mau dong'}
    NO_EXACT  = {'engga', 'ga', 'tidak', 'nggak', 'gak', 'skip',
                 'nanti', 'gausah', 'ga usah', 'engga deh'}
    if t in YES_EXACT: return 'yes'
    if t in NO_EXACT:  return 'no'

    # NO keywords — dicek lebih dulu (lebih aman)
    NO_KEYWORDS = ['engga', 'nggak', 'tidak', 'gak', 'skip', 'gausah',
                   'ga usah', 'ga mau', 'nanti aja', 'belum mau']
    for kw in NO_KEYWORDS:
        if kw in t: return 'no'

    # YES keywords (kecuali 'ya' — ditangani terpisah)
    YES_KEYWORDS = ['iya', 'boleh', 'oke', 'okay', 'ok sih', 'yuk',
                    'lanjut', 'dengerin', 'silakan', 'mau dong',
                    'monggo', 'share aja']
    for kw in YES_KEYWORDS:
        if kw in t: return 'yes'

    # 'ya' valid sebagai yes HANYA kalau di awal atau kalimat pendek
    if words[0] == 'ya': return 'yes'
    if len(words) <= 3 and 'ya' in words: return 'yes'

    return 'unclear'


def should_trigger_stagnation(coverage_history, current_turn):
    """
    Stagnasi boleh trigger kalau:
    - Turn >= 5
    - Coverage sudah >= 12/16 (v0.9: naik dari 10)
    - Coverage tidak naik dalam 3 turn terakhir
    ATAU hard limit turn >= 20 (v0.9: naik dari 15)
    """
    if current_turn >= 20:
        return True  # Soft hard limit
    if current_turn < 5 or len(coverage_history) < 3:
        return False
    if coverage_history[-1] < 12:
        return False  # Belum cukup tercover
    return len(set(coverage_history[-3:])) == 1


def print_debug(state, extraction_result=None, label=""):
    if not SHOW_DEBUG:
        return
    coverage = get_coverage_summary(state)
    sep = "─" * 52
    print(f"\n  {sep}")
    if label:
        print(f"  [DEBUG] {label}")
    print(f"  [DEBUG] Turn #{state['turn_count']}")
    print(f"  [DEBUG] Coverage: PHQ-9 {coverage['phq9_progress']} | "
          f"GAD-7 {coverage['gad7_progress']} | Total {coverage['total_covered']}/16")

    if extraction_result:
        detected = [
            f"{sc}.{item}: score={data['score']}, conf={data['confidence']:.2f}"
            for sc in ["phq9", "gad7"]
            if sc in extraction_result
            for item, data in extraction_result[sc].items()
            if data.get("detected") and data.get("confidence", 0) > 0.3
        ]
        if detected:
            print(f"  [DEBUG] Extracted:")
            for d in detected:
                print(f"    ✓ {d}")
        else:
            print(f"  [DEBUG] Tidak ada item terdeteksi turn ini")

        if extraction_result.get("relevant_quote"):
            print(f"  [DEBUG] Quote: \"{extraction_result['relevant_quote']}\"")

    missing = coverage["phq9_missing"] + coverage["gad7_missing"]
    if missing and len(missing) <= 12:
        print(f"  [DEBUG] Belum: {', '.join(missing)}")
    print(f"  {sep}\n")


def print_final_results(state):
    """
    Developer view — scoring untuk portfolio demo.
    Fase 2: akan terhubung ke ML model + visual dashboard.
    """
    p    = calculate_phq9(state)
    g    = calculate_gad7(state)
    tier = get_risk_tier(state, p, g)
    rec  = get_recommendation(tier, p, g)

    sep = "═" * 60
    print(f"\n{sep}")
    print("  HASIL SESI — Developer View")
    print(f"  [Fase 2: ML model + visual dashboard]")
    print(f"{sep}")
    print(f"  PHQ-9 : {p['score']:>2}/27  ({get_phq9_severity(p['score'])})")
    print(f"          Items covered: {p['items_covered']}/9")
    print(f"  GAD-7 : {g['score']:>2}/21  ({get_gad7_severity(g['score'])})")
    print(f"          Items covered: {g['items_covered']}/7")
    print(f"  Risk  : {tier}")
    print(f"{sep}")
    print("\n  Rekomendasi (fallback):")
    print(f"  {'─'*56}")
    for line in rec.split("\n"):
        print(f"  {line}")
    print(f"{sep}\n")


def run_session():
    print("\n" + "═" * 60)
    print("  WARAS — Employee Mental Health Assistant")
    print("  Prototype v0.9 | PHQ-9 + GAD-7")
    print("─" * 60)
    print("  Perintah: 'debug' | 'skor' | 'selesai'")
    print("═" * 60 + "\n")

    state             = create_session()
    coverage_history  = []
    wrapup_mode       = False
    results_shown     = False
    consecutive_short = 0
    suicidal_probe_sent = False

    opening = (
        "Hai! Aku Waras, teman bicara yang siap mendengarkan. "
        "Gimana hari-harimu belakangan ini? "
        "Bebas cerita apa aja ya 😊"
    )
    print(f"Waras: {opening}\n")
    state["conversation_history"].append({
        "role": "assistant", "content": opening
    })

    while True:
        try:
            user_input = input("Kamu: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  [Sesi dihentikan]")
            break

        if not user_input:
            continue

        # ── Special commands ─────────────────────────────────
        if user_input.lower() == "selesai":
            if state["turn_count"] == 0:
                print("\nWaras: Sampai jumpa! Kalau mau ngobrol lagi, aku di sini ya. 💙\n")
                break
            if wrapup_mode:
                print(f"\nWaras: {WRAPUP_CLOSE}\n")
                break
            # Ada percakapan — masuk wrap-up gracefully
            wrapup_mode = True
            cov_now     = get_coverage_summary(state)
            suicidal_ok = cov_now["suicidal_covered"]
            has_risk_signal = any(
                state["phq9"][item]["score"] >= 2
                for item in ["depressed_mood", "worthlessness", "anhedonia"]
            )
            use_probe = (
                not suicidal_ok
                and has_risk_signal
                and not suicidal_probe_sent
            )
            offer = WRAPUP_OFFER_WITH_PROBE if use_probe else WRAPUP_OFFER
            print(f"\nWaras: {offer}\n")
            state["conversation_history"].append(
                {"role": "assistant", "content": offer}
            )
            if SHOW_DEBUG:
                print(f"  [DEBUG] Wrap-up triggered: selesai command\n")
            continue

        if user_input.lower() == "debug":
            print_debug(state, label="Manual debug")
            continue
        if user_input.lower() == "skor":
            print_final_results(state)
            results_shown = True
            continue

        # ── Handle wrap-up response ──────────────────────────
        if wrapup_mode:
            # v0.9: Ekstrak dulu sebelum proses yes/no
            # Kalau user jawab "gampang terdistraksi" — data itu masuk tracker
            _extr_wrapup = extract_variables(
                user_input, state["conversation_history"]
            )
            if _extr_wrapup:
                state = update_tracker(state, _extr_wrapup)

            rt = detect_wrapup_response(user_input)
            state["conversation_history"].append(
                {"role": "user", "content": user_input}
            )

            if rt == "yes":
                print()
                print("  [⏳ menyiapkan rangkuman...]\n")
                p    = calculate_phq9(state)
                g    = calculate_gad7(state)
                tier = get_risk_tier(state, p, g)
                # Layer 1 + 3: personal summary dari kata-kata user sendiri
                wrapup_text = generate_personal_wrapup(
                    state, state["conversation_history"], tier
                )
                print(f"Waras: {wrapup_text}\n")
                state["conversation_history"].append(
                    {"role": "assistant", "content": wrapup_text}
                )
                # Developer view — tetap tampil untuk portfolio demo
                print_final_results(state)
                results_shown = True
                break

            elif rt == "no":
                print(f"\nWaras: {WRAPUP_CLOSE}\n")
                break

            else:
                # User menjawab dengan konten, bukan yes/no → re-offer natural
                clarify = (
                    "Aku dengerin kamu. Dari semua yang udah kita bahas tadi, "
                    "boleh ya aku share sedikit apa yang aku tangkep? 😊"
                )
                print(f"\nWaras: {clarify}\n")
                state["conversation_history"].append(
                    {"role": "assistant", "content": clarify}
                )
            continue

        state["turn_count"] += 1

        # ── Track jawaban pendek ─────────────────────────────
        if is_short_answer(user_input):
            consecutive_short += 1
        else:
            consecutive_short = 0

        # ── [1] Safety Check ─────────────────────────────────
        is_crisis, crisis_level = check_safety(user_input)
        if is_crisis:
            state["crisis_detected"] = True
            print("\n  [⏳ menyiapkan respons...]\n")
            crisis_resp = build_crisis_response(
                user_input, state["conversation_history"], crisis_level
            )
            print(f"Waras: {crisis_resp}\n")
            print("  [SISTEM: ⚠️  Crisis detected. "
                  "Ketik 'selesai' untuk keluar.]\n")
            state["conversation_history"].append(
                {"role": "user",      "content": user_input}
            )
            state["conversation_history"].append(
                {"role": "assistant", "content": crisis_resp}
            )
            consecutive_short = 0
            continue

        # ── [2] Extractor ────────────────────────────────────
        extraction_result = extract_variables(
            user_input, state["conversation_history"]
        )

        # ── [3] Update Tracker ───────────────────────────────
        if extraction_result:
            state = update_tracker(state, extraction_result)

        # ── [4] Coverage ─────────────────────────────────────
        coverage = get_coverage_summary(state)
        coverage_history.append(coverage["total_covered"])

        is_stagnant = should_trigger_stagnation(
            coverage_history, state["turn_count"]
        )
        is_done = detect_done(user_input)
        if is_done and coverage["total_covered"] < 6:
            is_done = False

        # ── [5] Responder ────────────────────────────────────
        bot_response = generate_response(
            user_input,
            state["conversation_history"],
            coverage,
            state["turn_count"],
            consecutive_short,
            is_done=is_done,
            suicidal_probe_sent=suicidal_probe_sent,
        )

        # Track apakah probe suicidal sudah terkirim
        probe_signals = [
            "takut sama diri kamu", "keselamatan dirimu",
            "pikiran yang lebih gelap", "bikin kamu khawatir",
            "takut sama diri",
        ]
        if any(sig in bot_response for sig in probe_signals):
            suicidal_probe_sent = True

        print(f"\nWaras: {bot_response}\n")
        print_debug(state, extraction_result)

        # ── [6] Update History ───────────────────────────────
        state["conversation_history"].append(
            {"role": "user",      "content": user_input}
        )
        state["conversation_history"].append(
            {"role": "assistant", "content": bot_response}
        )

        # ── [7] Wrap-up Check ────────────────────────────────
        should_wrapup = (
            is_stagnant or
            is_done or
            coverage["is_complete"]
        )

        if should_wrapup and not state["crisis_detected"]:
            wrapup_mode = True

            trigger = ("hard limit"   if state["turn_count"] >= 20
                       else "stagnasi"  if is_stagnant
                       else "user selesai" if is_done
                       else "semua tercover")
            if SHOW_DEBUG:
                print(f"  [DEBUG] Wrap-up triggered: {trigger}\n")

            # v0.9: probe suicidal masuk ke wrap-up offer untuk SEMUA trigger
            cov_now     = get_coverage_summary(state)
            suicidal_ok = cov_now["suicidal_covered"]
            has_risk_signal = any(
                state["phq9"][item]["score"] >= 2
                for item in ["depressed_mood", "worthlessness", "anhedonia"]
            )
            use_probe_offer = (
                not suicidal_ok
                and has_risk_signal
                and not suicidal_probe_sent
                and not state["crisis_detected"]
            )

            offer = WRAPUP_OFFER_WITH_PROBE if use_probe_offer else WRAPUP_OFFER
            print(f"Waras: {offer}\n")
            state["conversation_history"].append(
                {"role": "assistant", "content": offer}
            )

    # ── Final results ─────────────────────────────────────
    if state["turn_count"] > 0 and not results_shown:
        print_final_results(state)


if __name__ == "__main__":
    run_session()