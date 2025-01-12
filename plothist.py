import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('iris.csv')
ax = df.describe()
print(ax)

plt.hist(df['sepal.length'])
plt.show()

#ここまでは同じ---------------------------------------------------------------

import numpy as np

start = 4
end = 10
interval = 1
bins_count = end - start + 1

bins = np.linspace(start, end, bins_count)

plt.xticks(np.arange(start, end+interval, interval))
plt.xlim(start, end)

plt.hist(df['sepal.length'], bins=bins, rwidth=0.9,align='mid')
plt.show()