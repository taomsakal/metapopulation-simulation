import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

from simrules import helpers


def make_graph_from_csv(csv_path, x=None, y=None, show=True, drop=0, xlabel=None, ylabel=None, title="title", kind=None, ignore_list=None, include_list=None):
    """
    Makes a graph from a csv file. The first column is the x-axis and all the others get their own line.
    Args:
        csv_path: path to the csv file
        xlabel: the string for the x axis. If it is None then use the first column
        ignore_list: A list of columns to not graph. If None then graphs all columns except the for the x-axis
        include_list: A list of columns that we only graph. If None then graph all columns
        kind: The type of graph we want. Ex: put 'bar' for a bar graph. If None then is a line graph
        drop: Drop the last n rows. This is if for if the last bits of data shoot out errors.

    Returns:
        a graph object?

    """

    df = load_csv_to_df(csv_path)

    if drop != 0:
        df.drop(df.tail(drop).index, inplace=True)  # drop last n rows

    if ignore_list is not None:
        for i in ignore_list:
            try:
                df.drop(i, axis=1, inplace=True)
            except:
                pass

    graph = df.plot(kind=kind, x=x, y=y, title=title)
    graph.set_xlabel(xlabel)
    graph.set_ylabel(ylabel)

    if show:
        plt.savefig(Path(csv_path).parent / f"Plot {title}.png")
        plt.show()

    return graph

def load_csv_to_df(csv_path):

    if not os.path.exists(csv_path):
        raise FileExistsError(f"{csv_path} does not exist!")

    try:
        df = pd.read_csv(csv_path)  # Load the csv into a dataframe
        return df
    except:
        print(f"Error loading file at {csv_path}.")

    return None

def average_csvs(csv_list):
    """Makes an elementwise average of all the csvs in csv list"""

    dfs = []
    for path in csv_list:
        df = load_csv_to_df(path)
        if df is not None:
            dfs.append(df)

    averages = sum([df.stack() for df in dfs]) / len(dfs)
    averages = averages.unstack()

    return pd.concat(dfs)  # Todo Averaging is broken

def overlapped_csvs(csv_list):
    """Makes plots for each csv in the list then overlaps them."""
    # Todo Not Currently Working


    graphs = []
    for path in csv_list:
        graph = load_csv_to_df(path)
        graphs.append(graph)

    fig = plt.figure()

    for frame in graphs:
        plt.plot(frame, color="blue", alpha=0.5)

    plt.xlim(0, 500)
    plt.ylim(0, 1)
    plt.show()



def make_da_graphs(folder_name, mode=None):

    folder_name = folder_name

    # Set the folder path
    os.chdir(os.path.dirname(sys.argv[0]))  # Change current working directory to wherever dashboard.py is

    if mode == "direct":
        folder_path = Path.cwd() / 'AM_programs' / 'save_data' / folder_name
    else:
        folder_path = Path.cwd() / 'save_data' / folder_name

    print("Folder Path:", folder_path)
    print(os.listdir(folder_path))

    # Patch occupancy
    make_graph_from_csv(Path(folder_path / "patch_occupancy.csv"),
                        kind="line", ignore_list=["Time", "Total Number Occupied"],
                        xlabel="Time", ylabel="Occupancy",
                        title="Patch Occupancy")

    # # Data from Multistrain Run
    # make_graph_from_csv(Path(folder_path / "chance_by_sum.csv"),
    #                     x="Iteration", drop=20,
    #                     kind="line", xlabel="Time", ylabel="Population",
    #                     title="Population and Resources vs time")

    # Make Populuation vs Time with no resources
    make_graph_from_csv(Path(folder_path / "chance_by_sum.csv"),
                        x="Iteration", ignore_list=[" Resources", "Resources"], drop=0,
                        kind="line", xlabel="Time", ylabel="Strain Population",
                        title="Population vs time (No resources)")

    # Make Populuation vs Time with no resources
    make_graph_from_csv(Path(folder_path / "totals.csv"),
                        x="Iteration", ignore_list=["Resources"], drop=0,
                        kind="line", xlabel="Time", ylabel="Strain Population",
                        title="Population vs time (No resources, separated)")

    # Average eq values in multi strain run
    make_graph_from_csv(Path(folder_path/"average_eqs.csv"),
                        kind="bar", x="Sporulation Probability", y="Average Eq Frequency",
                        xlabel="Sporulation Probability", ylabel="Final Eq Frequency",
                        title="Average Equilibrium Frequency (Many strains)")

    make_graph_from_csv(Path(folder_path / "single_strain_averages.csv"),
                        x="Sporulation Probability", y="Average Eq",
                        kind="bar", xlabel="Sporulation Probability", ylabel="Average Equilibrium",
                        title="Single Strain Final Average Equilibrium")


    # Average final eqs for invasion
    make_graph_from_csv(Path(folder_path / "double_strain_averages.csv"),
                        kind="bar", x="Sporulation Probability", y="Average Eq",
                        xlabel="Sporulation Probability", ylabel="Average Equilibrium",
                        title="Average Final Eq Value (Single strain invading 0.3 strategy)")

    # Average final eqs for patch
    make_graph_from_csv(Path(folder_path / "single_strain_patch_freq_averages.csv"),
                        kind="bar", x="Sporulation Probability",
                        xlabel="Sporulation Probability", ylabel="Average Patch Occupancy Freq at Equilibrium",
                        title="Average Patch Occupancy Frequencies at Equilibrium")

    # Average final eqs for patch
    make_graph_from_csv(Path(folder_path / "double_strain_patch_freq_avgs.csv"),
                        kind="bar", x="Sporulation Probability",
                        xlabel="Sporulation Probability", ylabel="Double Strain Average Patch Occupancy",
                        title="Invader Average Patch Occupancy Frequencies at Equilibrium")

    # Final Eq of Single Strain runs
    # make_graph_from_csv(Path(folder_path / "final_eq.csv"),
    #                     x="Sporulation Probability", ignore_list=["id"],
    #                     kind="line", xlabel="Sporulation Probability", ylabel="Average Eq Values",
    #                     title="")

    # Single Strain Curve

def make_patch_occupancy_average(folder_path, filter: str, plotit=True):
    """
    Makes the patch occupancy average csv and plots it

    Args:
        folder_path: Path to the main simulation data folder
        filter: A string that tells what subfolders to include

    Returns:

    """

    paths = []
    l = os.listdir(folder_path)
    l = [f for f in l if filter in l]


    print(l)

    dfs = []
    for f in l:
        dfs.append(pd.read_csv("patch_occupancy.csv"))

    df_concat = pd.concat(dfs)
    by_row_index = df_concat.groupby(df_concat.index)
    df_means = by_row_index.mean()

    plt.plot(df_concat)


if __name__ == "__main__":

    paths = []

    name = "invasion test self loops"

    folder_path = Path.cwd() / 'AM_programs' / 'save_data' / name

    df = pd.read_csv(
        Path(f"{folder_path}/multi strain/0/totals.csv"))
    print(df.head(5))
    df = df.dropna(axis="columns")
    print(df)
    # for folder in os.listdir(folder_path):
    #     csv_list = []
    #     for run in os.listdir(folder_path / folder):
    #         path = folder_path / folder / run
    #         df = pd.read_csv(path /  "chance_by_sum.csv")


    # for i in range(0, 100):
    #     path = folder_path / f"single_spore_curve_{i}" / "patch_occupancy.csv"
    #     if os.path.exists(path):
    #         paths.append(path)
    #
    #
    # df = average_csvs(paths)
    #
    #
    # graph = df.plot(kind="Line", x="Time", title="Average Plot Occupancy Values")
    # graph.set_xlabel("Time")
    # graph.set_ylabel("Average Plot Occupancy Frequency")
    #
    # title = "Patch Occupancy Average"
    # plt.savefig(Path(folder_path).parent / f"Plot {title}.png")
    # plt.show()
    #
    # print("Done")

    # make_da_graphs(name, mode="direct")


