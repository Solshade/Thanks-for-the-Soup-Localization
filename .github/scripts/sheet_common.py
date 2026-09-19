import json
import os
from pathlib import Path

import gspread

LANGUAGES_DIR = Path(__file__).resolve().parents[2] / "languages"
KEY_HEADER = "key"


def open_worksheet():
    credentials = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    client = gspread.service_account_from_dict(credentials)
    spreadsheet = client.open_by_key(os.environ["SPREADSHEET_ID"].strip())
    sheet_name = os.environ.get("SHEET_NAME", "").strip()
    if sheet_name:
        return spreadsheet.worksheet(sheet_name)
    return spreadsheet.get_worksheet(0)


def read_grid(worksheet):
    rows = worksheet.get_all_values()
    width = max((len(row) for row in rows), default=0)
    grid = [row + [""] * (width - len(row)) for row in rows]
    if not grid:
        raise SystemExit("Spreadsheet is empty; expected a header row starting with 'key'.")
    header = [cell.strip() for cell in grid[0]]
    if not header or header[0].lower() != KEY_HEADER:
        raise SystemExit(f"First header cell must be '{KEY_HEADER}', found '{header[0] if header else ''}'.")
    return header, grid[1:]


def index_rows(rows):
    key_rows = {}
    for offset, row in enumerate(rows):
        key = row[0].strip() if row else ""
        if key and key not in key_rows:
            key_rows[key] = offset
    return key_rows


def load_language(lang):
    path = LANGUAGES_DIR / f"{lang}.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"{path.name} must contain a JSON object.")
    return data


def save_language(lang, data):
    path = LANGUAGES_DIR / f"{lang}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def local_languages():
    if not LANGUAGES_DIR.exists():
        return []
    return sorted(path.stem for path in LANGUAGES_DIR.glob("*.json"))


def column_letter(index):
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters
