def _first_error(serializer) -> str:
    """extract the first human-readable error from serializer.errors."""
    for field, messages in serializer.errors.items():
        msg = str(messages[0]) if isinstance(messages, list) and messages else str(messages)
        if field == "non_field_errors":
            return msg
        return f"{field}: {msg}"
    return "invalid data."


