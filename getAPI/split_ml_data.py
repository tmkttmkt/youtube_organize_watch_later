import pandas as pd

# ファイルパス
FEATURES_PATH = "data/ml_features.csv"
LABELS_PATH = "data/manual_classify.csv"
TRAIN_PATH = "data/ml_train.csv"
TEST_PATH = "data/ml_test.csv"
UNLABELED_PATH = "data/ml_unlabeled.csv"

# データ読み込み
features = pd.read_csv(FEATURES_PATH)
labels = pd.read_csv(LABELS_PATH)


# video_idで結合（ラベルありデータ）
labeled = pd.merge(features, labels, on="video_id", how="inner")
labeled.to_csv(TRAIN_PATH, index=False, encoding="utf-8")
print(f"ラベルありデータ: {TRAIN_PATH} ({len(labeled)}件)")

# ラベルがない特徴量データ（予測対象）
labeled_ids = set(labeled["video_id"])
unlabeled = features[~features["video_id"].isin(labeled_ids)]
unlabeled.to_csv(UNLABELED_PATH, index=False, encoding="utf-8")
print(f"ラベルなし予測対象: {UNLABELED_PATH} ({len(unlabeled)}件)")
