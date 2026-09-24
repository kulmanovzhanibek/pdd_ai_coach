import re

MAX_CHARS = 1500
SUBPOINT_RE = re.compile(r"\s(?=\d+(?:-\d+)?\)\s)")


def split_rule(text: str) -> list[str]:
    if len(text) <= MAX_CHARS:
        return [text]

    parts = SUBPOINT_RE.split(text)
    lead_in, subpoints = parts[0], parts[1:]
    if not subpoints:
        return [text]

    return [f"{lead_in} {subpoint}" for subpoint in subpoints]