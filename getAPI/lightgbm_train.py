import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# データ読み込み
train_df = pd.read_csv('./data/ml_train.csv')
X = train_df.drop(['video_id', 'category', 'pub_time_of_day', 'title'], axis=1)
y = train_df['category']

# 学習・テスト分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# モデル学習
clf = LGBMClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 予測・評価
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

# モデル保存
joblib.dump(clf, '../lgbm_model.pkl')
print('LightGBMモデル保存: lgbm_model.pkl')
