from collections import Counter
from pathlib import Path

from pdd_ai_coach.parser import parse_rules

lines = Path("data/pdd_rules.txt").read_text(encoding="utf-8").splitlines()
rules = parse_rules(lines)

numbers = [rule.number for rule in rules]
counter = Counter(numbers)
duplicates = [number for number, count in counter.items() if count > 1]

print("всего:", len(numbers))
print("уникальных:", len(set(numbers)))
print("дубли:", duplicates)

with_notes = [rule for rule in rules if "Сноска" in rule.text]
print("пунктов со сносками:", len(with_notes))
if with_notes:
    print(with_notes[0].number, with_notes[0].text[:300])


rule_43 = next(r for r in rules if r.number == "43")
print("ТЕКСТ:", rule_43.text)
print("СНОСКА:", rule_43.note)    