import streamlit as st
import pandas as pd
from func import seconds_to_length, length_to_seconds, seconds_to_hms

def show_list_page(df):
    all_tags = sorted({tag for tags in df["tag"] for tag in tags})
    selected_tags = st.sidebar.multiselect("タグで絞り込み", all_tags)
    time_groups = sorted(df["time_group"].dropna().unique())
    selected_time_groups = st.sidebar.multiselect("タイムグループで絞り込み", time_groups)

    show_df = df
    if selected_tags:
        show_df = show_df[show_df["tag"].apply(lambda tags: any(tag in tags for tag in selected_tags))]
    if selected_time_groups:
        show_df = show_df[show_df["time_group"].isin(selected_time_groups)]

    sort_by = st.selectbox("並び替え", ["views", "published", "length"])
    ascending = st.checkbox("昇順", value=False if sort_by == "views" else True)
    show_df = show_df.sort_values(by=sort_by, ascending=ascending)

    st.title("🎬 タグ付き動画データベース（一覧）")
    for idx, row in show_df.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(f"- 📺 チャンネル: {row['channel']}")
        st.markdown(f"- ⏱ 時間: {row['length']}　📅 公開: {row['published']}　👁️ 視聴: {row['views']:,}回")
        st.markdown(f"- 🏷️ タグ: {row['tag_str']}")
        # 動画URLリンク（新しいタブで開く）
        st.markdown(f"- 🔗 [YouTubeで開く]({row['url']})", unsafe_allow_html=True)
        # 動画削除ボタン（keyを一意にする）
        if st.button(f"この動画を削除登録（{row['title']}）", key=f"delete_{row['title']}_{row['channel']}_{idx}"):
            with open("deleted_videos.txt", "a", encoding="utf-8") as del_f:
                del_f.write("\n"+row["channel"]+" , "+row["title"]+" , "+row["url"])
            st.success(f"『{row['title']}』({row['channel']}) をdeleted_videos.txtに記録し、データも削除しました。ページを再読み込みしてください。")
        st.markdown("---")
