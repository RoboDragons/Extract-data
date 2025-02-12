import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter
print("tkinter is installed and ready to use!")

# バックエンドの設定
mpl.use('TkAgg')  # または 'Qt5Agg'

# Seabornのスタイルを設定
sns.set_theme()

# ./outからデータを取得する
data = np.loadtxt("./out/ssl-vision-client.csv", delimiter=",", skiprows=1)

# ヒートマップの作成
sns.heatmap(data,linewidths=0.5)

# グラフの表示
plt.show()
