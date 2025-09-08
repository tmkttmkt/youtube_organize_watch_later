import streamlit as st
import json
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import glob
from func import seconds_to_length, length_to_seconds, seconds_to_hms
from component.list_page import show_list_page
from component.database_page import show_database_page
from component.pie_chart_page import show_pie_chart_page
from component.bar_chart_page import show_bar_chart_page
from component.score_page import show_score_page
from component.admin_page import show_admin_page

from component.search_page import show_search_page
from component.classify_page import show_classify_page




matplotlib.rcParams['font.family'] = 'Meiryo'

st.set_page_config(layout="wide", page_title="YouTube後で見る管理", page_icon="🎬")

# データをファイルから読み込む
with open("data/tag_data.json", encoding="utf-8") as f:
    data = json.load(f)


def load_score_csvs():
    import glob
    import os
    csv_files = glob.glob(os.path.join("time", "*.csv"))
    date_score = {}
    for path in csv_files:
        basename = os.path.basename(path)
        date = os.path.splitext(basename)[0]
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
            total_sec = 0
            total_data = 0
            total_score = 0
            for line in lines:
                cols = line.strip().split(",")
                if len(cols) < 2:
                    continue
                time_str = cols[1]
                sec = length_to_seconds(time_str)
                total_data += int(cols[0])
                total_sec += sec
                total_score += sec * int(cols[0])
            # 型を変更: 各日付ごとに dict で格納
            date_score[date] = {
                "total_data": total_data,
                "total_sec": total_sec,
                "total_score": total_score
            }
        except Exception as e:
            st.warning(f"{basename} 読み込みエラー: {e}")
            continue
    if not date_score:
        return pd.DataFrame(columns=["date", "total_data", "total_sec", "total_score"])
    # DataFrame化
    df = pd.DataFrame([
        {"date": date, **vals} for date, vals in date_score.items()
    ])
    df = df.sort_values("date")
    return df

df = pd.DataFrame(data)
df["tag_str"] = df["tag"].apply(lambda tags: ", ".join(tags) if tags else "なし")
df["length_sec"] = df["length"].apply(length_to_seconds)

# サイドバーでページ選択
page = st.sidebar.selectbox("ページを選択", ["日別スコア集計", "一覧", "データベース", "グラフ（円）", "グラフ（棒）", "検索", "操作ページ", "動画分類"])
st.sidebar.title("メニュー")

if page == "一覧":
    show_list_page(df)
elif page == "データベース":
    show_database_page(df)
elif page == "グラフ（円）":
    show_pie_chart_page(df)
elif page == "グラフ（棒）":
    show_bar_chart_page(df)
elif page == "日別スコア集計":
    show_score_page(load_score_csvs)
elif page == "検索":
    show_search_page(df)
elif page == "操作ページ":
    show_admin_page(df)
elif page == "動画分類":
    show_classify_page()
