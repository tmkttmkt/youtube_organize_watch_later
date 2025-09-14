# ...existing code...
import os
import json
import time
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
# ...existing code...

# 設定
PROFILE_DIR = "Profile 1"
DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "watch_later.json"))
MAX_RETRIES = 3
WAIT_TIMEOUT = 30
PAUSE_AFTER_CLICK = 1.5
# ...existing code...
LIKE_XPATH = (
    "//button[@aria-label and ("
    "contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'like') or "
    "contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'いいね') or "
    "contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'高く評価')"
    ")]"
)

def is_already_liked(btn):
    try:
        aria_pressed = btn.get_attribute("aria-pressed")
        if aria_pressed and aria_pressed.lower() == "true":
            return True
        aria_label = (btn.get_attribute("aria-label") or "").lower()
        if "liked" in aria_label or "いいね済み" in aria_label or "高く評価済み" in aria_label:
            return True
    except Exception:
        pass
    return False

def click_button_safe(driver, btn):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        time.sleep(0.2)
        try:
            btn.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", btn)
        return True
    except Exception:
        return False
def get_driver(profile_dir=PROFILE_DIR):
    options = uc.ChromeOptions()
    user_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "User Data"))
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile_dir}")
    # 必要ならオプションを追加（例: ウィンドウサイズ固定など）
    return uc.Chrome(options=options)
def load_urls(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    urls = []
    for item in data:
        url = item.get("url") or item.get("video_url") or item.get("watch_url")
        if url:
            urls.append({"url": url, "title": item.get("title","")})
    return urls

def _extract_video_id(url):
    try:
        q = parse_qs(urlparse(url).query)
        if "v" in q:
            return q["v"][0]
        # パス形式 (/shorts/xxxx) の場合
        path = urlparse(url).path.strip("/")
        if path:
            return path.split("/")[-1]
    except Exception:
        pass
    return "unknown"

def _dismiss_consent(driver):
    # 簡易: 同意系ボタンを探してクリック（日本語/英語に対応）
    candidates = [
        "//button//*[text()[contains(.,'同意')]]/ancestor::button",
        "//button//*[text()[contains(.,'同意する')]]/ancestor::button",
        "//button//*[text()[contains(.,'Accept')]]/ancestor::button",
        "//button//*[text()[contains(.,'I agree')]]/ancestor::button"
    ]
    for xp in candidates:
        try:
            el = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, xp)))
            try:
                el.click()
                time.sleep(0.5)
                return True
            except Exception:
                driver.execute_script("arguments[0].click();", el)
                time.sleep(0.5)
                return True
        except Exception:
            continue
    return False

def main():
    urls = load_urls(DATA_FILE)
    if not urls:
        print(f"データファイルに動画URLが見つかりません: {DATA_FILE}")
        return

    driver = get_driver()
    liked_count = 0
    try:
        for entry in urls:
            url = entry["url"]
            title = entry.get("title","")
            vid = _extract_video_id(url)
            print(f"開く: {title} -> {url}")
            success = False
            for attempt in range(MAX_RETRIES):
                try:
                    driver.get(url)
                    # まずトップレベルのボタンコンテナが来るまで待つ
                    WebDriverWait(driver, WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#top-level-buttons-computed, ytd-video-primary-info-renderer"))
                    )
                    # Cookie等の同意ダイアログを閉じてみる
                    _dismiss_consent(driver)

                    # top-level-buttons-computed 内のボタン群を取得して「いいね」らしきボタンを探す
                    btn = None
                    try:
                        container = driver.find_element(By.ID, "top-level-buttons-computed")
                        candidates = container.find_elements(By.XPATH, ".//button[@aria-label]")
                        for c in candidates:
                            al = (c.get_attribute("aria-label") or "").lower()
                            if "いいね" in al or "like" in al or "高く評価" in al:
                                btn = c
                                break
                    except Exception:
                        btn = None

                    # フォールバック: 全ページ検索（既存のXPath）
                    if not btn:
                        buttons = driver.find_elements(By.XPATH, LIKE_XPATH)
                        if buttons:
                            btn = buttons[0]

                    if not btn:
                        raise TimeoutException("いいねボタンが見つかりません")

                    if is_already_liked(btn):
                        print("既に高評価済み。スキップ。")
                        success = True
                        break

                    ok = click_button_safe(driver, btn)
                    if ok:
                        liked_count += 1
                        print(f"高評価しました ({liked_count})")
                        time.sleep(PAUSE_AFTER_CLICK)
                        success = True
                        break
                    else:
                        print("クリックに失敗しました。リトライします。")
                except TimeoutException:
                    print("ページ読み込み/ボタン待機タイムアウト。リトライします。")
                    # デバッグ用にページソース保存
                    try:
                        fn = os.path.join(os.path.dirname(__file__), f"debug_{vid}.html")
                        with open(fn, "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        print(f"ページソースを保存しました: {fn}")
                    except Exception as e:
                        print(f"ページソース保存失敗: {e}")
                except WebDriverException as e:
                    print(f"WebDriver例外: {e}. リトライします。")
                time.sleep(1)
            if not success:
                print(f"処理失敗: {url}")
    finally:
        print(f"処理終了。合計高評価数: {liked_count}")
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()
# ...existing code...