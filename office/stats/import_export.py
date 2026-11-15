#!/usr/bin/env python3
"""นำไฟล์ export จาก TikTok Studio เข้าสมุดสถิติ

ใช้:  python3 office/stats/import_export.py <ไฟล์ .zip หรือ .xlsx> [<ไฟล์อื่น> ...]

สิ่งที่ทำ:
1. เก็บไฟล์ต้นฉบับไว้ที่ office/stats/raw/tiktok-studio/ (ตั้งชื่อตามวันที่นำเข้า + ชนิด + ช่วงวัน)
2. อ่านทุกชีตในไฟล์ แล้วรวมเข้า office/stats/data/<ชนิด>.csv
   - ชีต Overview → data/daily-overview.csv (วันละ 1 แถว ถ้าวันซ้ำ ใช้ตัวเลขจากไฟล์ใหม่กว่า)
   - ชีตอื่น (เช่น Followers, Content) → data/<ชื่อชีต>.csv รวมแถวแบบไม่ซ้ำ
3. พิมพ์สรุปสั้น ๆ ให้หัวหน้าทีมนำไปส่ง stats-tracker ต่อ
"""
import csv
import datetime as dt
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import openpyxl

STATS = Path(__file__).resolve().parent
RAW = STATS / "raw" / "tiktok-studio"
DATA = STATS / "data"

OVERVIEW_COLS = {
    "Date": "date",
    "Video Views": "video_views",
    "Profile Views": "profile_views",
    "Likes": "likes",
    "Comments": "comments",
    "Shares": "shares",
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "sheet"


def to_num(v):
    if v is None:
        return ""
    s = str(v).replace(",", "").strip()
    try:
        f = float(s)
        return str(int(f)) if f.is_integer() else str(f)
    except ValueError:
        return s


def parse_day(v, year):
    """'November 7' → 2026-11-07 (ปีเอามาจากชื่อไฟล์ export)"""
    if isinstance(v, (dt.date, dt.datetime)):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    for fmt in ("%B %d %Y", "%b %d %Y", "%Y-%m-%d"):
        try:
            text = s if fmt == "%Y-%m-%d" else f"{s} {year}"
            return dt.datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return s


def year_from_name(name):
    m = re.search(r"(20\d\d)-\d\d-\d\d", name)
    return int(m.group(1)) if m else dt.date.today().year


def read_csv(path):
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_csv(path, cols, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def merge_overview(rows, source):
    path = DATA / "daily-overview.csv"
    cols = list(OVERVIEW_COLS.values()) + ["source"]
    _, old = read_csv(path)
    by_date = {r["date"]: r for r in old}
    for r in rows:
        r["source"] = source
        by_date[r["date"]] = r  # ไฟล์ใหม่กว่าทับของเดิม (TikTok อัปเดตย้อนหลังได้)
    merged = [by_date[d] for d in sorted(by_date)]
    write_csv(path, cols, merged)
    return path, len(merged)


def merge_generic(name, header, rows, source):
    path = DATA / f"{slug(name)}.csv"
    old_cols, old = read_csv(path)
    cols = old_cols or (header + ["source"])
    for h in header + ["source"]:
        if h not in cols:
            cols.append(h)
    seen = {tuple(r.get(c, "") for c in header) for r in old}
    for r in rows:
        key = tuple(r.get(c, "") for c in header)
        if key not in seen:
            r["source"] = source
            old.append(r)
            seen.add(key)
    write_csv(path, cols, old)
    return path, len(old)


def import_xlsx(xlsx, year, source):
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    out = []
    for ws in wb:
        values = [r for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]
        if not values:
            continue
        header = [str(c).strip() if c is not None else f"col{i}" for i, c in enumerate(values[0])]
        body = values[1:]
        if ws.title.lower() == "overview" and set(header) >= set(OVERVIEW_COLS):
            rows = []
            for v in body:
                d = dict(zip(header, v))
                rows.append({OVERVIEW_COLS[k]: (parse_day(d[k], year) if k == "Date" else to_num(d[k]))
                             for k in OVERVIEW_COLS})
            path, n = merge_overview(rows, source)
            out.append((ws.title, len(rows), path, n, rows))
        else:
            rows = [{h: ("" if c is None else str(c)) for h, c in zip(header, v)} for v in body]
            path, n = merge_generic(ws.title, header, rows, source)
            out.append((ws.title, len(rows), path, n, None))
    return out


def archive(src, kind, rows):
    today = dt.date.today().isoformat()
    span = ""
    dates = [r["date"] for r in rows or [] if re.match(r"\d{4}-\d\d-\d\d", r["date"])]
    if dates:
        span = f"_{min(dates)}_to_{max(dates)}"
    dest = RAW / f"{today}_{slug(kind)}{span}{src.suffix.lower()}"
    if not dest.exists() and src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return dest


def main(paths):
    RAW.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    for p in map(Path, paths):
        year = year_from_name(p.name)
        kind = re.split(r"[_ .]", re.sub(r"^[0-9a-f]{8}-", "", p.name))[0] or "export"
        with tempfile.TemporaryDirectory() as tmp:
            if p.suffix.lower() == ".zip":
                with zipfile.ZipFile(p) as z:
                    names = [n for n in z.namelist() if n.lower().endswith((".xlsx", ".csv"))]
                    z.extractall(tmp, members=names)
                files = [Path(tmp) / n for n in names]
            else:
                files = [p]
            results = []
            for f in files:
                if f.suffix.lower() == ".xlsx":
                    results += import_xlsx(f, year, re.sub(r"^[0-9a-f]{8}-", "", p.name))
        overview_rows = next((r[4] for r in results if r[4]), None)
        dest = archive(p, kind, overview_rows)
        print(f"📦 เก็บต้นฉบับ: {dest.relative_to(STATS.parent.parent)}")
        for sheet, n_new, path, n_total, rows in results:
            print(f"  • ชีต {sheet}: {n_new} แถว → {path.relative_to(STATS.parent.parent)} (รวม {n_total} แถว)")
            if rows:
                tot = {k: sum(int(r[k] or 0) for r in rows) for k in list(OVERVIEW_COLS.values())[1:]}
                print("    รวมช่วงนี้: " + " · ".join(f"{k}={v:,}" for k, v in tot.items()))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
