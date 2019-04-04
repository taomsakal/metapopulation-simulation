"""
This file runs many simulations according to some simulation rules and then outputs the graphs
"""

import time
import logging
import numpy as np

from pathlib import Path
import dashboard
import simrules.helpers as helpers
from AM_programs.NStrain import NStrain
from world import World
from main import run
import matplotlib.pyplot as plt


def multiple_sims(num_strains, num_loops, name, sc_override=None, save_data=True):
    """
    Runs a simulation multiple times, saving it in the following folder structure:
        name/run number
    Each run number folder will have one run of the multiple sim. We can then take those and average them
    or whatever else we nat.


    Args:
        num_strains: Number of strains
        num_loops: Number of times to run.
        name: Folder name
        sc_override: Put in a vector to overide sporulation chance. Otherwise each strain is given a value so the are
        spaced out equally. (Ex if 5 strains the vector would be [0, .25, .5, .75, .9999])
        save_data: If true then saves the csv data.

    Returns:

    """
    # Make random strain probabilities
    # sc = spaced_probs(num_strains)
    sc = sorted(helpers.spaced_probs(num_strains))
    gc = [0] * num_strains  # Germination Chance
    fvs = [0] * num_strains  # Fly Veg Survival
    fss = [1] * num_strains  # Fly Spore Survival
    if sc_override:
        sc = sc_override

    for i in range(0, num_loops):
        print(f"Running basic sim {i}/{num_loops}")

        world = World(NStrain(num_strains, folder_name=Path(name) / str(i), console_input=False,
                              spore_chance=sc,
                              germ_chance=gc,
                              fly_s_survival=fss,
                              fly_v_survival=fvs))
        run(world)



def single_spore_curve(folder_name, resolution, iterations_for_average, save_data=True):
    """
    Makes the curve for a single strain by itself
    Args:
        resolution: How many times to partition the probability space
        iterations_for_average: How many iterations to do for averaging

    Returns:

    """
    sc = helpers.spaced_probs(resolution)
    for i, prob in enumerate(sc):
        print(f'\nCalculating Single Spore Curve. Now on spore_prob = {sc[i]}. ({i}/{resolution})')
        multiple_sims(1, iterations_for_average, folder_name + f"/single_spore_curve_{i}",
                      sc_override=[prob], save_data=False)


def double_spore_curve(folder_name, resolution, iterations_for_average):
    """
    Runs the simulation for two strains, one strain fixed.

    Args:
        folder_name:
        resolution: How many times to partition the probability space
        iterations_for_average: How many iterations to do for averaging

    Returns:

    """
    sc = helpers.spaced_probs(resolution)  # The strain we vary
    sc_2 = 0.5  # The strain we hold constant's spore prob

    for i, prob in enumerate(sc):
        print(f'Calculating Double Spore Curve {sc}... {i}/{resolution}')
        multiple_sims(2, iterations_for_average, folder_name + f"/double_strain_curve_{i}",
                      sc_override=[prob, sc_2])




if __name__ == "__main__":
    folder_name = 'invasion test new data saver'

    r = 2  # Times to repeat for average
    steps = 10
    num_strains = 10 # Number of strains for the multiple strain run

    print("\nSINGLE SPORE CURVE")
    single_spore_curve(folder_name, steps, r)

    print("\nDOUBLE SPORE CURVE")
    double_spore_curve(folder_name, steps, r)

    # Run i times. Report back
    print("\nMULTI STRAIN SIM")
    multiple_sims(num_strains, r, Path(folder_name) / "multi strain")  # Run a basic simulation on n strains and r loops

    # print("Done! Graphing...")

    # import data_analysis
    # data_analysis.make_da_graphs(folder_name)
