import json
import csv
import os
from datetime import datetime
from func import seconds_to_length, length_to_seconds, seconds_to_hms

with open("data/watch_later.json", encoding="utf-8") as f:
    data = json.load(f)

today = datetime.now().strftime("%Y-%m-%d")
os.makedirs("time", exist_ok=True)
csv_path = os.path.join("time", f"{today}.csv")

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