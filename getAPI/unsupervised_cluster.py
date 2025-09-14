import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# データ読み込み（ラベルなし特徴量のみ）
df = pd.read_csv('./data/ml_unlabeled.csv')
X = df.drop(['video_id'], axis=1)

# クラスタ数（例：7）
n_clusters = 7
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
kmeans.fit(X)

# クラスタ結果を保存
df['cluster'] = kmeans.labels_
df.to_csv('../ml_unlabeled_clustered.csv', index=False)
print(f'クラスタリング結果保存: ml_unlabeled_clustered.csv')

# クラスタ分布可視化（2次元PCA）
try:
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    plt.scatter(X_pca[:,0], X_pca[:,1], c=kmeans.labels_)
    plt.title('KMeansクラスタ分布(PCA)')
    plt.savefig('../cluster_pca.png')
    print('クラスタ分布画像保存: cluster_pca.png')
except Exception as e:
    print('PCA可視化失敗:', e)
