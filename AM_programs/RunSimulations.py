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


def basic_sim(num_strains, num_loops, name, sc_override=None, save_data=True):
    skip_simulation = False  # If true just display the dashboard but don't run the simulation
    final_eqs = []
    final_pops = []
    final_patch_freqs = []

    # Make random strain probabilities
    # sc = spaced_probs(num_strains)
    sc = sorted(helpers.spaced_probs(num_strains))
    gc = [0] * num_strains  # Germination Chance
    fvs = [0.2] * num_strains  # Fly Veg Survival
    fss = [.8] * num_strains  # Fly Spore Survival
    if sc_override:
        sc = sc_override

    world = World(NStrain(num_strains, folder_name=name, console_input=False, spore_chance=sc, germ_chance=gc,
                          fly_s_survival=fss,
                          fly_v_survival=fvs, save_data=save_data))

    if not skip_simulation:

        # Run multiple simulations and get average
        for i in range(0, num_loops):
            print(f"Running basic sim {i}/{num_loops}")

            world = World(NStrain(num_strains, folder_name=Path(name) / str(i), console_input=False,
                                  spore_chance=sc,
                                  germ_chance=gc,
                                  fly_s_survival=fss,
                                  fly_v_survival=fvs))
            run(world)

            # Make a list of final eq values
            resources = list(world.rules.sum_populations(world))[0]
            run_pop = list(world.rules.sum_populations(world))[-1]
            run_sum = sum(run_pop)
            try:
                if run_sum != 0:
                    run_strain_eqs = [strain / run_sum for strain in run_pop]  # Calculate the freq of each strain
                    final_eqs.append(run_strain_eqs)  # Append final census total
                    final_pops.append(run_pop)
                    final_patch_freqs.append(world.rules.measure_patch_frequency(world))
                else:
                    run_strain_eqs = [0] * world.rules.num_strains
                    final_eqs.append(run_strain_eqs)  # Append final census total
                    final_pops.append(run_pop)
                    final_patch_freqs.append(world.rules.measure_patch_frequency(world))
            except:
                logging.warning("Error dealing with an eq value. Skipping.")

    # Find average final eq values
    average_eqs = list(np.average(np.array(final_eqs), axis=0))
    average_pops = list(np.average(np.array(final_pops), axis=0))
    average_patch_freqs = list(np.average(np.array(final_patch_freqs), axis=0))
    print("averg patch freqs", average_patch_freqs)

    # Save the data
    helpers.init_csv(world.rules.data_path, "average_eqs.csv", ["Sporulation Probability", "Average Eq Frequency"])
    with open(world.rules.data_path + "/average_eqs.csv", 'a') as f:
        for chance, eq in zip(sc, average_eqs):
            f.write(f"{chance},{eq}\n")

    helpers.init_csv(world.rules.data_path, "average_patch_freq_eq.csv",
                     [f"Patch Occupancy Strain {i}" for i in range(0, num_strains)])
    with open(world.rules.data_path + "/average_patch_freq_eq.csv", 'a') as f:
        for chance, eq in zip(sc, [average_patch_freqs]):
            f.write(f"{chance},")
            for strain in eq:
                f.write(f"{strain},")
            f.write("\n")

    return [sc, average_eqs, average_pops, average_patch_freqs]


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
    patch_freqs = []
    sc = helpers.spaced_probs(resolution)
    for i, prob in enumerate(sc):
        print(f'\nCalculating Single Spore Curve. Now on spore_prob = {sc[i]}. ({i}/{resolution})')
        returned_sc, avg_eqs, pop_avg, patch_freq_avg = basic_sim(1, iterations_for_average, folder_name + f"/single_spore_curve_{i}",
                                                  sc_override=[prob], save_data=False)
        pops.append(pop_avg[0])  # Take first index because list isn't flat
        pops.append(patch_freq_avg[0])
        print("patch freq avg", patch_freq_avg)
        patch_freqs.append(patch_freq_avg[0])
    print("Patch freqs", patch_freqs)



    helpers.init_csv(world.rules.data_path, "single_strain_averages.csv", ["Sporulation Probability", "Average Eq"])
    with open(world.rules.data_path + "/single_strain_averages.csv", 'a') as f:
        for chance, eq in zip(sc, pops):
            f.write(f"{chance},{eq}\n")

    helpers.init_csv(world.rules.data_path, "single_strain_patch_freq_averages.csv", ["Sporulation Probability"] +
                     [f"Patch Occupancy Strain {i}" for i in range(0, world.rules.num_strains)])
    with open(world.rules.data_path + "/single_strain_patch_freq_averages.csv", 'a') as f:
        for chance, eq in zip(sc, patch_freqs):
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
    # Make world just so can make path  # Todo this is inelegant and leads to errors about strain number in csv. Fix
    world = World(NStrain(2, folder_name=folder_name, console_input=False, spore_chance=[1], germ_chance=[1],
                          fly_s_survival=[1], fly_v_survival=[1], save_data=True))
    helpers.init_csv(world.rules.data_path, "double_strain_averages.csv", ["Sporulation Probability", "Average Eq"])

    eqs = []
    patch_freqs = []
    sc = helpers.spaced_probs(resolution)  # The strain we vary
    sc_2 = 0.5  # The strain we hold constant's spore prob

    for i, prob in enumerate(sc):
        print(f'Calculating Double Spore Curve {sc}... {i}/{resolution}')
        returned_sc, avg_eqs, pop_avg, patch_freq = basic_sim(2, iterations_for_average, folder_name + f"/double_strain_curve_{i}",
                                                  sc_override=[prob, sc_2])
        eqs.append(avg_eqs[0])  # Take first index because list isn't flat
        patch_freqs.append(patch_freq)

    print("patch freqs", patch_freqs)

    helpers.init_csv(world.rules.data_path, "double_strain_averages.csv", ["Sporulation Probability", "Average Eq"])
    with open(world.rules.data_path + "/double_strain_averages.csv", 'a') as f:
        for chance, eq in zip(sc, eqs):
            f.write(f"{chance},{eq}\n")

    helpers.init_csv(world.rules.data_path, "double_strain_patch_freq_avgs.csv",
                     ["Sporulation Probability"] +
                     [f"Patch Occupancy Strain {i}" for i in range(0, world.rules.num_strains)])
    with open(world.rules.data_path + "/double_strain_patch_freq_avgs.csv", 'a') as f:
        for chance, eq in zip(sc, patch_freqs):
            f.write(f"{chance},")
            for strain in eq:
                f.write(f"{strain},")
            f.write("\n")


if __name__ == "__main__":
    folder_name = 'invasion test 2'

    r = 3  # Times to repeat for average
    steps = 10

    print("\nSINGLE SPORE CURVE")
    single_spore_curve(folder_name, steps, r)

    print("\nDOUBLE SPORE CURVE")
    double_spore_curve(folder_name, steps, r)

    # Run i times. Report back
    print("\nBASIC SIM")
    basic_sim(10, r, folder_name)  # Run a basic simulation on n strains and r loops

    print("Done! Graphing...")
    time.sleep(1)

    import data_analysis
    data_analysis.make_da_graphs(folder_name)
