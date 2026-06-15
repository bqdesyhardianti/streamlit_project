from .tracker import update_tracker, get_coverage_summary
from .extractor import extract_variables
from .responder import generate_response, is_short_answer
from .safety import check_safety, build_crisis_response


def process_message(user_input, state):

    # turn count
    state["turn_count"] += 1

    # safety
    is_crisis, crisis_level = check_safety(user_input)

    if is_crisis:

        response = build_crisis_response(
            user_input,
            state["conversation_history"],
            crisis_level
        )

        state["conversation_history"].append(
            {"role": "user", "content": user_input}
        )

        state["conversation_history"].append(
            {"role": "assistant", "content": response}
        )

        return response, state

    # extractor
    extraction_result = extract_variables(
        user_input,
        state["conversation_history"]
    )

    if extraction_result:

        state = update_tracker(
            state,
            extraction_result
        )

    coverage = get_coverage_summary(state)

    response = generate_response(
        user_input,
        state["conversation_history"],
        coverage,
        state["turn_count"],
        0,
        is_done=False,
        suicidal_probe_sent=False
    )

    state["conversation_history"].append(
        {"role": "user", "content": user_input}
    )

    state["conversation_history"].append(
        {"role": "assistant", "content": response}
    )

    return response, state