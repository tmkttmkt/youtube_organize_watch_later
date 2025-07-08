from googleapiclient.discovery import build
import isodate  # ISO 8601 duration変換に必要
import datetime

API_KEY = "AIzaSyDo7Ec6uv-jYpcx59h6HbKzzBwEOWgxHHY"
youtube = build("youtube", "v3", developerKey=API_KEY)

def get_video_details(video_id):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,topicDetails,recordingDetails,status",
        id=video_id
    )
    response = request.execute()

    if not response["items"]:
        print(f"動画ID {video_id} は無効または非公開です")
        return None

    item = response["items"][0]

    # ISO 8601 durationを秒に変換
    duration_iso = item["contentDetails"]["duration"]
    duration_sec = isodate.parse_duration(duration_iso).total_seconds()

    details = {
        # snippet
        "title": item["snippet"]["title"],
        "channelTitle": item["snippet"]["channelTitle"],
        "description": item["snippet"].get("description", ""),
        "tags": item["snippet"].get("tags", []),
        "categoryId": item["snippet"].get("categoryId", ""),
        "publishedAt": item["snippet"]["publishedAt"],

        # contentDetails
        "duration_sec": duration_sec,
        "dimension": item["contentDetails"].get("dimension", ""),
        "definition": item["contentDetails"].get("definition", ""),
        "caption": item["contentDetails"].get("caption", ""),  # "true"/"false"
        "licensedContent": item["contentDetails"].get("licensedContent", False),

        # statistics
        "viewCount": int(item["statistics"].get("viewCount", 0)),
        "likeCount": int(item["statistics"].get("likeCount", 0)),
        "commentCount": int(item["statistics"].get("commentCount", 0)),

        # topicDetails (WikipediaトピックID)
        "relevantTopicIds": item.get("topicDetails", {}).get("relevantTopicIds", []),

        # recordingDetails
        "recordingDate": item.get("recordingDetails", {}).get("recordingDate", None),
        "locationDescription": item.get("recordingDetails", {}).get("locationDescription", ""),

        # status
        "madeForKids": item.get("status", {}).get("madeForKids", False),
        "privacyStatus": item.get("status", {}).get("privacyStatus", ""),
    }

    return details
if __name__ == "__main__":
    # テスト
    video_id = "GLDpHE2LMS0"  # 任意のvideoIdに置き換え
    info = get_video_details(video_id)
    if info:
        for k, v in info.items():
            print(f"{k}: {v}")
