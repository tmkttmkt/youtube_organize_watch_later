import json
import MeCab
from collections import Counter
import unicodedata
import random

with open("watch_later.json", encoding="utf-8") as f:
    data = json.load(f)

mecab = MeCab.Tagger("-Ochasen")

title_words = Counter()
channel_words = Counter()

def is_skip(surface, feature):
    # 名詞以外はスキップ。さらに助詞・助動詞・動詞・連体詞・記号・非自立・接尾・接頭詞・数字・NGワード・絵文字もスキップ
    ng_words = {"|", "〜", "~", "+","ー"}
    if not feature.startswith("名詞"):
        return True
    if "非自立" in feature:
        return True
    if "接尾" in feature:
        return True
    if "接頭詞" in feature:
        return True
    if "記号" in feature:
        return True
    if surface and unicodedata.category(surface[0]).startswith("P"):
        return True
    # 全角・半角どちらも数字を除外
    if surface and all(unicodedata.category(c).startswith("N") for c in surface):
        return True
    # NGワードを除外
    if surface in ng_words:
        return True
    # 絵文字（サロゲートペアや記号カテゴリSoなど）を除外
    if surface and any(unicodedata.category(c) in {"So", "Cs"} or ord(c) > 0x1F000 for c in surface):
        return True
    return False

for item in data:
    title = item.get("title", "")
    channel = item.get("channel", "")
    # タイトル
    node = mecab.parseToNode(title)
    while node:
        surface = node.surface
        feature = node.feature
        if surface and not is_skip(surface, feature):
            title_words[surface] += 1
            # 1/10の確率で単語情報を表示
            if random.randint(1, 10) == 1:
                print(f"title: {surface} / {feature}")
        node = node.next
    # チャンネル
    node = mecab.parseToNode(channel)
    while node:
        surface = node.surface
        feature = node.feature
        if surface and not is_skip(surface, feature):
            channel_words[surface] += 1
            # 1/10の確率で単語情報を表示
            if random.randint(1, 10) == 1:
                print(f"channel: {surface} / {feature}")
        node = node.next

# 出現回数で降順ソート
title_words_sorted = dict(sorted(title_words.items(), key=lambda x: x[1], reverse=True))
channel_words_sorted = dict(sorted(channel_words.items(), key=lambda x: x[1], reverse=True))

result = {
    "title_words": title_words_sorted,
    "channel_words": channel_words_sorted
}

with open("word_list.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
