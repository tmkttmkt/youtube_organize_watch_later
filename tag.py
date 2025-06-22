import re
import json
from func import seconds_to_length, length_to_seconds, seconds_to_hms

# タイトルからタグを推定する簡易関数
def extract_tags(title):
    tags = []
    return tags
    keywords = {
        "ゆっくり": ["ゆっくり"],
        "ゲーム":["実況","ゲーム"],
        "VOICEROID":["VOICEROID","ヤンデレ"],
        "音楽": ["歌", "替え歌","feat."],
        "AI": ["AI", "人工知能", "ChatGPT", "GPT", "LLM"],
        "プログラミング": ["プログラミング", "Python", "コード", "開発", "エンジニア", "プログラム"],
    }
    for tag, words in keywords.items():
        if any(word in title for word in words):
            tags.append(tag)
    return tags

def detect_language(word):
    # ロシア語（キリル文字）
    if re.search(r'[А-Яа-яЁё]', word):
        return "russian"
    # 英語（半角英字のみ）
    elif re.fullmatch(r'[A-Za-z0-9_\-]+', word):
        return "english"
    # 日本語（ひらがな・カタカナ・漢字を含む）
    elif re.search(r'[ぁ-んァ-ン一-龥]', word):
        return "japanese"
    else:
        return "other"
def get_time_group(length_str):
    sec = length_to_seconds(length_str)
    if sec <= 60:
        return "ショート"
    elif sec <= 15*60:
        return "スモール"
    elif sec <= 40*60:
        return "ミドル"
    else:
        return "ロング"

with open("data/watch_later.json", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    item["tag"] = extract_tags(item.get("title", ""))
    item["time_group"] = get_time_group(item.get("length", ""))
    # detect_languageを使ってロシア語・英語のtagを作成（1単語でも含まれていればOK）
    title = item.get("title", "")
    words = re.findall(r'\w+|[ぁ-んァ-ン一-龥]+', title)
    has_ru = any(detect_language(w) == "russian" for w in words)
    has_en = any(detect_language(w) == "english" for w in words)
    if has_ru:
        item["tag"].append("ロシア語")
    if has_en:
        item["tag"].append("英語")

with open("data/tag_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
