import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = 'save_data/' + input("Which file?") + '.csv'
num_strains = int(input("How many strains?"))

n = []
for i in range(0, num_strains):
    n.append('v' + str(i+1))
    n.append('s' + str(i+1))
n.append('re')

df = pd.read_csv(file_path, header=None, names=n)
df.plot()
plt.show()
