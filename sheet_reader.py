def read_rows():
    ws = get_ws()

    # Pull full sheet range (A to AT)
    values = ws.get("A:AT")

    if not values:
        return []

    header = values[0]
    data_rows = values[1:]

    data = []
    for i, row in enumerate(data_rows, start=2):
        record = {}
        for col_index, col_value in enumerate(row):
            key = header[col_index] if col_index < len(header) else f"COL_{col_index}"
            record[key] = col_value

        record["_ROW"] = i
        data.append(record)

    return data
