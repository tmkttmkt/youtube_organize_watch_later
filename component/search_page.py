import streamlit as st
import pandas as pd
import re

def show_search_page(df):
    st.title("🔍 動画検索ページ")
    col1, col2, col3 = st.columns(3)
    with col1:
        title_query = st.text_input("タイトルで検索（AND・スペース区切り可）", key="search_title")
    with col2:
        channel_query = st.text_input("チャンネルで検索（AND・スペース区切り可）", key="search_channel")
    with col3:
        tag_query = st.text_input("タグで検索（AND・スペース区切り可）", key="search_tag")

    mask = pd.Series([True] * len(df))
    # タイトル検索
    if title_query:
        title_keywords = [q for q in re.split(r"[\s\u3000]+", title_query.strip()) if q]
        for kw in title_keywords:
            mask = mask & df["title"].str.contains(kw, case=False, na=False)
    # チャンネル検索
    if channel_query:
        channel_keywords = [q for q in re.split(r"[\s\u3000]+", channel_query.strip()) if q]
        for kw in channel_keywords:
            mask = mask & df["channel"].str.contains(kw, case=False, na=False)
    # タグ検索
    if tag_query:
        tag_keywords = [q for q in re.split(r"[\s\u3000]+", tag_query.strip()) if q]
        for kw in tag_keywords:
            mask = mask & df["tag_str"].str.contains(kw, case=False, na=False)

    result = df[mask]
    st.write(f"検索結果: {len(result)} 件")
    if len(result) == 0:
        st.warning("該当する動画がありません。")
    else:
        for idx, row in result.iterrows():
            st.markdown(f"### {row['title']}")
            st.markdown(f"- 📺 チャンネル: {row['channel']}")
            st.markdown(f"- 🏷️ タグ: {row['tag_str']}")
            st.markdown(f"- 🔗 [YouTubeで開く]({row['url']})", unsafe_allow_html=True)
            # 削除登録ボタン
            if st.button(f"この動画を削除登録（{row['title']}）", key=f"search_delete_{row['title']}_{row['channel']}_{idx}"):
                with open("deleted_videos.txt", "a", encoding="utf-8") as del_f:
                    del_f.write("\n"+row["channel"]+" , "+row["title"]+" , "+row["url"])
                st.success(f"『{row['title']}』({row['channel']}) をdeleted_videos.txtに記録しました。ページを再読み込みしてください。")
            st.markdown("---")
