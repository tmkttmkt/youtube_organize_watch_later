def seconds_to_length(seconds):
    """
    秒数を00:02:43や01:02:43のような形式に変換
    引数: seconds (int) - 秒数
    戻り値: 文字列 (例: '01:02:43' または '02:43')
    """
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"
    else:
        return f"{m:02}:{s:02}"

def length_to_seconds(length_str):
    """
    長さ文字列や時間文字列を秒数に変換
    例: "00:08:56" → 536, "2 分 38 秒" → 158, "1 時間 2 分 3 秒" → 3723, "2:01:50" → 7310, "1:13" → 73
    日本語表記やコロン区切り両方に対応
    引数: length_str (str)
    戻り値: int (秒数)
    """
    if not length_str:
        return 0
    import re
    jp = re.match(r"(?:(\d+)\s*時間)?\s*(?:(\d+)\s*分)?\s*(?:(\d+)\s*秒)?", length_str)
    if jp and (jp.group(1) or jp.group(2) or jp.group(3)):
        h = int(jp.group(1)) if jp.group(1) else 0
        m = int(jp.group(2)) if jp.group(2) else 0
        s = int(jp.group(3)) if jp.group(3) else 0
        return h*3600 + m*60 + s
    # コロン区切り
    parts = [int(p) for p in length_str.strip().split(":") if p.isdigit()]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    elif len(parts) == 2:
        return parts[0]*60 + parts[1]
    elif len(parts) == 1:
        return int(parts[0])
    else:
        return 0

def seconds_to_hms(sec):
    """
    秒数を「hh:mm:ss」形式の文字列に変換
    引数: sec (int)
    戻り値: 文字列 (例: '01:02:43')
    """
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02}:{m:02}:{s:02}"
