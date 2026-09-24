from pathlib import Path

from pypdf import PdfReader

PDF_PATH = Path("data/pdd.pdf")
OUT_PATH = Path("data/pdd_rules.txt")

# Правила дорожного движения — это главы 1–26.
# Дальше в файле идёт приложение 1 про дорожные знаки, со своей главой 1.
RULES_START = "Глава 1. Общие положения"
RULES_END = "Приложение 1 к Правилам"


def is_watermark(line: str) -> bool:
    return "Әділет" in line


def is_page_number(line: str) -> bool:
    """Колонтитул вида '46 / 96'."""
    parts = line.split()
    return len(parts) == 3 and parts[1] == "/" and parts[0].isdigit() and parts[2].isdigit()


def clean(raw_lines: list[str]) -> list[str]:
    result = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        if is_watermark(line) or is_page_number(line):
            continue
        result.append(line)
    return result


def main() -> None:
    reader = PdfReader(PDF_PATH)
    if reader.is_encrypted:
        reader.decrypt("")

    raw_text = "\n".join(page.extract_text() for page in reader.pages)
    lines = clean(raw_text.splitlines())

    start = lines.index(RULES_START)
    end = lines.index(RULES_END)
    rules_lines = lines[start:end]

    OUT_PATH.write_text("\n".join(rules_lines), encoding="utf-8")

    print(f"страниц в PDF: {len(reader.pages)}")
    print(f"строк после очистки: {len(lines)}")
    print(f"строк в Правилах: {len(rules_lines)}")


main()