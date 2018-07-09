import pandas as pd
import numpy
import math
import csv

while True:
    filePath = input("Which file?")  # Within KellyCSV
    colorTitle = input("Title of color column?")
    countTitle = input("Title of count column?")

    data = [[], []]  # Empty Array for red & green cell count

    df = pd.read_csv(filePath)  # Imports the csv into a Pandas Dataframe

    for i in df.index:  # Append cell counts to array
        if df[colorTitle][i] == 'red':
            data[0].append(str(df[countTitle][i]))
        elif df[colorTitle][i] == 'green':
            data[1].append(str(df[countTitle][i]))

    index = df.columns.get_loc(colorTitle)  # Get location to insert new columns
    df = df.drop(colorTitle, axis=1).drop(countTitle, axis=1)  # Remove the unnecessary columns

    x = int(len(df.index + 1) / 2)  # Drop every other row, since they are duplicates
    for i in range(0, x):
        df = df.drop(df.index[i])

    data[0] = data[0] + [''] * (len(df.index) - len(data[0]))  # Adds blank spaces to array to make merging easier
    data[1] = data[1] + [''] * (len(df.index) - len(data[1]))

    df.insert(index, "Red Count", data[0])  # Merges columns to Dataframe
    df.insert(index, "Green Count", data[1])

    df.to_csv(filePath)  # Saves Dataframe to original csv file
