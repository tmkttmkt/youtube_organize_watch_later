import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_pie_chart_page(df):
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
