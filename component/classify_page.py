import streamlit as st
import json
import os
categories = [
    ("その他", "その他"),
    ("技術解説", "頭がさえてる時に見たい"),
    ("エンタメ的解説", "課題などしながら見たい"),
    ("音楽・替え歌", "疲れてて情報を入れたくないときに見たい"),
    ("実況", "ゲームしながら見たい"),
    ("茶番", "ゲームしながら見たい"),
    ("ネタ動画・MAD", "笑いたいとき"),
    ("ニュース", "短い時間で見たい"),
]
def show_classify_page():
    st.title("動画の分類（人力）")
    data_path = os.path.join("data", "tag_data.json")
    if not os.path.exists(data_path):
        st.error("tag_data.jsonが見つかりません")
        return
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    import csv
    csv_path = os.path.join("data", "manual_classify.csv")
    # 既存分類済みvideo_idをCSVから取得
    classified = {}
    classified_ids = set()
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row.get("video_id")
                if vid:
                    classified_ids.add(vid)
                    classified[vid] = {"category": row.get("category", ""), "memo": row.get("memo", "")}
    # 未分類動画のみ表示
    unclassified = [d for d in data if d.get("video_id") and d["video_id"] not in classified_ids]
    if not unclassified:
        st.success("すべての動画が分類済みです！")
        return
    # 流れ作業用：2件ずつ表示、カテゴリはボタンで選択
    N = 10
    batch = unclassified[:N]
    st.write(f"未分類動画 {len(unclassified)} 件中 {N} 件を表示中")
    for idx, video in enumerate(batch):
        st.markdown(f"---\n#### {idx+1}. {video.get('title', 'タイトルなし')}")
        cols = st.columns([2, 3])
        with cols[0]:
            st.write(f'チャンネル: {video.get("channel", "-")}, 長さ: {video.get("length", "-")}, 視聴数: {video.get("views", "-")}, URL: {video.get("url", "-" )}')
            st.write(f'タグ: {", ".join(video.get("tag", []))}')
        with cols[1]:
            url = video.get("url", "")
            if url and "youtube.com/watch?v=" in url:
                video_id = url.split("v=")[-1].split("&")[0]
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                st.markdown(f"""
                    <iframe width='320' height='180' src='{embed_url}' frameborder='0' allowfullscreen></iframe>
                """, unsafe_allow_html=True)
            else:
                st.info("動画URLがありません")
        # カテゴリボタンを動画の下に表示
        # 用途一覧をボタンの上に横並びで表示
        usage_html = "<div style='display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;'>"
        for cat, comment in categories:
            usage_html += f"<div style='min-width:120px;padding:4px 8px;background:#f7f7f7;border-radius:6px;text-align:center;font-size:13px;'>"
            usage_html += f"<b>{cat}</b><br><span style='color:#666'>{comment}</span></div>"
        usage_html += "</div>"
        st.markdown(usage_html, unsafe_allow_html=True)
        st.write("カテゴリを選択:")
        btn_cols = st.columns(len(categories))
        for i, (cat, _) in enumerate(categories):
            btn_key = f"btn_{cat}_{video['video_id']}"
            if btn_cols[i].button(cat, key=btn_key):
                classified[video["video_id"]] = {"category": cat}
                rows = []
                for vid, info in classified.items():
                    title = next((d.get("title", "") for d in data if d.get("video_id") == vid), "")
                    rows.append([vid, title, info.get("category", "")])
                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["video_id", "title", "category"])
                    writer.writerows(rows)
                st.success(f"保存しました！（{video.get('title', '')} → {cat}）")
                st.rerun()
