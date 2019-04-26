import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from simrules import helpers



def load_csv_to_df(csv_path):
    """Returns a dataframe of the csv"""

    if not os.path.exists(csv_path):
        raise FileExistsError(f"{csv_path} does not exist!")

    try:
        df = pd.read_csv(csv_path)  # Load the csv into a dataframe
        # df = df.dropna(axis="columns")
        return df
    except:
        print(f"Error loading file at {csv_path}.")

    return None

def concat_dataframes(file_name, folder_path):

    # Make list of dataframes
    for folder in os.listdir(folder_path):
        df_list = []
        for run in os.listdir(folder_path):
            path = folder_path / run
            df = load_csv_to_df(path / file_name)
            df_list.append(df)

    return pd.concat(df_list)

def meta_concat_dataframes(folder_prefix, file_name, folder_path):
    """Concatanates dataframes across multiple replicate runs of the simulation.
    This is for making invasion curves.
    Ex if folder_prefix is double_strain_curve_ then it will concat all dataframes
    from folders that start with the prefix."""

    valid_folders = []
    for folder in os.listdir(folder_path):
        if folder_prefix in str(folder):
            print("added!")
            valid_folders.append(folder)

    dfs = []
    for folder in valid_folders:
        file_name = Path(file_name)
        df = concat_dataframes(file_name, folder_path / folder)
        dfs.append(df)

    print("Dfs:", dfs)
    df = pd.concat(dfs)
    print("df:", df)

    return df

def strain_pop(df, title=None):
    """Makes a graph of strain population"""

    # Look at only one entry for each timestep. Don't think we need this but putting it in just in case.
    df = df[df.Type == "Both"]

    sns.relplot(x="Iteration", y="Population",
                data=df, kind="line", legend="full", hue="Strain Number")#.set_title("Strain Population")
    plt.show()


def global_patch_occupancy_curve(df, title=None):
    """Makes the global patch occupancy curve"""

    # Look at only one entry for each timestep. Don't think we need this but putting it in just in case.
    # df = df[df.Type == "Both"]
    df = df[df["Strain Number"] == 0]

    sns.relplot(x="Iteration", y="Global Patch Occupancy",
                data=df, kind="line", style="Type")
    plt.show()

def strain_patch_occupancy_curve(df, title=None):
    """Makes a patch occupancy curve seperated by strains"""

    # df = df[df.Type == "Both"]
    sns.lineplot(x="Iteration", y="Patch Occupancy of Strain", data=df, legend="full",
                hue="Strain Number", style="Type").set_title("Strain Patch Occupancy")
    plt.show()

def eq_values(df, title=None):

    sns.lineplot(x="Sporulation Chance", y="Patch Occupancy of Strain",
                data=df)#.set_title("Final Eq Values")
    plt.show()


if __name__ == "__main__":
    # sns.set()
    # tips = sns.load_dataset("tips")
    # sns.relplot(x="total_bill", y="tip", col="time",
    #             hue="smoker", style="smoker", size="size",
    #             data=tips)

    paths = []

    name = "testy testy"

    sns.set()

    path = Path.cwd() / 'AM_programs' / 'save_data' / Path(name)
    totals_df = concat_dataframes("totals.csv", path / "multi strain")
    print(totals_df["Strain Number"])

    print("Calculating patch occupancy curves")
    # strain_patch_occupancy_curve(totals_df)
    # global_patch_occupancy_curve(totals_df)
    strain_pop(totals_df)

    print("Making final eq dataframes...")
    eqs_df_double = meta_concat_dataframes("double_strain_curve_", "final_eq.csv", path)
    eqs_df_single = meta_concat_dataframes("single_strain_curve_", "final_eq.csv", path)
    eqs_multi = concat_dataframes("final_eq.csv", path / "multi strain")

    print("Calculating final eq values...")
    # eq_values(eqs_multi)
    print(eqs_df_double)
    eq_values(eqs_df_double)
    eq_values(eqs_df_single)

    print("DONE")



