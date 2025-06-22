import streamlit as st
import pandas as pd

def show_bar_chart_page(df):
    st.title("📊 タグ・再生数グラフ（棒グラフ）")
    tag_count = df.explode("tag")["tag"].value_counts()
    st.subheader("タグごとの動画数")
    st.bar_chart(tag_count)

    tag_views = df.explode("tag").groupby("tag")["views"].sum().sort_values(ascending=False)
    st.subheader("タグごとの合計再生数")
    st.bar_chart(tag_views)

    time_count = df["time_group"].value_counts()
    st.subheader("タイムグループごとの動画数")
    st.bar_chart(time_count)

    time_views = df.groupby("time_group")["views"].sum().sort_values(ascending=False)
    st.subheader("タイムグループごとの合計再生数")
    st.bar_chart(time_views)
