import numpy as np
import pandas as pd

# np.random.seed(42) # 乱数を固定
# z = np.random.randn(2,50) # x,yの値を50個ずつ作成
dataframe = pd.read_csv('./out/ssl-vision-client.csv')
dataframe.head()

z=[dataframe['x'],dataframe['y']]
print(z)
print("------------------------------------------")
print(dataframe)
print("------------------------------------------")
print(z[0])
print("------------------------------------------")

hist, xedges, yedges = np.histogram2d(z[0], z[1], bins=50) # ５個区切りでxとyのヒストグラムを作成

xpos, ypos = np.meshgrid(xedges[:-1], yedges[:-1]) # x,y座標を3D用の形式に変換（その１）
zpos = 0 # zは常に0を始点にする

dx = xpos[0][1] - xpos[0][0] # x座標の幅を設定
dy = ypos[1][0] - ypos[0][0] # y座標の幅を設定

# dx = 1000
# dy = 1000
dz = hist.ravel() # z座標の幅は棒の長さに相当

xpos = xpos.ravel() # x座標を3D用の形式に変換（その２）
ypos = ypos.ravel() # y座標を3D用の形式に変換（その２）

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure() # 描画領域を作成
ax = fig.add_subplot(111, projection="3d") # 3Dの軸を作成
ax.bar3d(xpos,ypos,zpos,dx,dy,dz) # ヒストグラムを3D空間に表示
plt.title("Histogram 2D") # タイトル表示
plt.xlabel("X") # x軸の内容表示
plt.ylabel("Y") # y軸の内容表示
ax.set_zlabel("Z") # z軸の内容表示
plt.show()