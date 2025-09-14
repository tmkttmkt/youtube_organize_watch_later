# ...existing code...
import os
import json
import sys
import time
import importlib.util

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "watch_later.json")
SEARCH_PY = os.path.join(PROJECT_ROOT, "getAPI", "search.py")
ADD_LIKE_PY = os.path.join(PROJECT_ROOT, "selenium", "add_like.py")

def load_module_from_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ...existing code...
def main(max_results=10, search_query=None):
    # load search.py
    search = load_module_from_path(SEARCH_PY, "getAPI.search")
    # 引数がなければ空検索（仕様どおり）
    query = search_query if search_query is not None else " "
    results = search.search_youtube_videos(query, max_results=max_results)
    if not results:
        print("検索結果が空です。終了します。")
        return

    # 保存先作成と書き込み（add_like が参照するパス）
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"検索結果を保存しました: {DATA_PATH} ({len(results)}件)")

    # 少し待ってファイルシステムの整合性を確保
    time.sleep(0.5)

    # load add_like.py と実行
    add_like = load_module_from_path(ADD_LIKE_PY, "selenium.add_like")
    # add_like モジュールの main() を呼ぶ
    if hasattr(add_like, "main"):
        # add_like がデータファイルを参照する実装になっている想定
        add_like.main()
    else:
        print("add_like.py に main() が見つかりません。手動で実行してください。")

if __name__ == "__main__":
    # 必要なら max_results や検索クエリを引数で渡せるようにする
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=10, help="検索で取得する最大件数")
    p.add_argument("query", nargs="?", default=None, help="検索ワード（省略すると空検索）")
    args = p.parse_args()
    main(max_results=args.max, search_query=args.query)
# ...existing code...