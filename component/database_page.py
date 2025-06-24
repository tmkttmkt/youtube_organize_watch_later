import streamlit as st
import pandas as pd
from func import seconds_to_length, length_to_seconds, seconds_to_hms

def show_database_page(df):
    st.title("📋 データベース（テーブル表示）")
    time_groups = sorted(df["time_group"].dropna().unique())
    selected_time_groups = st.sidebar.multiselect("タイムグループで絞り込み（データベース）", time_groups, key="db_time_group")

    filtered_df = df
    if selected_time_groups:
        filtered_df = filtered_df[filtered_df["time_group"].isin(selected_time_groups)]

    group_by = st.selectbox("グループ化", ["なし", "channel", "tag"], key="db_group")
    sort_by = st.selectbox("テーブル並び替え", ["views", "published", "length"], key="db_sort")
    ascending = st.checkbox("昇順", value=False if sort_by == "views" else True, key="db_asc")
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
        st.dataframe(sorted_df.drop(columns=["time_group", "length_sec", "url","video_id"]), use_container_width=True)
    elif group_by == "channel":
        channel_counts = sorted_df["channel"].value_counts()
        for channel in channel_counts.index:
            group = sorted_df[sorted_df["channel"] == channel]
            st.markdown(f"## 📺 {channel}")
            group_summary(group)
            st.dataframe(group.drop(columns=["time_group", "length_sec", "url"]), use_container_width=True)
    elif group_by == "tag":
        exploded = sorted_df.explode("tag")
        tag_counts = exploded["tag"].value_counts()
        for tag in tag_counts.index:
            if tag == "" or pd.isna(tag):
                continue
            group = exploded[exploded["tag"] == tag]
            st.markdown(f"## 🏷️ {tag}")
            group_summary(group)
            st.dataframe(group.drop(columns=["time_group", "length_sec", "url"]), use_container_width=True)
