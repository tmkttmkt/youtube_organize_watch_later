import re
import json
from func import seconds_to_length, length_to_seconds, seconds_to_hms

keywords_for_channel = {
    "プログラミング・IT": [
        "プログラミング", "Python", "IT", "開発", "情報", "ボイロプログラミング", "プログラマ", "プログラマー", "プログラム", "AI", "Programming"
    ],
    "科学・数学": [
        "数学", "科学", "化学", "物理", "天文学", "定理", "サイエンス"
    ],
    "歴史・地理・国際": [
        "歴史", "世界", "地理", "博物館", "歴史", "SOVIET", "戦国", "文明"
    ],
    "音楽・音声・エンタメ": [
        "音楽", "実況", "ゲーム", "ボカロ", "DTM", "ラジオ", "動画", "エンジェル"
    ],
    "教育・学問・学習": [
        "大学", "学徒", "教養", "講座", "予備校", "学者", "教科書", "学区"
    ],
    "エンタメ・アニメ・ボカロ": [
        "VTuber", "VOICEROID", "ヤンデレボイロ", "ボイスロイド", "ボイロ"
    ],
    "社会・文化": [
        "社会", "哲学", "経済", "政治", "文化", "民俗", "国際", "就活", "転職"
    ],
    "鉄道・乗り物": [
        "鉄道", "列車", "交通", "車", "駅"
    ],
    "雑談・趣味": [
        "趣味", "日常", "雑学", "暇", "余談", "猫", "旅", "サブ", "カフェ"
    ]
}
keywords_for_title = {
  "プログラミング・IT": [
    "プログラミング", "Python", "入門", "IT", "開発", "使い方", "ソフトウェア", "API", "コード", "プログラム", "AI", "ディープラーニング"
  ],
  "科学・数学": [
    "物理", "理論", "化学", "科学", "数学", "演算", "線形", "代数", "統計", "量子力学"
  ],
  "音楽・音声・エンタメ": [
    "音楽", "作曲", "音", "音声", "初音", "ミク", "替え歌", "DTM", "UTAU", "VOICEVOX", "VOICEROID", "ボイスロイド"
  ],
  "ゲーム・実況": [
    "ゲーム", "実況", "RPG", "戦争", "戦車", "シミュレーション", "MOD", "攻略", "実況", "プレイ", "マインクラフト"
  ],
  "歴史・地理・国際": [
    "歴史", "Soviet", "ロシア", "世界", "日本", "ドイツ", "アメリカ", "ソ連", "中国", "共産", "国家", "戦争", "資源"
  ],
  "教育・学問・学習": [
    "学習", "初心者", "講座", "研究", "講義", "実装", "講演", "授業", "学者", "解説", "入門"
  ],
  "哲学・社会・文化": [
    "哲学", "主義", "社会", "宗教", "経済", "政治", "思想", "文化", "倫理", "生活"
  ],
  "鉄道・乗り物": [
    "鉄道", "列車", "新幹線", "交通", "運転", "車両", "飛行機", "夜行", "ブルートレイン", "航空"
  ],
  "エンタメ・アニメ・ボカロ": [
    "アニメ", "キャラ", "VTuber", "ボカロ", "葵", "琴葉", "茜", "漫画", "アレンジ", "映像", "声", "音源"
  ]
}

# タイトルからタグを推定する簡易関数
def extract_tags(title,channel):
    tags = []
    
    

    for tag, words in keywords_for_title.items():
        if any(word in title for word in words):
            tags.append(tag)
    for tag, words in keywords_for_channel.items():
        if any(word in channel for word in words):
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
    item["tag"] = extract_tags(item.get("title", ""), item.get("channel", ""))
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
