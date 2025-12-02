def build_email(processed):
    body="Level-50 Daily Report\n\n"
    for r in processed:
        body+=f"RFQ: {r.get('RFQ NO')} | {r.get('CUSTOMER NAME')} | {r.get('VENDOR')} | Due: {r.get('DUE DATE')} | Status: {r.get('STATUS')}\n"
    return "Level-50 Report", body
