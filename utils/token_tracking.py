from typing import Any


def token_usage_tracking(
    token_history: dict[str, Any], usage_data: dict[str, Any]
) -> dict[str, Any] | Any:
    """Track and accumulate token usage over multiple calls.

    Args:
        token_history (dict[str, Any]): Historical token usage data
        usage_data (dict[str, Any]): Current token usage data

    Returns:
        dict[str, Any] | Any: Updated token usage data
    """
    if not token_history:
        token_history = usage_data
        return token_history

    if token_history.get("input_token_details") and usage_data.get(
        "input_token_details"
    ):
        if token_history["input_token_details"].get("audio") and usage_data[
            "input_token_details"
        ].get("audio"):
            token_history["input_token_details"]["audio"] += usage_data[
                "input_token_details"
            ]["audio"]
        if token_history["input_token_details"].get("cache_read") and usage_data.get(
            "input_token_details"
        ).get("cache_read"):
            token_history["input_token_details"]["cache_read"] += usage_data[
                "input_token_details"
            ]["cache_read"]
    if token_history.get("input_tokens") and usage_data.get("input_tokens"):
        token_history["input_tokens"] += usage_data["input_tokens"]
    if token_history.get("output_token_details") and usage_data.get(
        "output_token_details"
    ):
        if token_history["output_token_details"].get("audio") and usage_data.get(
            "output_token_details"
        ).get("audio"):
            token_history["output_token_details"]["audio"] += usage_data[
                "output_token_details"
            ]["audio"]
        if token_history["output_token_details"].get("reasoning") and usage_data.get(
            "output_token_details"
        ).get("reasoning"):
            token_history["output_token_details"]["reasoning"] += usage_data[
                "output_token_details"
            ]["reasoning"]
    if token_history.get("output_tokens") and usage_data.get("output_tokens"):
        token_history["output_tokens"] += usage_data["output_tokens"]
    if token_history.get("total_tokens") and usage_data.get("total_tokens"):
        token_history["total_tokens"] += usage_data["total_tokens"]

    return token_history
