#!/usr/bin/env pypy

from collections import defaultdict
import random
import csv
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

    def __init__(self, num_strains, run_name=None, console_input=False, spore_chance=None, germ_chance=None,
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
            run_name: Name of the specific simulation run
        """

        super().__init__()
        self.console_input = console_input
        self.run_name = run_name

        # Default patch specific parameters
        # These are passed into the patch, which always uses it's own, meaning we can change these per patch.
        # For example, we can make some patches more dangerous than others.
        logging.info("Setting default patch parameters")
        self.c = 0.2  # Consumption rate for init_resources_per_patch.
        self.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
        self.mu_v = 0.1  # Background death rate for vegetative cells
        self.mu_s = 0.05  # Background death rate for sporulated cells
        self.mu_R = 0.01  # "death" rate for init_resources_per_patch.
        self.gamma = 1  # Rate of resource renewal
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
        self.worldmap = nx.complete_graph(50)  # The worldmap
        self.prob_death = 0.004  # Probability of a patch dying.
        self.stop_time = 2000  # Iterations to run
        self.data_save_step = 1  # Save the data every this many generations

        # Colonization Mode
        self.colonize_mode = 'probabilities'  # 'fly' or 'probabilities'
        self.colonization_prob_slope =1/1000  # Total weighted number of yeast times this is the prob that a patch is colonized

        # Fly Params
        self.num_flies = 3  # Number of flies each colonization event
        self.fly_stomach_size = 1  # Number of cells they each. Put in "type 2" for a type 2 functional response
        self.germinate_on_drop = True  # If true then sporulated cells germinate immediatly when they are dropped.

        # Update Params
        self.update_mode = 'eq'  # 'discrete' or 'eq'. See the update function for details
        self.patch_update_iterations = 1  # How many times to repeat the update function

        # Change these params if the number of yeast eaten is a type 2 functional response
        self.fly_attack_rate = 0.3
        self.fly_handling_time = 0.3

        self.yeast_size = 0.001  # Size of a single yeast
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
                                               ["Iteration", "Resources"] + [f"Strain {i} (Veg), Strain {i} (Spore)" for
                                                                             i in range(0, num_strains)])
            # Make another totals file that compares sporulation chance to
            self.chance_by_sum_file = helpers.init_csv(self.data_path, "chance_by_sum.csv",
                                                       ["Iteration, Resources"] + [f"Strain {i}" for i in
                                                                                   range(0, num_strains)] + [
                                                           "Frequency"])




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

        if self.num_strains > 1:
            for i in range(1, self.num_strains):
                try:
                    assert self.spore_chance[i-1] <= self.spore_chance[i]  # If fails then direct jump to eq update type won't work because it assumes they are ordered
                except:
                    Exception(f"Our sporulation chances are not ordered correctly. Specifically {self.spore_chance[i-1]} is not less than {self.spore_chance[i]} \n" +
                              f"The spore chance vector is {self.spore_chance}")

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
            # todo: for now just give each strain an intial number
            initial_s = [self.yeast_size] * self.num_strains
            initial_v = [self.yeast_size] * self.num_strains

        # Give each patch a strain
        for i, patch in enumerate(world.patches):  # Iterate through each patch
            strain = i % world.rules.num_strains
            # Fill the patch with a single strain
            patch.v_populations[strain] += initial_v[strain]
            patch.s_populations[strain] += initial_s[strain]

        # Prepare an array of save files for each patch
        # todo: move this line to a better location
        if self.save_patch_data:
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
        patch.germ_chance = self.germ_chance
        patch.fly_v = self.fly_v_survival
        patch.fly_s = self.fly_s_survival
        patch.spore_chance = self.spore_chance

        # print(f"Patch {patch.id} has been reset.")

    def patch_update(self, patch):
        """
        Each individual has fitness of resource_level and reproduces by that amount.

        There are two types of of patch update. Discrete does a basic discrete stepwise model to calculate the
        the next timestep. The size of the steps is controlled through the parameter dt.

        Eq uses previously calculated values of each patch equlibrium and brings the patch to exactly that value.
        """

        mode = self.update_mode

        if mode == 'discrete':
            for i in range(0, self.patch_update_iterations):

                r_change = patch.gamma - patch.mu_R * patch.resources  # Constant init_resources_per_patch, death proportional to population

                for i in range(0, self.num_strains):  # Iterate through strains of patch

                    # Vegetative cell change
                    # (new veg)*(prop remaining veg) - (dead veg) + (germinated spores)
                    v_change = (patch.alpha * patch.c * patch.resources * patch.v_populations[i]) * (
                                1 - self.spore_chance[i]) \
                               - (patch.mu_v * patch.v_populations[i]) + (
                                           self.germ_chance[i] * patch.resources * patch.s_populations[i])

                    # Sporulated cell change
                    # (birth from resource consumption)*(prop spores) - (spore death) - (germinated spores)
                    s_change = (patch.alpha * patch.c * patch.resources * patch.v_populations[i]) * (
                    self.spore_chance[i]) \
                               - (patch.mu_s * patch.s_populations[i]) - (
                                           self.germ_chance[i] * patch.resources * patch.s_populations[i])

                    r_change -= patch.c * patch.resources * patch.v_populations[
                        i]  # Resource change -= eaten init_resources_per_patch

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

        # If calculating via equilibrium values, set all strains in each patch to be the eq value we calculated
        # outside of the program.
        elif mode == 'eq':
            self.jump_to_eq_update(patch)

        else:
            raise Exception(f"{type} is not a valid update mode.")

    def jump_to_eq_update(self, patch):
        """
        This jumps a patch directly to the calculated equilibrium.

        Args:
            patch: The patch to set to eq

        """

        i = helpers.find_winner(patch.v_populations, patch.s_populations)  # This is the index of the best competitor

        # Set all strains to be extinct
        patch.v_populations = [0]*self.num_strains
        patch.s_populations = [0]*self.num_strains


        if i == "no winner":
            patch.resources = patch.gamma / patch.mu_R
            return

        # Sporulation chance of winner
        s = self.spore_chance[i]


        # Set winning strain to eq
        patch.v_populations[i] = ((patch.c * patch.alpha * patch.gamma) * (1 - s) - patch.mu_R * patch.mu_v) / (patch.c * patch.mu_v)
        if s != 1:
            patch.s_populations[i] = (s * (
                    (patch.c * patch.alpha * patch.gamma) * (s - 1)) + patch.mu_R*patch.mu_v) / ((s - 1)*(patch.c * patch.mu_s))

            patch.resources = -patch.mu_v / ((s - 1) * patch.alpha * patch.c)
        # Special case: If spore chance is 1 then just make the numerator real small
        else:
            patch.s_populations[i] = (s * (
                    (patch.c * patch.alpha * patch.gamma) * (s - 1)) + patch.mu_R*patch.mu_v) / ((.999999 - 1) * (patch.c * patch.mu_s))

            patch.resources = -patch.mu_v / ((.999999 - 1) * patch.alpha * patch.c)



    def colonize(self, world):
        """The colonize function switches between a couple modes."""

        if self.colonize_mode == 'fly':
            self.colonize_fly_mode(world)
        elif self.colonize_mode == 'probabilities':
            self.probability_colonize_mode(world)
        else:
            raise ValueError(f"{self.colonize_mode} is not a valid colonization mode. (Choose 'fly' or 'probabilities'")

    def colonize_fly_mode(self, world):
        """
        In this function fly_num flies pick up fly_size yeast cells at random from a patch.
        Each cell has a chance of surviving based off it's fly survival probability.
        The fly then chooses a random neighbor patch to deposit the yeast cells onto.

        Warnings:
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

            # If actually eat any yeast, then see which survive and drop into new neighboring patch.
            if num_eaten > 0:
                try:
                    # Filter zeros out of patch populations
                    patch_pops = patch.v_populations + patch.s_populations
                    patch_pops = [x if x > 0 else 0 for x in patch_pops]
                    # Select the types of cells to be eaten
                    hitchhikers = random.choices(range(0, 2 * self.num_strains), weights=patch_pops,
                                                 k=num_eaten)
                except IndexError:
                    if sum(patch.v_populations) > 0:
                        raise Exception(
                            f"Cannot choose {num_eaten} hitchikers out of {self.num_strains} strains in patch {patch.id} with population "
                            f"{patch.v_populations + patch.s_populations}")
                    else:
                        logging.info(f"Patch {patch.id} is empty, the fly dies a slow sad death of starvation...")
                        hitchhikers = {}

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

    def probability_colonize_mode(self, world):
        """
        This mode goes through each patch and flips a coin to see if a colonizer lands on it.
        The more surviviable colonizers between all patches the more likely it is to be colonized.

        Args:
            world: The world

        Returns:
            None
        """

        propagules = self.sum_populations(world)
        veg = propagules[1]
        spores = propagules[2]

        # Make sure no negatives in veg and spores. If any set to 0.
        veg = [v if v >= 0 else 0 for v in veg]
        spores = [s if s >= 0 else 0 for s in spores]

        # Weight each entry by Strainpop * Survival chance
        weighted_veg = [a * b for a, b in zip(veg, self.fly_v_survival)]
        weighted_spore = [a * b for a, b in zip(spores, self.fly_s_survival)]
        weights = weighted_veg + weighted_spore
        weighted_sum = sum(weights)

        for patch in world.patches:
            if self.colonization_prob(weighted_sum):
                colonist = random.choices(range(0, self.num_strains*2), weights=weights, k=1)[0]
                if colonist > self.num_strains - 1:  # If index says is a spore
                    patch.s_populations[colonist - self.num_strains] += self.yeast_size
                else:  # Otherwise must be a veg cell
                    patch.v_populations[colonist] += self.yeast_size


    def colonization_prob(self, n):

        prob = n * self.colonization_prob_slope

        if prob > 1:
            prob = 1

        if random.random() < prob:
            return True
        else:
            return False


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

        if world.age % 100 == 0:
            print("    Veg, Spore, Resource:", round(sum(v_population_totals), 3), round(sum(s_population_totals), 3), round(total_resources, 3))

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


        if self.save_data:
            # Make a csv with final equilibrium
            helpers.init_csv(self.data_path, "final_eq.csv",
                             ["id", "Sporulation Probability", "Total Population", "Veg Population", "Spore Population",
                              "Frequency"])
            with open(f'{self.data_path}/final_eq.csv', 'a') as final_eq:
                for i in range(0, self.num_strains):
                    final_eq.write(
                        f"{i},{self.spore_chance[i]},{self.all_population_totals[i]},{self.v_population_totals[i]},{self.s_population_totals[i]},")
                    self.write_frequency(world, i)
                    final_eq.write("\n")

            with open(f"{self.data_path}/params.txt", "a") as txt:
                txt.write(f"\nCurrent Parameters for {self.run_name}")
                for d in self.__dict__.items():
                    txt.write("    " + d[0] + ':' + str(d[1]) + "\n")


            self.chance_by_sum_file.close()
            self.total_file.close()

        # self.print_params(world)

    def write_frequency(self, world, n):
        "Writes a line with the frequency of the strain n"
        try:
            self.chance_by_sum_file.write(
                f"{(self.v_population_totals[n] + self.s_population_totals[n]) / self.total_pop},")
        except ZeroDivisionError:
            logging.warning("Population went extinct!")
            self.chance_by_sum_file.write("-404,")  # -404 is out numeric symbol for went extinct. Species not found.
        except IndexError:
            logging.error(
                f"Something crazy happened. We have population index {n} unable to be found in {self.v_population_totals}, or {self.s_population_totals}")

    def update_chance_by_sum_csv(self, world, total_resources, v_population_totals, s_population_totals):
        """ Updates the chance by sum csv """
        # Write to totals save file
        self.chance_by_sum_file.write(f"{world.age},")
        self.chance_by_sum_file.write(str(total_resources) + ",")
        for i in range(0, self.num_strains):
            self.chance_by_sum_file.write(f"{v_population_totals[i] + s_population_totals[i]},")
        # total_pop = sum([v_population_totals[i] + s_population_totals[i] for i in range(len(v_population_totals))])
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

if __name__ == "__main__":

    pass