import json
import csv
import os
from datetime import datetime

with open("watch_later.json", encoding="utf-8") as f:
    data = json.load(f)

today = datetime.now().strftime("%Y-%m-%d")
os.makedirs("time", exist_ok=True)
csv_path = os.path.join("time", f"{today}.csv")

def seconds_to_length(seconds):
    # 秒数を00:02:43のような形式に変換
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"
    else:
        return f"{m:02}:{s:02}"

def length_to_seconds(length_str):
    # "00:08:56" → 536, "2 分 38 秒" → 158, "1 時間 2 分 3 秒" → 3723
    if not length_str:
        return 0
    import re
    jp = re.match(r"(?:(\d+)\s*時間)?\s*(?:(\d+)\s*分)?\s*(?:(\d+)\s*秒)?", length_str)
    if jp and (jp.group(1) or jp.group(2) or jp.group(3)):
        h = int(jp.group(1)) if jp.group(1) else 0
        m = int(jp.group(2)) if jp.group(2) else 0
        s = int(jp.group(3)) if jp.group(3) else 0
        return h*3600 + m*60 + s
    # 通常のコロン区切り
    parts = [int(p) for p in length_str.split(":") if p.isdigit()]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    elif len(parts) == 2:
        return parts[0]*60 + parts[1]
    else:
        return 0

with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    for item in data:
        insert_date = item.get("insert", "")
        try:
            d0 = datetime.strptime(insert_date, "%Y-%m-%d")
            d1 = datetime.strptime(today, "%Y-%m-%d")
            diff = (d1 - d0).days
        except Exception:
            diff = ""
        # lengthを秒数に変換してからlength形式に戻す
        length_sec = length_to_seconds(item.get("length", ""))
        writer.writerow([diff, seconds_to_length(length_sec)])