import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from func import seconds_to_hms

def show_score_page(load_score_csvs):
    st.title("📅 日別スコア集計（複数CSV集計）")
    score_df = load_score_csvs()
    if score_df.empty:
        st.warning("time/配下に日付CSVがありません。")
    else:
        st.dataframe(score_df, use_container_width=True)
        score_df = score_df.sort_values("date")
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
        ax1.ticklabel_format(style="plain", axis="y")
        lines = [l1, l2, l3]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc="best")
        st.pyplot(fig)
