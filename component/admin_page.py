import streamlit as st
import os

def show_admin_page():
    st.title("🔧 操作ページ（管理用）")
    # ページが開かれるたびにdeleted_videos.txtを読み込む
    deleted_list = []
    if os.path.exists("deleted_videos.txt"):
        with open("deleted_videos.txt", "r", encoding="utf-8") as f:
            line = f.read().strip()
            if line:
                items = [s.strip() for s in line.split(",") if s.strip()]
                for i in range(0, len(items), 3):
                    if i+2 < len(items):
                        channel = items[i]
                        title = items[i+1]
                        url = items[i+2]
                        deleted_list.append({"channel": channel, "title": title, "url": url})

    if not deleted_list:
        st.info("削除予定の動画はありません。")
    else:
        if st.button("この一覧の動画をすべて削除", key="delete_all"):
            with open("deleted_videos.txt", "w", encoding="utf-8") as f:
                f.write("")
            st.success("一覧の動画をすべてdeleted_videos.txtから削除しました。ページを再読み込みしてください。")
        st.markdown("#### 削除予定動画一覧")
        for item in deleted_list:
            st.markdown(f"- {item['title']}（{item['channel']}）")