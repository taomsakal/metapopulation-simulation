"""
This file runs many simulations according to some simulation rules and then outputs the graphs
"""

import time
import logging
import numpy as np

import dashboard
import simrules.helpers as helpers
from AM_programs.NStrain import NStrain
from world import World
from main import run
import matplotlib.pyplot as plt


def basic_sim(num_strains, num_loops, name, sc_override=None, save_data=True):
    skip_simulation = False  # If true just display the dashboard but don't run the simulation
    final_eqs = []
    final_pops = []

    # Make random strain probabilities
    # sc = spaced_probs(num_strains)
    sc = sorted(helpers.random_probs(num_strains))
    gc = [0] * num_strains  # Germination Chance
    fvs = [0] * num_strains  # Fly Veg Survival
    fss = [1] * num_strains  # Fly Spore Survival
    if sc_override:
        sc = sc_override

    world = World(NStrain(num_strains, folder_name=name, console_input=False, spore_chance=sc, germ_chance=gc,
                          fly_s_survival=fss,
                          fly_v_survival=fvs, save_data=save_data))

    if not skip_simulation:

        # Run multiple simulations and get average
        for i in range(0, num_loops):
            print(f"Running basic sim {i}/{num_loops}")

            world = World(NStrain(num_strains, folder_name=name, console_input=False, spore_chance=sc, germ_chance=gc,
                                  fly_s_survival=fss,
                                  fly_v_survival=fvs))
            run(world)

            # Make a list of final eq values
            # todo: Put these in the simulation itself
            resources = list(world.rules.sum_populations(world))[0]
            run_pop = list(world.rules.sum_populations(world))[-1]
            run_sum = sum(run_pop)
            try:
                if run_sum != 0:
                    run_strain_eqs = [strain / run_sum for strain in run_pop]  # Calculate the freq of each strain
                    final_eqs.append(run_strain_eqs)  # Append final census total
                    final_pops.append(run_pop)
                else:
                    run_strain_eqs = [0] * world.rules.num_strains
                    final_eqs.append(run_strain_eqs)  # Append final census total
                    final_pops.append(run_pop)
            except:
                logging.warning("Error dealing with an eq value. Skipping.")

    # Find average final eq values
    print("final_eqs:", final_eqs)
    average_eqs = list(np.average(np.array(final_eqs), axis=0))
    average_pops = list(np.average(np.array(final_pops), axis=0))
    print("average eqs:", average_eqs)
    print("average pops:", average_pops)  # todo this is broken?
    helpers.init_csv(world.rules.data_path, "average_eqs.csv", ["Sporulation Probability", "Average Eq Frequency"])
    with open(world.rules.data_path + "/average_eqs.csv", 'a') as f:
        for chance, eq in zip(sc, average_eqs):
            f.write(f"{chance},{eq}\n")

    return [sc, average_eqs, average_pops]


def single_spore_curve(folder_name, resolution, iterations_for_average, save_data=True):
    """
    Makes the curve for a single strain by itself
    Args:
        folder_name:
        resolution: How many times to partition the probability space
        iterations_for_average: How many iterations to do for averaging

    Returns:

    """
    # Make world just so can make path
    world = World(NStrain(1, folder_name=folder_name, console_input=False, spore_chance=[1], germ_chance=[1],
                          fly_s_survival=[1], fly_v_survival=[1], save_data=save_data))

    helpers.init_csv(world.rules.data_path, "single_strain_averages.csv", ["Sporulation Probability", "Average Eq"])

    pops = []
    sc = helpers.spaced_probs(resolution)
    for i, prob in enumerate(sc):
        print(f'\nCalculating Single Spore Curve. Now on spore_prob = {sc[i]}. ({i}/{resolution})')
        returned_sc, avg_eqs, pop_avg = basic_sim(1, iterations_for_average, folder_name + "/single_spore_curve",
                                                  sc_override=[prob], save_data=False)
        pops.append(pop_avg[0])  # Take first index because list isn't flat

    helpers.init_csv(world.rules.data_path, "single_strain_averages.csv", ["Sporulation Probability", "Average Eq"])
    with open(world.rules.data_path + "/single_strain_averages.csv", 'a') as f:
        for chance, eq in zip(sc, pops):
            f.write(f"{chance},{eq}\n")


def double_spore_curve(folder_name, resolution, iterations_for_average):
    """
    Runs the simulation for two strains, one strain fixed.

    Args:
        folder_name:
        resolution: How many times to partition the probability space
        iterations_for_average: How many iterations to do for averaging

    Returns:

    """
    # Make world just so can make path
    world = World(NStrain(1, folder_name=folder_name, console_input=False, spore_chance=[1], germ_chance=[1],
                          fly_s_survival=[1], fly_v_survival=[1], save_data=True))
    helpers.init_csv(world.rules.data_path, "double_strain_averages.csv", ["Sporulation Probability", "Average Eq"])

    eqs = []
    sc = helpers.spaced_probs(resolution)  # The strain we vary
    sc_2 = 0.3  # The strain we hold constant's spore prob

    for i, prob in enumerate(sc):
        print(f'Calculating Double Spore Curve {sc}... {i}/{resolution}')
        returned_sc, avg_eqs, pop_avg = basic_sim(2, iterations_for_average, folder_name + "/double_strain_curve",
                                                  sc_override=[prob, sc_2])
        eqs.append(avg_eqs[0])  # Take first index because list isn't flat

    helpers.init_csv(world.rules.data_path, "double_strain_averages.csv", ["Sporulation Probability", "Average Eq"])
    with open(world.rules.data_path + "/double_strain_averages.csv", 'a') as f:
        for chance, eq in zip(sc, eqs):
            f.write(f"{chance},{eq}\n")


if __name__ == "__main__":
    folder_name = 'Colonization 1000'

    r = 10  # Times to repeat for average
    steps = 20

    print("\nSINGLE SPORE CURVE")
    single_spore_curve(folder_name, steps, r)

    print("\nDOUBLE SPORE CURVE")
    double_spore_curve(folder_name, steps, r)

    # Run i times. Report back
    print("\nBASIC SIM")
    basic_sim(10, r, folder_name)  # Run a basic simulation on n strains and i loops
    #
    # print("Starting Server")
    # dashboard.run_dash_server(folder_name)

    print("Done!")
