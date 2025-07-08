import pandas as pd
import json
import numpy as np
from datetime import datetime
import re

def load_details_data():
    """details_data.jsonを読み込む"""
    try:
        with open("data/details_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("details_data.jsonが見つかりません")
        return []
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return []

def preprocess_duration(duration_sec):
    """動画時間（秒）を分:秒形式に変換"""
    if pd.isna(duration_sec) or duration_sec == 0:
        return "0:00"
    
    minutes = int(duration_sec // 60)
    seconds = int(duration_sec % 60)
    
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def preprocess_published_date(published_at):
    """公開日時を日本時間に変換"""
    if pd.isna(published_at) or published_at == "":
        return None
    
    try:
        # ISO 8601形式をパース
        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        # 日本時間に変換（UTC+9）
        dt_jst = dt.replace(tzinfo=None) + pd.Timedelta(hours=9)
        return dt_jst
    except:
        return None

def extract_time_features(published_at):
    """公開日時から機械学習用の時間特徴量を抽出"""
    if pd.isna(published_at) or published_at == "":
        return {
            'year': 2020,  # デフォルト値
            'month': 1,
            'day': 1,
            'hour': 12,
            'day_of_week': 0,
            'day_of_year': 1,
            'week_of_year': 1,
            'quarter': 1,
            'is_weekend': 0,
            'is_holiday_season': 0,
            'time_of_day': 'afternoon',
            'days_since_epoch': 18262  # 2020-01-01からの日数
        }
    
    try:
        # ISO 8601形式をパース
        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        # 日本時間に変換（UTC+9）
        dt_jst = dt.replace(tzinfo=None) + pd.Timedelta(hours=9)
        
        # 基本的な時間特徴量
        year = dt_jst.year
        month = dt_jst.month
        day = dt_jst.day
        hour = dt_jst.hour
        day_of_week = dt_jst.weekday()  # 0=月曜日, 6=日曜日
        day_of_year = dt_jst.timetuple().tm_yday
        week_of_year = dt_jst.isocalendar()[1]
        quarter = (month - 1) // 3 + 1
        
        # 派生特徴量
        is_weekend = 1 if day_of_week >= 5 else 0  # 土日
        
        # ホリデーシーズン（12月、1月、8月）
        is_holiday_season = 1 if month in [12, 1, 8] else 0
        
        # 時間帯の分類
        if 5 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 18:
            time_of_day = 'afternoon'
        elif 18 <= hour < 22:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        # エポック（1970-01-01）からの日数
        epoch = datetime(1970, 1, 1)
        days_since_epoch = (dt_jst.replace(tzinfo=None) - epoch).days
        
        return {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'day_of_week': day_of_week,
            'day_of_year': day_of_year,
            'week_of_year': week_of_year,
            'quarter': quarter,
            'is_weekend': is_weekend,
            'is_holiday_season': is_holiday_season,
            'time_of_day': time_of_day,
            'days_since_epoch': days_since_epoch
        }
    except:
        # エラー時はデフォルト値を返す
        return {
            'year': 2020,
            'month': 1,
            'day': 1,
            'hour': 12,
            'day_of_week': 0,
            'day_of_year': 1,
            'week_of_year': 1,
            'quarter': 1,
            'is_weekend': 0,
            'is_holiday_season': 0,
            'time_of_day': 'afternoon',
            'days_since_epoch': 18262
        }

def clean_description(description):
    """動画説明をクリーンアップ"""
    if pd.isna(description) or description == "":
        return ""
    
    # 改行を空白に置換
    cleaned = re.sub(r'\n+', ' ', description)
    # 連続する空白を単一の空白に
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # 先頭と末尾の空白を削除
    cleaned = cleaned.strip()
    # 長すぎる場合は切り詰め
    if len(cleaned) > 500:
        cleaned = cleaned[:500] + "..."
    
    return cleaned

def preprocess_data(data):
    """データの事前処理を実行"""
    print("データの事前処理を開始...")
    
    # pandas DataFrameに変換
    df = pd.DataFrame(data)
    
    print(f"読み込み件数: {len(df)}件")
    
    # 欠損データの確認
    print("\n=== 欠損データの確認 ===")
    missing_data = df.isnull().sum()
    for col, count in missing_data.items():
        if count > 0:
            print(f"{col}: {count}件")
    
    # 基本的なクリーニング
    print("\n=== データクリーニング ===")
    
    # 欠損値を適切な値で埋める
    df['title'] = df['title'].fillna('タイトル不明')
    df['channelTitle'] = df['channelTitle'].fillna('チャンネル不明')
    df['description'] = df['description'].fillna('')
    df['tags'] = df['tags'].fillna('').apply(lambda x: x if isinstance(x, list) else [])
    df['duration_sec'] = df['duration_sec'].fillna(0)
    df['viewCount'] = df['viewCount'].fillna(0)
    df['likeCount'] = df['likeCount'].fillna(0)
    df['commentCount'] = df['commentCount'].fillna(0)
    
    # 新しいカラムを追加
    print("新しいカラムを追加中...")
    
    # 動画時間を分:秒形式で追加
    df['duration_formatted'] = df['duration_sec'].apply(preprocess_duration)
    
    # 公開日時を日本時間で追加
    df['published_at_jst'] = df['publishedAt'].apply(preprocess_published_date)
    
    # 説明文のクリーンアップ
    df['description_clean'] = df['description'].apply(clean_description)
    
    # タグ数を追加
    df['tag_count'] = df['tags'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    
    # エンゲージメント率（いいね数/視聴回数）
    df['engagement_rate'] = np.where(
        df['viewCount'] > 0, 
        df['likeCount'] / df['viewCount'] * 100, 
        0
    )
    
    # 視聴回数のlog変換
    df['viewCount_log'] = np.where(
        df['viewCount'] > 1,  # 1より大きい場合のみlog変換
        np.log10(df['viewCount']),
        0
    )
    
    # 動画時間のlog変換
    df['duration_log'] = np.where(
        df['duration_sec'] > 1,  # 1より大きい場合のみlog変換
        np.log10(df['duration_sec']),
        0
    )
    
    # フラグ系の特徴量を追加
    print("フラグ系特徴量を追加中...")
    
    # プライバシーステータス（0: public, 1: unlisted, 2: private）
    privacy_mapping = {'public': 0, 'unlisted': 1, 'private': 2}
    df['privacy_status_flag'] = df['privacyStatus'].fillna('public').map(privacy_mapping).fillna(0)
    
    # キャプション有無（True/False -> 1/0）
    df['caption_flag'] = df['caption'].fillna(False).apply(lambda x: 1 if x is True or x == 'true' or x == True else 0)
    
    # ライセンスコンテンツ（True/False -> 1/0）
    df['licensed_content_flag'] = df['licensedContent'].fillna(False).apply(lambda x: 1 if x is True or x == 'true' or x == True else 0)
    
    # 子供向けコンテンツ（True/False -> 1/0）
    df['made_for_kids_flag'] = df['madeForKids'].fillna(False).apply(lambda x: 1 if x is True or x == 'true' or x == True else 0)
    
    # 動画定義（hd/sd -> 1/0）
    df['definition_hd_flag'] = (df['definition'].fillna('sd') == 'hd').astype(int)
    
    # 動画次元（2d/3d -> 0/1）
    df['dimension_3d_flag'] = (df['dimension'].fillna('2d') == '3d').astype(int)
    
    # カテゴリIDを数値として使用
    df['category_id'] = pd.to_numeric(df['categoryId'].fillna(0), errors='coerce').fillna(0).astype(int)
    
    # カテゴリIDのワンホットエンコーディング
    print("カテゴリIDをワンホットエンコーディング中...")
    category_dummies = pd.get_dummies(df['category_id'], prefix='category')
    df = pd.concat([df, category_dummies], axis=1)
    
    # 公開日時から時間特徴量を抽出してDataFrameに展開
    print("公開日時から時間特徴量を抽出中...")
    time_features_list = df['publishedAt'].apply(extract_time_features)
    
    # 時間特徴量を個別のカラムとして展開
    time_features_df = pd.DataFrame(time_features_list.tolist())
    
    # 元のDataFrameに時間特徴量を結合
    for col in time_features_df.columns:
        df[f'pub_{col}'] = time_features_df[col]
    
    # 機械学習用カラムの順序を整理
    ml_columns_order = [
        'video_id',  # 識別用（機械学習では使わないが管理用に保持）
        # 数値特徴量
        'duration_sec', 'duration_log', 'viewCount', 'viewCount_log', 
        'likeCount', 'commentCount', 'engagement_rate', 'tag_count',
        # フラグ系特徴量
        'privacy_status_flag', 'caption_flag', 'licensed_content_flag', 
        'made_for_kids_flag', 'definition_hd_flag', 'dimension_3d_flag',
        # 時間特徴量
        'pub_year', 'pub_month', 'pub_day', 'pub_hour', 'pub_day_of_week',
        'pub_day_of_year', 'pub_week_of_year', 'pub_quarter', 'pub_is_weekend',
        'pub_is_holiday_season', 'pub_time_of_day', 'pub_days_since_epoch'
    ]
    
    # カテゴリのワンホットエンコーディングカラムを追加
    category_columns = [col for col in df.columns if col.startswith('category_')]
    ml_columns_order.extend(category_columns)
    
    # 存在するカラムのみを選択
    available_columns = [col for col in ml_columns_order if col in df.columns]
    df_processed = df[available_columns].copy()
    
    print(f"\n処理後件数: {len(df_processed)}件")
    print(f"カラム数: {len(df_processed.columns)}個")
    
    return df_processed

def save_processed_data(df):
    """処理済みデータを保存"""
    try:
        # 機械学習用の特徴量のみを抽出
        ml_features = ['video_id', 'duration_sec', 'duration_log', 'viewCount', 'viewCount_log', 
                      'likeCount', 'commentCount', 'engagement_rate', 'tag_count',
                      'privacy_status_flag', 'caption_flag', 'licensed_content_flag', 
                      'made_for_kids_flag', 'definition_hd_flag', 'dimension_3d_flag',
                      'pub_year', 'pub_month', 'pub_day', 'pub_hour', 'pub_day_of_week',
                      'pub_day_of_year', 'pub_week_of_year', 'pub_quarter', 'pub_is_weekend',
                      'pub_is_holiday_season', 'pub_time_of_day', 'pub_days_since_epoch']
        
        # カテゴリのワンホットエンコーディングカラムを追加
        category_columns = [col for col in df.columns if col.startswith('category_')]
        ml_features.extend(category_columns)
        
        # 存在するカラムのみを選択
        available_ml_features = [col for col in ml_features if col in df.columns]
        df_ml = df[available_ml_features].copy()
        
        # 機械学習用CSVを保存
        csv_path = "data/ml_features.csv"
        df_ml.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"機械学習用CSVファイルを保存: {csv_path} ({len(available_ml_features)}カラム)")
        
        # 機械学習用特徴量の詳細情報をJSONで保存
        category_columns = [col for col in df_ml.columns if col.startswith('category_')]
        feature_info = {
            'numeric_features': [col for col in available_ml_features if col not in ['video_id', 'pub_time_of_day'] and not col.startswith('category_')],
            'categorical_features': ['pub_time_of_day'] if 'pub_time_of_day' in available_ml_features else [],
            'category_onehot_features': category_columns,
            'feature_count': len(available_ml_features),
            'record_count': len(df_ml),
            'description': '機械学習用に前処理済みのYouTube動画特徴量データセット（カテゴリIDワンホットエンコーディング済み）'
        }
        
        feature_info_path = "data/ml_feature_info.json"
        with open(feature_info_path, 'w', encoding='utf-8') as f:
            json.dump(feature_info, f, ensure_ascii=False, indent=2)
        print(f"機械学習用特徴量情報を保存: {feature_info_path}")
        
    except Exception as e:
        print(f"保存エラー: {e}")

def display_sample_data(df, n=5):
    """サンプルデータを表示"""
    print(f"\n" + "="*50)
    print(f"機械学習用データサンプル（先頭{n}件）")
    print("="*50)
    
    # 主要な機械学習特徴量のみを表示
    display_columns = ['video_id', 'duration_log', 'viewCount_log', 'engagement_rate',
                      'privacy_status_flag', 'caption_flag', 'made_for_kids_flag',
                      'pub_year', 'pub_month', 'pub_day_of_week', 'pub_time_of_day']
    
    available_display_columns = [col for col in display_columns if col in df.columns]
    sample_df = df[available_display_columns].head(n)
    
    for i, row in sample_df.iterrows():
        print(f"\n--- データ {i+1} ---")
        for col in available_display_columns:
            if col in ['duration_log', 'viewCount_log', 'engagement_rate']:
                print(f"{col}: {row[col]:.3f}")
            else:
                print(f"{col}: {row[col]}")

def display_feature_info(df):
    """機械学習用特徴量の情報を表示"""
    print(f"\n" + "="*50)
    print("機械学習用特徴量情報")
    print("="*50)
    
    # 機械学習用の数値特徴量
    ml_numeric_features = ['duration_sec', 'duration_log', 'viewCount', 'viewCount_log', 'likeCount', 
                          'commentCount', 'engagement_rate', 'tag_count',
                          'privacy_status_flag', 'caption_flag', 'licensed_content_flag', 
                          'made_for_kids_flag', 'definition_hd_flag', 'dimension_3d_flag',
                          'pub_year', 'pub_month', 'pub_day', 'pub_hour', 'pub_day_of_week',
                          'pub_day_of_year', 'pub_week_of_year', 'pub_quarter', 'pub_is_weekend',
                          'pub_is_holiday_season', 'pub_days_since_epoch']
    
    print(f"\n【機械学習用数値特徴量】({len([col for col in ml_numeric_features if col in df.columns])}個)")
    for col in ml_numeric_features:
        if col in df.columns:
            if col in ['privacy_status_flag', 'caption_flag', 'licensed_content_flag', 
                      'made_for_kids_flag', 'definition_hd_flag', 'dimension_3d_flag',
                      'pub_is_weekend', 'pub_is_holiday_season']:
                # フラグ系は分布を表示
                counts = df[col].value_counts().sort_index()
                print(f"  {col}: {counts.to_dict()}")
            else:
                # 数値系は統計情報を表示
                print(f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, "
                      f"mean={df[col].mean():.2f}, std={df[col].std():.2f}")
    
    # 機械学習用カテゴリ特徴量（ワンホットエンコーディング対象）
    ml_categorical_features = ['pub_time_of_day']
    print(f"\n【機械学習用カテゴリ特徴量】")
    for col in ml_categorical_features:
        if col in df.columns:
            categories = df[col].value_counts()
            print(f"  {col}: {categories.to_dict()}")
    
    # カテゴリIDのワンホットエンコーディング情報
    category_columns = [col for col in df.columns if col.startswith('category_')]
    if category_columns:
        print(f"\n【カテゴリIDワンホットエンコーディング】({len(category_columns)}個)")
        # 元のcategory_idの分布を表示
        if 'category_id' in df.columns:
            original_categories = df['category_id'].value_counts().sort_index()
            print(f"  元のカテゴリ分布: {original_categories.to_dict()}")
        print(f"  ワンホットエンコーディング後: {len(category_columns)}カラム")
        print(f"  カラム例: {category_columns[:5]}...")  # 最初の5個を表示
    
    print(f"\n【データセット情報】")
    print(f"  総レコード数: {len(df):,}件")
    print(f"  特徴量数: {len(df.columns)}個")
    print(f"  数値特徴量: {len([col for col in ml_numeric_features if col in df.columns])}個")
    print(f"  カテゴリ特徴量: {len([col for col in ml_categorical_features if col in df.columns])}個")
    category_columns = [col for col in df.columns if col.startswith('category_')]
    print(f"  カテゴリワンホット: {len(category_columns)}個")
    
    print(f"\n【出力ファイル】")
    print("  - ml_features.csv: 機械学習用特徴量データセット")
    print("  - ml_feature_info.json: 特徴量の詳細情報（メタデータ）")

def main():
    print("YouTube動画データ事前処理を開始します...")
    
    # データ読み込み
    raw_data = load_details_data()
    if not raw_data:
        return
    
    # 事前処理実行
    df_processed = preprocess_data(raw_data)
    
    # データ保存
    save_processed_data(df_processed)
    
    # サンプルデータ表示
    display_sample_data(df_processed)
    
    # 機械学習用特徴量情報表示
    display_feature_info(df_processed)
    
    print("\n処理完了!")

if __name__ == "__main__":
    main()