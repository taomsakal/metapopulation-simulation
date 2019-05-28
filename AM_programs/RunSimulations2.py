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
import networkx as nx


WORLDMAP = nx.complete_graph(1200)
VAL1 = None  # Parameter to iterate over
VAL2 = None

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
    elif len(sc) <= 1:
        logging.warning(f"The sporulation chance vector is {sc}.")

    for i in range(0, num_loops):
        print(f"Running basic sim {i}/{num_loops}")

        world = World(NStrain(num_strains, folder_name=Path(name) / str(i), replicate_number=i, worldmap=WORLDMAP,
                              spore_chance=sc,
                              germ_chance=gc,
                              fly_s_survival=fss,
                              fly_v_survival=fvs))

        world.rules.prob_death = VAL1
        world.rules.colonization_prob_slope = VAL2
        run(world)

    return world



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
        multiple_sims(1, iterations_for_average, Path(folder_name) / f"single_spore_curve_{i}",
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
    sc_2 = 0.4  # The strain we hold constant's spore prob

    for i, prob in enumerate(sc):
        print(f'Calculating Double Spore Curve {sc}... {i}/{resolution}')
        multiple_sims(2, iterations_for_average, Path(folder_name) / f"double_strain_curve_{i}",
                      sc_override=[prob, sc_2])

def sanity_check():
    """
    This iterates through many simulations of two strains with the exact same parameters.
    We should find that they on average have 50% patch occupancy. Otherwise something is wrong.
    This function just runs the simulations.
    """
    # Same param test
    for i in range(2, 8):  # Avoid doing test for 0 and 1 because both strains go extinct and this messes up the results.
        for j in range(1, 15):
            print(f"Running sanity test. (Make sure same strain does the same) {i}-{j}")
            prob=helpers.spaced_probs(9)[i]
            world = World(NStrain(2, folder_name=Path("SanityTest") / f"{i}-{j}", replicate_number=j, worldmap=WORLDMAP,
                                  spore_chance=[prob, prob],
                                  germ_chance=[0, 0],
                                  fly_s_survival=[.8, .8],
                                  fly_v_survival=[.2, .2]))

            from main import run  # For some reason I need this a second time?
            run(world)




if __name__ == "__main__":



    # for val1 in [0, .01, .02, .1, .2, .3, .5, .8, .99, 1]:  # patch death
    #     for val2 in [0, .01, .1, .2, .5, 1, 2, 5]:
    #
    #         VAL1 = val1
    #         VAL2 = val2
    #
    #         folder_name = Path("patch death x col prob") / f'{val1}x{val2}'
    #
    #         r = 5  # Times to repeat for average
    #         steps = 20
    #         num_strains = 12  # Number of strains for the multiple strain run
    #
    #         print("\nSINGLE SPORE CURVE")
    #         single_spore_curve(folder_name, steps, r)
    #
    #         print("\nDOUBLE SPORE CURVE")
    #         double_spore_curve(folder_name, steps, r)
    #
    #         # Run i times. Report back
    #         print("\nMULTI STRAIN SIM")
    #         world = multiple_sims(num_strains, r, Path(folder_name) / "multi strain")
    #         # sc_override=[.1, .4, .6, .9])  # Run a basic simulation on n strains and r loops
    #
    #         print(world.rules.num_strains)
    #
    #         # Special invasion test
    #         # multiple_sims(2, 3, Path(folder_name) / "special invasion test", sc_override=[.3, .3])
    #
    #         print("Done! Graphing...")
    #
    sanity_check()