from pathlib import Path

from pdd_ai_coach.parser import parse_rules

lines = Path("data/pdd_rules.txt").read_text(encoding="utf-8").splitlines()
rules = parse_rules(lines)

print("пунктов:", len(rules))
print(rules[0])
print(rules[-1])