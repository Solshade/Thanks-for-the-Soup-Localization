from sheet_common import index_rows, load_language, open_worksheet, read_grid, save_language


def main():
    worksheet = open_worksheet()
    header, rows = read_grid(worksheet)
    key_rows = index_rows(rows)

    seen = set()
    total_added = 0
    for column, lang in enumerate(header):
        if column == 0 or not lang or lang in seen:
            continue
        seen.add(lang)

        data = load_language(lang)
        added = 0
        for key, offset in key_rows.items():
            value = rows[offset][column]
            if value == "":
                continue
            existing = data.get(key)
            if existing is not None and existing != "":
                continue
            data[key] = value
            added += 1

        if added:
            save_language(lang, data)
            total_added += added
        print(f"{lang}: added {added} value(s)")

    print(f"Total values added: {total_added}")


if __name__ == "__main__":
    main()
