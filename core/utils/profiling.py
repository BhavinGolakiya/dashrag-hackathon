# utils/profiling.py
from collections import Counter
from datetime import date, datetime

def is_number(x):
    try: float(x); return True
    except: return False

def is_dt(x):
    return isinstance(x, (datetime, date))

def profile_records(records, max_sample=200):
    if not records:
        return {"row_count": 0, "columns": [], "samples": []}

    samples = records[:max_sample]
    cols = list(samples[0].keys())
    col_profiles = []
    for c in cols:
        vals = [r[c] for r in samples if r.get(c) is not None]
        uniq = len(set(vals))
        num = sum(1 for v in vals if is_number(v))
        dt  = sum(1 for v in vals if is_dt(v))
        prof = {
            "name": c,
            "sample_values": list(Counter(vals).most_common(5)),
            "unique_count": uniq,
            "is_numeric_ratio": (num / max(1, len(vals))),
            "is_datetime_ratio": (dt / max(1, len(vals))),
        }
        col_profiles.append(prof)

    return {
        "row_count": len(records),
        "columns": col_profiles,
        "samples": samples
    }
