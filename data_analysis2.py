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
            valid_folders.append(folder)

    dfs = []
    for folder in valid_folders:
        file_name = Path(file_name)
        df = concat_dataframes(file_name, folder_path / folder)
        dfs.append(df)
    dfs = pd.concat(dfs)

    return dfs

def strain_pop(df, path, name):
    """Makes a graph of strain population"""
    plot, ax = plt.subplots()
    # Look at only one entry for each timestep. Don't think we need this but putting it in just in case.
    df = df[df.Type == "Both"]

    sns.relplot(x="Iteration", y="Population",
                data=df, kind="line", legend="full", hue="Strain Number")#.set_title("Strain Population")
    plt.tight_layout()

    # plt.show()

    ax.set_title(name)
    plot.savefig(path / f"{name}.png")


def global_patch_occupancy_curve(df, path, name):
    """Makes the global patch occupancy curve"""
    plot, ax = plt.subplots()
    # Look at only one entry for each timestep. Don't think we need this but putting it in just in case.
    df = df[df.Type == "Both"]
    # df = df[df["Strain Number"] == 0]

    sns.relplot(x="Iteration", y="Global Patch Occupancy",
                data=df, kind="line")

    # plt.tight_layout()
    # plt.show()

    ax.set_title(name)
    plot.savefig(path / f"{name}.png")

def strain_patch_occupancy_curve(df, path, name):
    """Makes a patch occupancy curve seperated by strains"""
    plot, ax = plt.subplots()
    df = df[df.Type == "Both"]
    sns.lineplot(x="Iteration", y="Patch Occupancy of Strain", data=df, legend="full",
                hue="Strain Number")
    # plt.tight_layout()
    # plt.show()

    ax.set_title(name)
    plot.savefig(path / f"{name}.png")

def eq_values(df, path, name):
    plot, ax= plt.subplots()
    sns.barplot(x="Sporulation Chance", y="Patch Occupancy of Strain", color="b",
                data=df)

    # plot.savefig("Final Eq Averages")
    # plt.tight_layout()
    # plt.show()

    ax.set_title(name)
    plot.savefig(path / f"{name}.png")

def double_strain_plot(df, path, name):
    f, ax = plt.subplots()

    # Plot the crashes where alcohol was involved
    sns.set_color_codes("pastel")
    sns.barplot(x="Sporulation Chance", y="Global Patch Occupancy", data=df[df["Strain Number"] == 0],
                label="Global Patch Occupancy", color="b")
    #
    # Plot the total crashes
    sns.set_color_codes("muted")
    sns.barplot(x="Sporulation Chance", y="Patch Occupancy of Strain", data=df[df["Strain Number"]==0],
                label="Resident", color="b")



    # Add a legend and informative axis label
    ax.legend(ncol=2, loc="lower right", frameon=True)
    ax.set(ylabel="Patch Occupancy",
           xlabel="Double Strain Curve")
    sns.despine(left=True, bottom=True)

    ax.set_title(name)
    f.savefig(path / f"{name}.png")
    # plt.show()

if __name__ == "__main__":
    # sns.set()
    # tips = sns.load_dataset("tips")
    # sns.relplot(x="total_bill", y="tip", col="time",
    #             hue="smoker", style="smoker", size="size",
    #             data=tips)

    paths = []

    name = "patch death x col prob"
    # name = "Lookup Table Run"
    # name = "SanityTest"

    sns.set()

    path1 = Path.cwd() / 'AM_programs' / 'save_data' / Path(name)


    # data =[]
    # for folder in os.listdir(path):
    #     print(f"Adding {folder}")
    #     data.append(load_csv_to_df(path/ folder / "final_eq.csv"))
    # data = pd.concat(data)
    #
    # print(data)
    # data.to_csv(path / "SanityTest.csv")

    for folder in os.listdir(path1):
        try:
            path = Path(path1) / folder

            print(f"\nMAKING GRAPHS FOR {folder}")

            totals_df = concat_dataframes("totals.csv", path / "multi strain")
            #
            print("Calculating patch occupancy curves")
            strain_patch_occupancy_curve(totals_df, path, f"Patch occupancy (multi strain) {folder}")
            global_patch_occupancy_curve(totals_df, path, f"Global patch occupancy (multi strain) {folder}")
            # strain_pop(totals_df)

            print("Making double strain curve...")
            eqs_df_double = meta_concat_dataframes("double_strain_curve_", "final_eq.csv", path)
            double_strain_plot(eqs_df_double, path, f"Patch occupancy (two strains) {folder}")

            print("Calculating final eq values...")
            eqs_multi = concat_dataframes("final_eq.csv", path / "multi strain")
            eq_values(eqs_multi, path, f"Average Patch Occupancy eqs (multi strain) {folder}")

            # Single strain curve
            eqs_df_single = meta_concat_dataframes("single_spore_curve_", "final_eq.csv", path)
            eq_values(eqs_df_single, path, f"Average Patch occupancy eqs (single strain) {folder}")


            print("DONE")
        except:
            print(f"folder {folder} failed")



