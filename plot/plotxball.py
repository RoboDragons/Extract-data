import pandas as pd
import matplotlib.pyplot as plt

# データの読み込み
dataframe = pd.read_csv('../out/ssl-vision-client.csv')
dataframe.head()

# ヒストグラムのプロット
dataframe['x'].hist(bins=20)  # 基数の数を20個にする

plt.hist(dataframe['x'].dropna(), bins=10, range=(-6000, 6000), color='Blue')
plt.xlabel('X Position')
plt.ylabel('Frequency')
plt.title('Histogram of X Position')
plt.show()
