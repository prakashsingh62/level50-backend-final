from config import get_ws

def write_updates(rows):
    ws = get_ws()
    for row_idx, row_data in rows.items():
        ws.update(f"A{row_idx}:Z{row_idx}", [row_data])

def write_test_row():
    ws = get_ws()
    ws.append_row(
        ["TEST ENTRY FROM LEVEL-50 BACKEND"],
        value_input_option="RAW"
    )
    return True
