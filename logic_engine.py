from classify import classify_row

def run_engine(rows):
    out = []
    for r in rows:
        try:
            status = classify_row(r)
        except Exception as e:
            r["STATUS"] = "ERROR"
            out.append(r)
            continue

        if not status or not isinstance(status, str):
            # Protects templates + writer
            r["STATUS"] = "INVALID"
            out.append(r)
            continue

        if status == "SKIP":
            continue

        r["STATUS"] = status
        out.append(r)

    return out
