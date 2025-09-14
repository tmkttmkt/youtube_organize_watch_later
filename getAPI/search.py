from googleapiclient.discovery import build
import isodate  # ISO 8601 duration変換に必要
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError(".envファイルにYOUTUBE_API_KEYが設定されていません")

youtube = build("youtube", "v3", developerKey=API_KEY)

def search_youtube_videos(query, max_results=5):
    """
    指定したキーワード(query)でYouTube動画を検索し、
    タイトル・URL・video_idの辞書リストを返す
    """
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        type="video"
    ).execute()

    results = []
    for item in search_response.get("items", []):
        video_id = item["id"].get("videoId")
        title = item["snippet"].get("title")
        if video_id and title:
            url = f"https://www.youtube.com/watch?v={video_id}"
            results.append({"title": title, "url": url, "video_id": video_id})
    return results

if __name__ == "__main__":
    import sys
    import json
    print("使い方: python search.py <検索キーワード> [max_results]")
    if len(sys.argv) > 2:
        query = sys.argv[1]
        max_results = int(sys.argv[2])
    elif len(sys.argv) > 1:
        query = sys.argv[1]
        max_results = 10
    else:
        query = " "
        max_results = 10
    results = search_youtube_videos(query, max_results=max_results)
    for item in results:
        print(f"タイトル: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"video_id: {item['video_id']}")
        print("---")
    # JSON保存
    save_path = "data/video_url.json"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"検索結果を {save_path} に保存しました")