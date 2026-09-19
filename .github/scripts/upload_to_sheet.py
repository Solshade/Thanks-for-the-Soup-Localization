from sheet_common import (
    column_letter,
    index_rows,
    load_language,
    local_languages,
    open_worksheet,
    read_grid,
)


def to_cell(lang, key, value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        raise SystemExit(f"{lang}.json key '{key}' is nested; only flat string values are supported.")
    return str(value)


def main():
    worksheet = open_worksheet()
    header, rows = read_grid(worksheet)
    key_rows = index_rows(rows)

    languages = local_languages()
    languages.sort(key=lambda lang: (lang != "en", lang))

    columns = {name: index for index, name in reversed(list(enumerate(header))) if index > 0 and name}
    new_columns = [lang for lang in languages if lang not in columns]
    for lang in new_columns:
        columns[lang] = len(header)
        header.append(lang)

    updates = {}
    for lang in new_columns:
        updates[(0, columns[lang])] = lang

    new_keys = []
    changed_cells = 0
    for lang in languages:
        column = columns[lang]
        for key, raw_value in load_language(lang).items():
            key = key.strip()
            value = to_cell(lang, key, raw_value)
            if not key:
                continue
            if key not in key_rows:
                key_rows[key] = len(rows)
                rows.append([key] + [""] * (len(header) - 1))
                new_keys.append(key)
                updates[(key_rows[key] + 1, 0)] = key
            row = rows[key_rows[key]]
            if len(row) < len(header):
                row.extend([""] * (len(header) - len(row)))
            if value == "" or row[column] == value:
                continue
            row[column] = value
            updates[(key_rows[key] + 1, column)] = value
            changed_cells += 1

    if not updates:
        print("Spreadsheet already up to date.")
        return

    required_rows = len(rows) + 1
    if worksheet.row_count < required_rows:
        worksheet.add_rows(required_rows - worksheet.row_count)
    if worksheet.col_count < len(header):
        worksheet.add_cols(len(header) - worksheet.col_count)

    batch = [
        {"range": f"{column_letter(column)}{row + 1}", "values": [[value]]}
        for (row, column), value in sorted(updates.items())
    ]
    for start in range(0, len(batch), 500):
        worksheet.batch_update(batch[start:start + 500], value_input_option="RAW")

    print(f"Added columns: {', '.join(new_columns) or 'none'}")
    print(f"Added keys: {len(new_keys)}")
    print(f"Updated cells: {changed_cells}")


if __name__ == "__main__":
    main()
