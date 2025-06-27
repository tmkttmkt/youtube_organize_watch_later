import streamlit as st
import os
import subprocess
import sys

def show_admin_page(df):
    st.title("🔧 操作ページ（管理用）")
    
    # dfからタグとチャンネルのリストを作成
    try:
        # チャンネル名の一意リストを作成
        channels = sorted(df["channel"].dropna().unique().tolist())
        
        # タグの一意リストを作成
        all_tags = []
        for tags in df["tag"].dropna():
            if isinstance(tags, list):
                all_tags.extend(tags)
        tags = sorted(list(set(all_tags)))
        
    except Exception as e:
        st.error(f"データの処理に失敗しました: {str(e)}")
        channels = []
        tags = []
    
    # ソートボタンと切り出しボタンの追加
    st.markdown("### 🔧 YouTube後で見る操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 ソート設定")
        sort_option = st.selectbox(
            "ソート方法を選択",
            ["日付順（古い順）", "日付順（新しい順）", "動画長順", "視聴回数順"],
            key="sort_option"
        )
        
        if st.button("📊 ソート実行", key="sort_button", help="YouTube後で見るリストをソートします"):
            try:
                st.info(f"ソート処理を開始しています...（{sort_option}）")
                # ソートオプションを引数として渡す
                sort_arg = {
                    "日付順（古い順）": "date_asc",
                    "日付順（新しい順）": "date_desc", 
                    "動画長順": "duration",
                    "視聴回数順": "views"
                }[sort_option]
                
                result = subprocess.run([sys.executable, "selenium/sort_data.py", sort_arg], 
                                      cwd=os.getcwd(), 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    st.success(f"ソート処理が完了しました！（{sort_option}）")
                else:
                    st.error(f"ソート処理でエラーが発生しました: {result.stderr}")
            except Exception as e:
                st.error(f"ソート処理の実行中にエラーが発生しました: {str(e)}")
    
    with col2:
        st.markdown("#### ✂️ 切り出し設定")
        cutout_option = st.selectbox(
            "切り出し条件を選択",
            ["動画長", "特定チャンネル", "特定タグ"],
            key="cutout_option"
        )
        
        # 特定チャンネル、タグ、または動画長が選択された場合は追加入力
        input_value = ""
        if cutout_option == "特定チャンネル":
            if channels:
                # チャンネル名をセレクトボックスから選択
                selected_channel = st.selectbox(
                    "チャンネルを選択", 
                    ["選択してください"] + channels, 
                    key="channel_select"
                )
                if selected_channel != "選択してください":
                    input_value = selected_channel
                
                # 手動入力のオプションも提供
                st.write("または手動で入力:")
                manual_channel = st.text_input("チャンネル名を入力", key="channel_manual")
                if manual_channel:
                    input_value = manual_channel
            else:
                input_value = st.text_input("チャンネル名を入力", key="channel_name")
                
        elif cutout_option == "特定タグ":
            if tags:
                # タグをセレクトボックスから選択
                selected_tag = st.selectbox(
                    "タグを選択", 
                    ["選択してください"] + tags, 
                    key="tag_select"
                )
                if selected_tag != "選択してください":
                    input_value = selected_tag
                
                # 手動入力のオプションも提供
                st.write("または手動で入力:")
                manual_tag = st.text_input("タグを入力", key="tag_manual")
                if manual_tag:
                    input_value = manual_tag
            else:
                input_value = st.text_input("タグを入力", key="tag_name")
                
        elif cutout_option == "動画長":
            # 最小時間設定
            st.write("**最小時間:**")
            col_min_hour, col_min_min = st.columns(2)
            with col_min_hour:
                min_hours = st.number_input("最小時間", min_value=0, max_value=23, value=0, key="min_hours")
            with col_min_min:
                min_minutes = st.number_input("最小分", min_value=0, max_value=59, value=0, key="min_minutes")
            
            # 最大時間設定
            st.write("**最大時間:**")
            col_max_hour, col_max_min = st.columns(2)
            with col_max_hour:
                max_hours = st.number_input("最大時間", min_value=0, max_value=23, value=1, key="max_hours")
            with col_max_min:
                max_minutes = st.number_input("最大分", min_value=0, max_value=59, value=0, key="max_minutes")
            
            # 最小から最大の範囲を引数として作成
            input_value = f"range_{min_hours}h{min_minutes}m_{max_hours}h{max_minutes}m"
        
        if st.button("✂️ 切り出し実行", key="cutout_button", help="YouTube後で見るリストから不要な動画を切り出します"):
            try:
                st.info(f"切り出し処理を開始しています...（{cutout_option}）")
                # 切り出しオプションを引数として渡す
                cutout_arg = {
                    "動画長": "duration_range",
                    "特定チャンネル": "specific_channel",
                    "特定タグ": "specific_tag"
                }[cutout_option]
                
                # コマンドライン引数を構築
                cmd_args = [sys.executable, "selenium/cutout_data.py", cutout_arg]
                if (cutout_option == "特定チャンネル" or cutout_option == "特定タグ" or cutout_option == "動画長") and input_value:
                    cmd_args.append(input_value)
                
                result = subprocess.run(cmd_args, 
                                      cwd=os.getcwd(), 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    st.success(f"切り出し処理が完了しました！（{cutout_option}）")
                else:
                    st.error(f"切り出し処理でエラーが発生しました: {result.stderr}")
            except Exception as e:
                st.error(f"切り出し処理の実行中にエラーが発生しました: {str(e)}")
    
    st.markdown("---")
    
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