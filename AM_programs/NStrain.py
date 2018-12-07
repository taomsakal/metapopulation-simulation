#!/usr/bin/env pypy

from collections import defaultdict
import random
import os
from main import run
import networkx as nx
from world import World
import logging
import time
import numpy as np
from simrules import helpers
from rules import Rules
import dashboard



class NStrain(Rules):
    """
    This is a discrete version of the main ODE model.
    It has the competitor and colonizer, both which have vegetative and sporulated cells.

    Each population consists of the following dictionary
    populations = {
        'kv': integer number of cells
        'rv': integer "  "
        'ks': integer "  "
        'rs': integer "  "
        }

    Where k → competitor, c → colonizer, v → vegatative, and s → sporulated.
    """

    def __init__(self, num_strains, console_input=False, spore_chance=None, germ_chance=None,
                 fly_v_survival=None, fly_s_survival=None, folder_name=None, save_data=True):
        """
        Creates a discrete multi-strain simulation. The individuals each have two states (sporulated/vegetative) but
        there can be an arbitrary number of strains.

        Args:
            num_strains: The number of strains
            console_input: If true then put in all parameters via console manually. Good for small, one off runs.
            spore_chance: A vector of the form [x1, x2, ..., xn] where xi is the chance of sporulation of strain i.
            germ_chance: A vector like spore_chance except for germination chance.
            fly_s_survival: A vector like above but for fly survival chance for sporulated cells
            fly_v_survival: A vector like above but for fly survival chance of vegetative cells
            folder_name: Name of the folder where we store all the data. This is by default in the data folder.
                        If none then the console will ask for input.
        """

        super().__init__()
        self.console_input = console_input

        # Default patch specific parameters
        # (These are passed into the patch, which always uses it's own, meaning we can change these per patch.)
        logging.info("Setting default patch parameters")
        self.c = 0.2  # Consumption rate for init_resources_per_patch.
        self.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
        self.mu_v = 0.1  # Background death rate for vegetative cells
        self.mu_s = 0.05  # Background death rate for sporulated cells
        self.mu_R = 0.01  # "death" rate for init_resources_per_patch.
        self.gamma = 10  # Rate of resource renewal
        self.num_strains = num_strains
        self.init_resources_per_patch = 0.5  # Initial resource value for each patch

        # Variables that will be overwritten
        self.spore_chance = []  # Chance of sporulation for each strain
        self.germ_chance = []  # Chance of germination for each strain
        self.fly_v_survival = []  # Chance of veg cell survival for each strain
        self.fly_s_survival = []  # Chance for sporulated cell survival for each strain

        self.s_population_totals = []
        self.v_population_totals = []
        self.total_resources = 0
        self.all_population_totals = []  # The current population totals across all patches.
        self.total_pop = 0

        # todo move to bottom and init.

        self.save_patch_data = False  # If we save patch by patch data too. This can eat up a lot of storage space.
        self.save_data = save_data  # If to save any data at all

        if console_input:
            logging.info("Getting user input for parameter values")
        else:
            logging.info("Skipping user input and using vectors for parameter values")
            self.spore_chance = spore_chance
            self.germ_chance = germ_chance
            self.fly_s_survival = fly_s_survival
            self.fly_v_survival = fly_v_survival



        # Global Parameters
        self.dt = 0.5  # Timestep size
        self.worldmap = nx.complete_graph(20)  # The worldmap
        self.prob_death = 0.004  # Probability of a patch dying.
        self.stop_time = 2000  # Iterations to run
        self.data_save_step = 40 # Save the data every this many generations
        self.num_flies = 3  # Number of flies each colonization event
        self.fly_stomach_size = 1  # Number of cells they each. Put in "type 2" for a type 2 functional response
        self.germinate_on_drop = True  #If true then sporulated cells germinate immediatly when they are dropped.

        # Change these params if the number of yeast eaten is a type 2 functional response
        self.fly_attack_rate = 0.3
        self.fly_handling_time = 0.3

        self.yeast_size = 0.01  # Size of a single yeast
        self.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
        # Ie mush all current patches into a pool and redistribute to new patches.

        self.files = []

        if folder_name is None:
            self.data_path = input("What shall we name the data folder for this simulation?")
        else:
            self.data_path = folder_name
        if save_data:
            # Create the data files
            self.data_path = f'save_data/{self.data_path}'

            # Make the main totals file
            self.total_file = helpers.init_csv(self.data_path, "totals.csv",
                                               ["Iteration", "Resources"] + [f"Strain {i} (Veg), Strain {i} (Spore)" for i in range(0, num_strains)])
            # Make another totals file that compares sporulation chance to
            self.chance_by_sum_file = helpers.init_csv(self.data_path, "chance_by_sum.csv",
                                                       ["Iteration, Resources"] + [f"Strain {i}" for i in range(0, num_strains)] + ["Frequency"])

            # todo close the files at the end


    def safety_checks(self, world):
        """
        Checks to make sure nothing greatly concerning is going on in terms of parameters. If not fails an assertion.
        """

        logging.info("Checking that all parameters have legal values.")
        assert self.num_strains > 0 and isinstance(self.num_strains, int)
        assert self.check_param_lists([self.spore_chance, self.germ_chance, self.fly_v_survival, self.fly_s_survival])

        # Make sure there are populations to begin with
        if world.age == 0:
            for patch in world.patches:
                assert sum(patch.v_populations) > 0
                assert sum(patch.s_populations) > 0

    def ask_for_input(self, num_strains):
        """Asks for the parameter input instead of reading the default"""

        self.init_resources_per_patch = float(
            input("Initial Resources: "))  # Initial init_resources_per_patch, input from user
        self.num_strains = int(input("Number of Strains (overwrites given number): "))  # Number of strains to test
        for i in range(0, self.num_strains):  # Iterates through each strain
            self.spore_chance.append(float(input("Chance of Sporulation: ")))  # Chance to sporulate
            self.germ_chance.append(float(input("Germination Factor: ")))  # Chance to reactivate from sporulation
            # Chance for vegetative cells to survive fly
            self.fly_v_survival.append(float(input("Vegetative Cell Fly Survival Chance : ")))
            # Chance for sporulated cells to survive fly
            self.fly_s_survival.append(float(input("Sporulated Cell Fly Survival Chance : ")))

    def set_initial_conditions(self, world):
        """
        For each patch give a random strain.
        """
        initial_v = []
        initial_s = []

        # decide on initial cells for each strain
        if self.console_input:
            for i in range(0, self.num_strains):  # Iterate through each strain
                # Initial Vegetative Cells
                initial_v.append(float(input("Initial Vegetative Cells of Strain " + str(i + 1) + ": ")))
                # Initial Vegetative Cells
                initial_s.append(float(input("Initial Sporulated Cells of Strain " + str(i + 1) + ": ")))
        else:
            # todo: for now just give each strain an intial number of one
            initial_s = [1] * self.num_strains
            initial_v = [1] * self.num_strains

        # Give each patch a strain
        for i, patch in enumerate(world.patches):  # Iterate through each patch
            strain = i % world.rules.num_strains
            # Fill the patch with a single strain
            patch.v_populations[strain] += initial_v[strain]
            patch.s_populations[strain] += initial_s[strain]

        # Prepare an array of save files for each patch
        # todo: move this line to a better location
        for patch in world.patches:
            self.files.append(open('save_data/patch_' + str(patch.id) + '.csv', 'a+'))

        self.sum_populations(world)

    def reset_patch(self, patch):
        """
        Each patch starts with 0 of all individuals, unless changed by initial_conditions
        and a resource level of 0.
        """

        # Set all populations to
        patch.v_populations = [0] * self.num_strains
        patch.s_populations = [0] * self.num_strains

        # Reset patch parameters
        patch.c = self.c
        patch.alpha = self.alpha
        patch.mu_v = self.mu_v
        patch.mu_s = self.mu_s
        patch.mu_R = self.mu_R
        patch.gamma = self.gamma
        patch.resources = self.init_resources_per_patch
        patch.germ_chance = self.germ_chance  # todo: see if we need these values or if they mess with stuff
        patch.fly_v = self.fly_v_survival
        patch.fly_s = self.fly_s_survival
        patch.spore_chance = self.spore_chance

        # print(f"Patch {patch.id} has been reset.")

    def patch_update(self, patch):
        """
        Each individual has fitness of resource_level and reproduces by that amount.
        """

        r_change = patch.gamma - patch.mu_R * patch.resources  # Constant init_resources_per_patch, death proportional to population

        for i in range(0, self.num_strains):  # Iterate through strains of patch

            # Vegetative cell change
            # (new veg)*(prop remaining veg) - (dead veg) + (germinated spores)
            v_change = (patch.alpha * patch.c * patch.resources * patch.v_populations[i]) * (1 - self.spore_chance[i]) \
                       - (patch.mu_v * patch.v_populations[i]) + (self.germ_chance[i] * patch.resources * patch.s_populations[i])

            # Sporulated cell change
            # (birth from resource consumption)*(prop spores) - (spore death) - (germinated spores)
            s_change = (patch.alpha * patch.c * patch.resources * patch.v_populations[i]) * (self.spore_chance[i]) \
                       - (patch.mu_s * patch.s_populations[i]) - (self.germ_chance[i] * patch.resources * patch.s_populations[i])

            r_change -= patch.c * patch.resources * patch.v_populations[i]  # Resource change -= eaten init_resources_per_patch


            # Add population changes
            patch.v_populations[i] += v_change * self.dt
            patch.s_populations[i] += s_change * self.dt

        patch.resources += r_change * self.dt  # Add resource changes

        # Make sure none become negative
        for i in range(0, self.num_strains):
            if patch.v_populations[i] < 0:
                patch.v_populations[i] = 0
            if patch.s_populations[i] < 0:
                patch.s_populations[i] = 0

        if patch.resources < 0:
            patch.resources = 0

    def colonize(self, world):
        """
        In this function fly_num flies pick up fly_size yeast cells at random from a patch.
        Each cell has a chance of surviving based off it's fly survival probability.
        The fly then chooses a random neighbor patch to deposit the yeast cells onto.

        Warnings:
            The fly doesn't actually remove the yeast cells from the patch when it eats them.
            We assume the fly eats few cells compared to the total number.
        """

        for i in range(0, self.num_flies):

            patch = random.choice(world.patches)  # Pick the random patch that the fly lands on

            # Determine number of cells eaten
            if self.fly_stomach_size == "type 2":
                num_eaten = int(helpers.typeIIresponse(sum(patch.s_populations) + sum(patch.v_populations),
                                                   self.fly_attack_rate, self.fly_handling_time))
            elif self.fly_stomach_size >= 0:
                num_eaten = self.fly_stomach_size

            # print(f"num_eaten for patch {patch.id}: {num_eaten}")
            # If actually eat any yeast, then see which survive and drop into new neighboring patch.
            if num_eaten > 0:

                try:
                    # Select the types of cells to be eaten
                    hitchhikers = random.choices(range(0, 2 * self.num_strains), patch.v_populations + patch.s_populations,
                                                 k=num_eaten)  # todo: This is probably broken because the populations can sneak into small negative numbers
                except IndexError:
                    if sum(patch.v_populations) > 0:
                        raise Exception(
                            f"Cannot choose {num_eaten} hitchikers out of {self.num_strains} strains in patch {patch.id} with population "
                            f"{patch.v_populations + patch.s_populations}")
                    else:
                        logging.info(f"Patch {patch.id} is empty, the fly dies a slow death of starvation...")
                        hitchhikers = {}

                # print(patch.populations)
                # print(hitchhikers)
                v_survivors = [0] * self.num_strains
                s_survivors = [0] * self.num_strains
                # Remove the cell from the population. For each cell, check if it survives. If so, place it in survivors
                for j in hitchhikers:
                    if j < self.num_strains:
                        patch.v_populations[j] -= self.yeast_size
                        if random.random() < self.fly_v_survival[j]:
                            v_survivors[j] += self.yeast_size
                    else:
                        patch.s_populations[j - self.num_strains] -= self.yeast_size
                        if random.random() < self.fly_s_survival[j - self.num_strains]:
                            s_survivors[j - self.num_strains] += self.yeast_size

                # Add the survivors to a random neighboring patch.
                # If no neighbors then the fly vanishes
                drop_patch = patch.random_neighbor()
                if drop_patch is not None:
                    drop_patch.v_populations = [x + y for x, y in zip(drop_patch.v_populations, v_survivors)]
                    # if spore cells germinate on the drop then add them directly to the veg populations
                    if self.germinate_on_drop:
                        drop_patch.v_populations = [x + y for x, y in zip(drop_patch.s_populations, s_survivors)]
                    else:
                        drop_patch.s_populations = [x + y for x, y in zip(drop_patch.s_populations, s_survivors)]

    def kill_patches(self, world):
        """ Resets population on a patch to 0 with probability prob_death """

        # Kill ALL the patches
        for patch in world.patches:
            if random.random() < self.prob_death:
                self.reset_patch(patch)

    def sum_populations(self, world):
        """
        Sums the populations for all the patches to give a final number.
        Also sets the number for the entire simulation

        Args:
            world: The world

        Returns:
            A tuple (#init_resources_per_patch, #veg, #spore, #total)

        """

        # Reset the global counts
        self.v_population_totals = [0] * self.num_strains
        self.s_population_totals = [0] * self.num_strains
        self.all_population_totals = [0] * self.num_strains
        self.total_resources = 0

        # Gather for totals from each patch
        for patch in world.patches:
            self.total_resources += patch.resources
            for i in range(0, self.num_strains):
                self.v_population_totals[i] += patch.v_populations[i]
                self.s_population_totals[i] += patch.s_populations[i]
                self.all_population_totals[i] += patch.v_populations[i] + patch.s_populations[i]

        self.total_pop = sum(self.all_population_totals)

        return (self.total_resources, self.v_population_totals, self.s_population_totals, self.all_population_totals)

    def census(self, world):

        self.safety_checks(world)

        logging.info("Censusing and saving data")
        total_resources, v_population_totals, s_population_totals, final_totals = self.sum_populations(world)

        # print("\nIndividual Patch Info")
        # for patch in world.patches:
        #     print(f"Patch {patch.id}")
        #     print(f"    Vegetative Population: {str(patch.v_populations)}")
        #     print(f"    Sporulated Population: {str(patch.s_populations)}")
        #     print(f"    Resources: {patch.init_resources_per_patch}")

        # Write to individual patch save files
        if self.save_patch_data:
            for patch in world.patches:
                self.files[patch.id].write(f"{world.age}, {str(patch.init_resources_per_patch)}")
                for i in range(0, self.num_strains):
                    self.files[patch.id].write(str(patch.v_populations[i]) + ',' + str(patch.s_populations[i]) + ',')

        if self.save_data:
            # Open closed data files
            if self.chance_by_sum_file.closed:
                # print("Opening chance by sum file")
                self.chance_by_sum_file = open(f'{self.data_path}/chance_by_sum.csv', 'a')
            if self.total_file.closed:
                # print("Opening totals file")
                self.total_file = open(f'{self.data_path}/totals.csv', 'a')

            # Update the data files every n'th step
            if world.age % self.data_save_step == 0:
                self.update_chance_by_sum_csv(world, total_resources, v_population_totals, s_population_totals)
                self.update_totals_csv(world, total_resources, v_population_totals, s_population_totals)

        # Print current progress.
        # print(f"\nGEN {world.age}/{self.stop_time}\nTOTALS: "
              # f"\n    Veg: {str(v_population_totals)}"
              # f"\n    Spore:{str(s_population_totals)}"
              # f"\n    Resources: {str(total_resources)}"
              # )

    def stop_condition(self, world):
        if world.age > self.stop_time:
            self.last_things(world)
            return True
        elif sum(world.rules.sum_populations(world)[-1]) == 0:
            logging.warning(f"Population went extinct at gen {world.age}! Ending Simulation!")
            return True
        else:
            return False

    def last_things(self, world):
        """
        Last steps before exiting the simulation.
        """

        self.sum_populations(world)

        # Make a csv with final equilibrium
        helpers.init_csv(self.data_path, "final_eq.csv", ["id", "Sporulation Probability", "Total Population", "Veg Population", "Spore Population", "Frequency"])
        with open(f'{self.data_path}/final_eq.csv', 'a') as final_eq:
            for i in range(0, self.num_strains):
                final_eq.write(
                    f"{i},{self.spore_chance[i]},{self.all_population_totals[i]},{self.v_population_totals[i]},{self.s_population_totals[i]},")
                self.write_frequency(world, i)
                final_eq.write("\n")

    def write_frequency(self, world, n):
        "Writes a line with the frequency of the strain n"
        try:
            self.chance_by_sum_file.write(f"{(self.v_population_totals[n] + self.s_population_totals[n]) / self.total_pop},")
        except ZeroDivisionError:
            logging.warning("Population went extinct!")
            self.chance_by_sum_file.write("-404,")  # -404 is out numeric symbol for went extinct. Ie species not found.
        except IndexError:
            logging.error(f"Something crazy happened. We have population index {n} unable to be found in {self.v_population_totals}, or {self.s_population_totals}")

    # Todo: Is possible for all to go extinct and there to be problems calculating frequency because of division by zero
    def update_chance_by_sum_csv(self, world, total_resources, v_population_totals, s_population_totals):
        """ Updates the chance by sum csv """
        # Write to totals save file
        self.chance_by_sum_file.write(f"{world.age},")
        self.chance_by_sum_file.write(str(total_resources) + ",")
        for i in range(0, self.num_strains):
            self.chance_by_sum_file.write(f"{v_population_totals[i] + s_population_totals[i]},")
        total_pop = sum([v_population_totals[i] + s_population_totals[i] for i in range(len(v_population_totals))])
        self.write_frequency(world, 0)
        self.chance_by_sum_file.write("\n")

    def update_totals_csv(self, world, total_resources, v_population_totals, s_population_totals):
        """ Updates the totals csv"""
        # Write to totals save file
        self.total_file.write(str(world.age) + ",")
        self.total_file.write(str(total_resources) + ",")
        for i in range(0, self.num_strains):
            self.total_file.write(str(v_population_totals[i]) + ',' + str(s_population_totals[i]) + ',')
        self.total_file.write("\n")

def basic_sim(num_strains, num_loops, name, sc_override=None, save_data=True):


    skip_simulation = False  # If true just display the dashboard but don't run the simulation
    final_eqs = []
    final_pops = []

    # Make random strain probabilities
    # sc = spaced_probs(num_strains)
    sc = sorted(helpers.random_probs(num_strains))
    # sc = [0.35, 0.5, 0.8]
    gc = [0] * num_strains  # Germination Chance
    fvs = [.2] * num_strains  # Fly Veg Survival
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
            # print(f"The probability vectors are...\n{sc}\n{gc}\n{fvs}\n{fss}")

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
                    run_strain_eqs = [strain / run_sum for strain in run_pop]
                    final_eqs.append(run_strain_eqs)  # Append final census total
                    final_pops.append(run_pop)
                else:
                    run_strain_eqs = [0]*world.rules.num_strains
                    final_eqs.append(run_strain_eqs)  # Append final census total
                    final_pops.append(run_pop)
            except:
                logging.warning("Error dealing with an eq value. Skipping.")

            # print('runpop', run_pop)
            # print('runsum', run_sum)
            # print('run_strain_eqs', run_strain_eqs)


    # Find average final eq values
    print(final_eqs)
    average_eqs = list(np.average(np.array(final_eqs), axis=0))
    average_pops = list(np.average(np.array(final_pops), axis=0))
    print('average eqs', average_eqs)
    print('average pops', average_pops)  # todo this is broken?
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
                                  fly_s_survival=[1],fly_v_survival=[1], save_data=save_data))

    helpers.init_csv(world.rules.data_path, "single_strain_averages.csv", ["Sporulation Probability", "Average Eq"])

    pops = []
    sc = helpers.spaced_probs(resolution)
    for i, prob in enumerate(sc):
        print(f'Calculating Single Spore Curve {sc}... {i}/{resolution}')
        returned_sc, avg_eqs, pop_avg = basic_sim(1, iterations_for_average, folder_name+"/single_spore_curve", sc_override=[prob], save_data=False)
        pops.append(pop_avg[0])  # Take first intext because list isn't flat

    #avg_pops = sum(pops)/len(pops)
    #print('avg pops for 1 strain', avg_pops)
    helpers.init_csv(world.rules.data_path, "single_strain_averages.csv", ["Sporulation Probability", "Average Eq"])
    with open(world.rules.data_path + "/single_strain_averages.csv", 'a') as f:
        for chance, eq in zip(sc, pops):
            f.write(f"{chance},{eq}\n")

def double_spore_curve(folder_name, resolution, iterations_for_average):
    """

    Args:
        folder_name:
        resolution: How many times to partition the probability space
        iterations_for_average: How many iterations to do for averaging

    Returns:

    """
    # Make world just so can make path
    world = World(NStrain(1, folder_name=folder_name, console_input=False, spore_chance=[1], germ_chance=[1],
                          fly_s_survival=[1], fly_v_survival=[1]))
    helpers.init_csv(world.rules.data_path, "double_strain_averages.csv", ["Sporulation Probability", "Average Eq"])

    eqs = []
    sc = helpers.spaced_probs(resolution)  # The strain we vary
    sc_2 = 0.3  # The strain we hold constant's spore prob
    coexistences = []
    for i, prob in enumerate(sc):
        print(f'Calculating Single Spore Curve {sc}... {i}/{resolution}')
        # Run the Simulation
        returned_sc, avg_eqs, pop_avg = basic_sim(2, iterations_for_average, folder_name + "/double_strain_curve",
                                                  sc_override=[prob, sc_2])
        eqs.append(avg_eqs[0])  # Take first intext because list isn't flat

    helpers.init_csv(world.rules.data_path, "double_strain_averages.csv", ["Sporulation Probability", "Average Eq"])
    with open(world.rules.data_path + "/double_strain_averages.csv", 'a') as f:
        for chance, eq in zip(sc, eqs):
            f.write(f"{chance},{eq}\n")

#todo: node that the frequency of all strains should be equal if there is only one.

if __name__ == "__main__":

    folder_name = 'test'


    print("\nSINGLE SPORE CURVE")
    single_spore_curve(folder_name, 10, 2)  #todo: for some reason this overwrites the single non-looped data

    print("\nDOUBLE SPORE CURVE")
    double_spore_curve(folder_name, 10, 2)

    # Run i times. Report back
    print("\nBASIC SIM")
    basic_sim(3, 2, folder_name)  # Run a basic simulation on n strains and i loops


    time.sleep(2)
    print("Starting Server")
    dashboard.run_dash_server(folder_name)

    # todo Get dashboard working by itself so can explore old data







