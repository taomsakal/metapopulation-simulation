import pandas as pd
import matplotlib.pyplot as plt
import os
file_path = 'save_data/' + input("Which file?") + '.csv'
print("Current Files")
print(os.listdir(file_path))

df = pd.read_csv(file_path, header=None, names=['rv', 'rs', 'kv', 'ks', 're'])
df.plot()
plt.show()