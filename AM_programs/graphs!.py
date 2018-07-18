import pandas as pd
import matplotlib.pyplot as plt

file_path = 'save_data/' + input("Which file?") + '.csv'

df = pd.read_csv(file_path, header=None, names=['rv', 'rs', 'kv', 'ks', 're'])
df.plot()
plt.show()