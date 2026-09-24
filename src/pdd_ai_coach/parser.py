import re
from dataclasses import dataclass

CHAPTER_RE = re.compile(r"^Глава (\d+)\. (.+)$")
RULE_RE = re.compile(r"^(\d+(?:-\d+)?)\. (.+)$")


@dataclass
class ParsedRule:
    number: str
    text: str
    chapter_number: int
    chapter_title: str
    note: str = "" 


def parse_rules(lines: list[str]) -> list[ParsedRule]:
    rules: list[ParsedRule] = []
    chapter_number = 0
    chapter_title = ""
    current: ParsedRule | None = None
    in_note = False  

    for line in lines:
        chapter_match = CHAPTER_RE.match(line)
        if chapter_match:
            if current is not None:
                rules.append(current)
                current = None
            chapter_number = int(chapter_match.group(1))
            chapter_title = chapter_match.group(2)
            in_note = False 
            continue

        rule_match = RULE_RE.match(line)
        if rule_match:
            if current is not None:
                rules.append(current)
            current = ParsedRule(
                number=rule_match.group(1),
                text=rule_match.group(2),
                chapter_number=chapter_number,
                chapter_title=chapter_title,
            )
            in_note = False  
            continue

        if line.startswith("Сноска.") and current is not None:
            current.note = line
            in_note = True
            continue

        if current is not None:
            if in_note: 
                current.note += " " + line
            else:
                current.text += " " + line

    if current is not None:
        rules.append(current)

    return rules