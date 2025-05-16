import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Seabornのスタイルを設定
sns.set_theme()

# 正しいフィールドサイズ（mm）
field_x_min, field_x_max = -6000, 6000  # X軸の範囲
field_y_min, field_y_max = -4500, 4500  # Y軸の範囲

# マス目のサイズを調整（200mm x 200mm に変更）
grid_size = 100

# ヒストグラムのビン数を再計算
bins_x = (field_x_max - field_x_min) // grid_size  # 60
bins_y = (field_y_max - field_y_min) // grid_size  # 45

# CSVファイルの読み込み（1列目: x座標, 2列目: y座標）
data = np.loadtxt("./out/ballpoji.csv", delimiter=",", skiprows=1)

# x, y 座標データを取得
x = data[:, 0]
y = data[:, 1]

# データの範囲を確認
print("X range:", np.min(x), "to", np.max(x))
print("Y range:", np.min(y), "to", np.max(y))

# 2次元ヒストグラム（ボールの分布）
heatmap_data, xedges, yedges = np.histogram2d(
    x, y, bins=[bins_x, bins_y], range=[[field_x_min, field_x_max], [field_y_min, field_y_max]]
)

# # データの偏りを軽減するために対数変換を適用
# heatmap_data = np.log1p(heatmap_data)

# しきい値を適用
X = 10
heatmap_data[heatmap_data > X] = X

# ヒートマップの描画
plt.figure(figsize=(12, 9))  # 4:3の比率
ax = sns.heatmap(
    heatmap_data.T, cmap="coolwarm", cbar=True, xticklabels=True, yticklabels=True, center=0,
    cbar_kws={'label': 'Ball Density (log scale)'}
)

# X 軸ラベルを設定
plt.xticks(
    ticks=np.linspace(0, bins_x, num=7),  # 7個のラベルを等間隔に配置
    labels=np.linspace(field_x_min, field_x_max, num=7, dtype=int)  # -6000 ～ 6000 の範囲で設定
)

# Y 軸ラベルを設定
plt.yticks(
    ticks=np.linspace(0, bins_y, num=7),
    labels=np.linspace(field_y_min, field_y_max, num=7, dtype=int)
)

# Y軸の反転（正しくマップするため）
ax.invert_yaxis()

# 軸の範囲を明示的に設定
plt.xlim(0, bins_x)
plt.ylim(0, bins_y)

# 軸ラベルとタイトル
plt.xlabel("X Position (mm)")
plt.ylabel("Y Position (mm)")
plt.title("Ball Position Heatmap (RoboCup SSL)")

# グラフの表示
plt.show()