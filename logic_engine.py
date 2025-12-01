
from classify import classify_row

def run_engine(rows):
    out=[]
    for r in rows:
        status=classify_row(r)
        if status=="SKIP": continue
        r["STATUS"]=status
        out.append(r)
    return out
