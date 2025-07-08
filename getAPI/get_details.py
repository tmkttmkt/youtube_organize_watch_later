import json
import time
from api import get_video_details
import os

def load_watch_later_json():
    """watch_later.jsonからvideo_idのリストを読み込む"""
    try:
        with open("data/watch_later.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return [item["video_id"] for item in data]
    except FileNotFoundError:
        print("watch_later.jsonが見つかりません")
        return []
    except Exception as e:
        print(f"watch_later.jsonの読み込みエラー: {e}")
        return []

def save_details_json(details_list):
    """詳細情報をJSONファイルに保存"""
    output_path = "data/details_data.json"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(details_list, f, ensure_ascii=False, indent=2)
        print(f"詳細情報を {output_path} に保存しました")
    except Exception as e:
        print(f"ファイル保存エラー: {e}")

def main():
    print("YouTube動画詳細情報取得を開始します...")
    
    # watch_later.jsonからvideo_idリストを取得
    video_ids = load_watch_later_json()
    if not video_ids:
        print("取得するvideo_idがありません")
        return
    
    print(f"{len(video_ids)}個の動画の詳細情報を取得します")
    
    details_list = []
    success_count = 0
    error_count = 0
    
    for i, video_id in enumerate(video_ids, 1):
        print(f"進行状況: {i}/{len(video_ids)} - {video_id}")
        
        try:
            # YouTube APIで詳細情報を取得
            details = get_video_details(video_id)
            
            if details:
                # video_idも追加
                details["video_id"] = video_id
                details_list.append(details)
                success_count += 1
                print(f"  ✓ 成功: {details['title']}")
            else:
                error_count += 1
                print(f"  ✗ 失敗: 動画情報を取得できませんでした")
                
        except Exception as e:
            error_count += 1
            print(f"  ✗ エラー: {e}")
        
        # API制限を避けるため少し待機
        time.sleep(0.1)
        
        # 100件ごとに中間保存
        if i % 100 == 0:
            print(f"\n中間保存中... ({i}件処理済み)")
            save_details_json(details_list)
    
    # 最終保存
    save_details_json(details_list)
    
    print(f"\n処理完了!")
    print(f"成功: {success_count}件")
    print(f"失敗: {error_count}件")
    print(f"総処理数: {len(video_ids)}件")

if __name__ == "__main__":
    main()
