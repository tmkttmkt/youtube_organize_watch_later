import streamlit as st
import json
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import glob




matplotlib.rcParams['font.family'] = 'Meiryo'

st.set_page_config(layout="wide")

# データをファイルから読み込む
with open("tag_data.json", encoding="utf-8") as f:
    data = json.load(f)

def parse_time_to_seconds(time_str):
    # "2:01:50" → 7310, "1:13" → 73
    parts = [int(p) for p in time_str.strip().split(":")]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    elif len(parts) == 2:
        return parts[0]*60 + parts[1]
    elif len(parts) == 1:
        return int(parts[0])
    else:
        return 0

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
                sec = parse_time_to_seconds(time_str)
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

def length_to_seconds(length_str):
    # "00:08:56" → 536
    if not length_str:
        return 0
    parts = [int(p) for p in length_str.split(":")]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    elif len(parts) == 2:
        return parts[0]*60 + parts[1]
    else:
        return 0

def seconds_to_hms(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02}:{m:02}:{s:02}"

df = pd.DataFrame(data)
df["tag_str"] = df["tag"].apply(lambda tags: ", ".join(tags) if tags else "なし")
df["length_sec"] = df["length"].apply(length_to_seconds)

# サイドバーでページ選択
page = st.sidebar.selectbox("ページを選択", [ "日別スコア集計","一覧", "データベース", "グラフ（円）", "グラフ（棒）"])

if page == "一覧":
    # タグフィルタ
    all_tags = sorted({tag for tags in df["tag"] for tag in tags})
    selected_tags = st.sidebar.multiselect("タグで絞り込み", all_tags)
    # time_groupフィルタ
    time_groups = sorted(df["time_group"].dropna().unique())
    selected_time_groups = st.sidebar.multiselect("タイムグループで絞り込み", time_groups)

    show_df = df
    if selected_tags:
        show_df = show_df[show_df["tag"].apply(lambda tags: any(tag in tags for tag in selected_tags))]
    if selected_time_groups:
        show_df = show_df[show_df["time_group"].isin(selected_time_groups)]

    # 並び替えオプション
    sort_by = st.selectbox("並び替え", ["views", "published", "length"])
    ascending = st.checkbox("昇順", value=False if sort_by == "views" else True)
    show_df = show_df.sort_values(by=sort_by, ascending=ascending)

    st.title("🎬 タグ付き動画データベース（一覧）")
    for _, row in show_df.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(f"- 📺 チャンネル: {row['channel']}")
        st.markdown(f"- ⏱ 時間: {row['length']}　📅 公開: {row['published']}　👁️ 視聴: {row['views']:,}回")
        st.markdown(f"- 🏷️ タグ: {row['tag_str']}")
        st.markdown("---")

elif page == "データベース":
    st.title("📋 データベース（テーブル表示）")
    # time_groupフィルタ
    time_groups = sorted(df["time_group"].dropna().unique())
    selected_time_groups = st.sidebar.multiselect("タイムグループで絞り込み（データベース）", time_groups, key="db_time_group")

    filtered_df = df
    if selected_time_groups:
        filtered_df = filtered_df[filtered_df["time_group"].isin(selected_time_groups)]

    # グルーピング選択
    group_by = st.selectbox("グループ化", ["なし", "channel", "tag"], key="db_group")
    sort_by = st.selectbox("テーブル並び替え", ["views", "published", "length"], key="db_sort")
    ascending = st.checkbox("昇順", value=False if sort_by == "views" else True, key="db_asc")
    print(f"Sorting by: {sort_by}, Ascending: {ascending}")

    sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    def group_summary(group):
        count = len(group)
        avg_views = int(group["views"].mean()) if count > 0 else 0
        avg_length_sec = int(group["length_sec"].mean()) if count > 0 else 0
        avg_length = seconds_to_hms(avg_length_sec)
        avg_published = group["published"].mode()[0] if count > 0 and not group["published"].mode().empty else ""
        st.markdown(
            f"- 件数: {count}　- 平均視聴: {avg_views:,}回　- 平均長さ: {avg_length}　- 代表公開日: {avg_published}"
        )

    if group_by == "なし":
        group_summary(sorted_df)
        st.dataframe(sorted_df.drop(columns=["time_group", "length_sec"]), use_container_width=True)
    elif group_by == "channel":
        # 件数が多い順にchannelを並べる
        channel_counts = sorted_df["channel"].value_counts()
        for channel in channel_counts.index:
            group = sorted_df[sorted_df["channel"] == channel]
            st.markdown(f"## 📺 {channel}")
            group_summary(group)
            st.dataframe(group.drop(columns=["time_group", "length_sec"]), use_container_width=True)
    elif group_by == "tag":
        # タグごとにグループ化（explodeしてからグループ化）、件数が多い順
        exploded = sorted_df.explode("tag")
        tag_counts = exploded["tag"].value_counts()
        for tag in tag_counts.index:
            if tag == "" or pd.isna(tag):
                continue
            group = exploded[exploded["tag"] == tag]
            st.markdown(f"## 🏷️ {tag}")
            group_summary(group)
            st.dataframe(group.drop(columns=["time_group", "length_sec"]), use_container_width=True)

elif page == "グラフ（円）":
    st.title("🟠 タグ・再生数グラフ（円グラフ）")
    tag_count = df.explode("tag")["tag"].value_counts()
    st.subheader("タグごとの動画数")
    fig1, ax1 = plt.subplots()
    ax1.pie(tag_count, labels=tag_count.index, autopct="%.1f%%", startangle=90, counterclock=False)
    ax1.axis("equal")
    st.pyplot(fig1)

    tag_views = df.explode("tag").groupby("tag")["views"].sum().sort_values(ascending=False)
    st.subheader("タグごとの合計再生数")
    fig2, ax2 = plt.subplots()
    ax2.pie(tag_views, labels=tag_views.index, autopct="%.1f%%", startangle=90, counterclock=False)
    ax2.axis("equal")
    st.pyplot(fig2)

    # --- time_groupごとのグラフ ---
    time_count = df["time_group"].value_counts()
    st.subheader("タイムグループごとの動画数")
    fig3, ax3 = plt.subplots()
    ax3.pie(time_count, labels=time_count.index, autopct="%.1f%%", startangle=90, counterclock=False)
    ax3.axis("equal")
    st.pyplot(fig3)

    time_views = df.groupby("time_group")["views"].sum().sort_values(ascending=False)
    st.subheader("タイムグループごとの合計再生数")
    fig4, ax4 = plt.subplots()
    ax4.pie(time_views, labels=time_views.index, autopct="%.1f%%", startangle=90, counterclock=False)
    ax4.axis("equal")
    st.pyplot(fig4)

elif page == "グラフ（棒）":
    st.title("📊 タグ・再生数グラフ（棒グラフ）")
    tag_count = df.explode("tag")["tag"].value_counts()
    st.subheader("タグごとの動画数")
    st.bar_chart(tag_count)

    tag_views = df.explode("tag").groupby("tag")["views"].sum().sort_values(ascending=False)
    st.subheader("タグごとの合計再生数")
    st.bar_chart(tag_views)

    # --- time_groupごとのグラフ ---
    time_count = df["time_group"].value_counts()
    st.subheader("タイムグループごとの動画数")
    st.bar_chart(time_count)

    time_views = df.groupby("time_group")["views"].sum().sort_values(ascending=False)
    st.subheader("タイムグループごとの合計再生数")
    st.bar_chart(time_views)

elif page == "日別スコア集計":
    st.title("📅 日別スコア集計（複数CSV集計）")
    score_df = load_score_csvs()
    if score_df.empty:
        st.warning("time/配下に日付CSVがありません。")
    else:
        st.dataframe(score_df, use_container_width=True)
        # 日付順に並べる
        score_df = score_df.sort_values("date")
        # 各日ごとに延べ日数（1）、延べ秒数（score）、スコア（日数+秒数）を計算
        st.subheader("延べ日数・延べ秒数・スコア（x軸: 日付, 折れ線グラフ）")
        fig, ax1 = plt.subplots()
        color1 = "tab:blue"
        color2 = "tab:orange"
        color3 = "tab:green"
        ax1.set_xlabel("日付")
        ax1.set_ylabel("値")
        l1, = ax1.plot(score_df["date"], score_df["total_data"], marker="o", label="延べ日数", color=color1)
        l2, = ax1.plot(score_df["date"], score_df["total_sec"], marker="o", label="延べ秒数", color=color2)
        l3, = ax1.plot(score_df["date"], score_df["total_score"], marker="o", label="スコア", color=color3)
        ax1.tick_params(axis='x', rotation=45)
        ax1.ticklabel_format(style="plain", axis="y")  # ← 追加: y軸の指数表記を無効化

        # 凡例をまとめて表示
        lines = [l1, l2, l3]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc="best")

        st.pyplot(fig)
