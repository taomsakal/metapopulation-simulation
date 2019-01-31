import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

def make_graph_from_csv(csv_path, xaxis=None, yaxis=None, title=None, kind=None, ignore_list=None, include_list=None):
    """
    Makes a graph from a csv file. The first column is the x-axis and all the others get their own line.
    Args:
        csv_path: path to the csv file
        xaxis: the string for the x axis. If it is None then use the first column
        ignore_list: A list of columns to not graph. If None then graphs all columns except the for the x-axis
        include_list: A list of columns that we only graph. If None then graph all columns
        type: The type of graph we want. Ex: put 'bar' for a bar graph. If None then is a line graph

    Returns:
        a graph object?

    """

    try:
        df = pd.read_csv(csv_path)  # Load the csv into a dataframe
    except ValueError:
        raise ValueError(f"Cannot find file at {csv_path}.")

    if ignore_list is not None:
        df.drop(ignore_list)  # Drop the labels to ignore

    df.plot(kind=kind, xaxis=xaxis, yaxis=yaxis, title=title)
    plt.show()

if __name__ == "__main__":

    folder_name = "Colonization 1000"

    # Set the folder path
    os.chdir(os.path.dirname(sys.argv[0]))  # Change current working directory to wherever dashboard.py is
    folder_path = Path.cwd() / 'AM_programs' / 'save_data' / folder_name
    print("Folder Path:", folder_path)
    print(os.listdir(folder_path))

    # Todo: Make the rest of the graphs generate, fix the bug

    make_graph_from_csv(Path(folder_path/"average_eqs.csv"), xaxis="Sporulation Probability", yaxis="Final Eq Frequency", title="Average Eq Frequency")

