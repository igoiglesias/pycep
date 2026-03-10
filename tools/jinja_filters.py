from markupsafe import Markup


def format_error_messages(error_messages: str) -> str:
    return Markup("<br> ".join(error_messages.split(";")) if error_messages else "")