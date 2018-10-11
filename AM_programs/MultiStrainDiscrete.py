from collections import defaultdict
import random
import os
from main import run
import networkx as nx
from world import World
import logging
from simrules import helpers
from rules import Rules
import general


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

    def __init__(self, num_strains, console_input=True, spore_chance="manual", germ_chance="manual", fly_v="manual",
                 fly_v_survival="manual", fly_s_survival="manual"):
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
        """

        super().__init__()
        self.console_input = console_input

        # Default patch specific parameters
        # (These are passed into the patch, which always uses it's own, meaning we can change these per patch.)
        logging.info("Setting default patch parameters")
        self.c = 0.2  # Consumption rate for resources.
        self.alpha = 0.2  # Conversion factor for resources into cells
        self.mu_v = 0.1  # Background death rate for vegetative cells
        self.mu_s = 0.05  # Background death rate for sporulated cells
        self.mu_R = 0.01  # "death" rate for resources.
        self.gamma = 10  # Rate of resource renewal
        self.num_strains = num_strains
        self.resources = 0.5  # Initial resource value for each patch

        self.spore_chance = []  # Chance of sporulation for each strain
        self.germ_chance = []  # Chance of germination for each strain
        self.fly_v_survival = []  # Chance of veg cell survival for each strain
        self.fly_s_survival = []  # Chance for sporulated cell survival for each strain

        self.save_patch_data = False  # If we save patch by patch data too. This can eat up a lot of storage space.

        if console_input:
            logging.info("Getting user input for parameter values")
        else:
            logging.info("Skipping user input and using vectors for parameter values")
            self.spore_chance = spore_chance
            self.germ_chance = germ_chance
            self.fly_s_survival = fly_s_survival
            self.fly_v_survival = fly_v_survival

        logging.info("Checking that all parameters have legal values.")
        self.check_param_lists([spore_chance, germ_chance, fly_v_survival, fly_s_survival])

        # Global Parameters
        self.dt = 0.01  # Timestep size
        self.worldmap = nx.complete_graph(100)  # The worldmap
        self.prob_death = 0.00004  # Probability of a patch dying.
        self.stop_time = 50  # Iterations to run
        self.num_flies = 50  # Number of flies each colonization event


        # The number of yeast eaten is a type 2 functional response
        self.fly_attack_rate = 0.3
        self.fly_handling_time = 0.3

        self.drop_single_yeast = False  # If true only pick one survivor to drop, instead of all (todo: "True" not implemented)
        self.yeast_size = 0.01  # Size of a single yeast
        self.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
        # Ie mush all current patches into a pool and redistribute to new patches.

        self.files = []


        # Create the data files
        self.data_path = input("What shall we name the data folder for this simulation?")
        self.data_path = f'save_data/{self.data_path}'

        # Make the main totals file
        self.total_file = self.init_csv(self.data_path, "totals.csv", [f"{i} Veg, {i} Spore," for i in range(0, num_strains)])
        # Make another totals file that compares sporulation chance to
        self.chance_by_sum_file = self.init_csv(self.data_path, "chance_by_sum.csv", [f"{i}," for i in spore_chance])



        # todo close the files at the end




    def ask_for_input(self, num_strains):
        """Asks for the parameter input instead of reading the default"""

        self.resources = float(input("Initial Resources: "))  # Initial resources, input from user
        self.num_strains = int(input("Number of Strains (overwrites given number): "))  # Number of strains to test
        for i in range(0, self.num_strains):  # Iterates through each strain
            print("Strain " + str(i + 1))
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
            initial_s = [1]*self.num_strains
            initial_v = [1]*self.num_strains

        # Give each patch n random strains
        for i, patch in enumerate(world.patches):  # Iterate through each patch
            # rand_strain = i
            for i in range(0, random.randrange(0, 20)):
                rand_strain = random.randrange(0, self.num_strains)  # Randomly select a strain
                # Fill the patch with a single strain
                patch.v_populations[rand_strain] += initial_v[rand_strain]
                patch.s_populations[rand_strain] += initial_s[rand_strain]

        # Prepare an array of save files for each patch
        # todo: move this line to a better location
        for patch in world.patches:
            self.files.append(open('save_data/patch_' + str(patch.id) + '.csv', 'a+'))

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
        patch.resources = self.resources
        patch.germ_chance = self.germ_chance  # todo: see if we need these values or if they mess with stuff
        patch.fly_v = self.fly_v_survival
        patch.fly_s = self.fly_s_survival
        patch.spore_chance = self.spore_chance

        print(f"Patch {patch.id} has been reset.")

    def patch_update(self, patch):
        """
        Each individual has fitness of resource_level and reproduces by that amount.
        """

        r_change = patch.gamma - patch.mu_R * patch.resources  # Constant resources, death proportional to population

        for i in range(0, self.num_strains):  # Iterate through strains of patch
            # Vegetative cell change = birth from resource consumption not spored - death rate + germinated spores
            v_change = patch.alpha * patch.c * patch.resources * patch.v_populations[i] * (1 - self.spore_chance[i]) - \
                       patch.mu_v * patch.v_populations[i] + self.germ_chance[i] * patch.resources * \
                       patch.s_populations[i]
            # Sporulated cells = birth from resource consumption spored - death rate - germinated spores
            s_change = patch.alpha * patch.c * patch.resources * patch.v_populations[i] * self.spore_chance[i] - \
                       patch.mu_s * patch.s_populations[i] - self.germ_chance[i] * patch.resources * \
                       patch.s_populations[i]
            r_change -= patch.c * patch.resources * patch.v_populations[i]  # Resource change -= eaten resources
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
            num_eaten = int(helpers.typeIIresponse(sum(patch.s_populations) + sum(patch.v_populations),
                                                   self.fly_attack_rate, self.fly_handling_time))

            # print(f"num_eaten for patch {patch.id}: {num_eaten}")

            # If actually eat any yeast, then see which survive and drop into new neighboring patch.
            if num_eaten > 0:

                try:
                    # Select the types of cells to be eaten
                    hitchhikers = random.choices(range(2 * self.num_strains), patch.v_populations + patch.s_populations,
                                                 k=num_eaten)
                except IndexError:
                    if sum(patch.populations) > 0:
                        raise Exception(
                            f"Cannot choose hitchikers in patch {patch.id} with population "
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
                    if self.drop_single_yeast:
                        # Randomly choose only one survivor to drop
                        #todo
                        random.randint(0, self.num_strains)  # Choose random strain to keep
                    drop_patch.v_populations = [x + y for x, y in zip(drop_patch.v_populations, v_survivors)]
                    drop_patch.s_populations = [x + y for x, y in zip(drop_patch.s_populations, s_survivors)]

    def kill_patches(self, world):
        """ Resets population on a patch to 0 with probability prob_death """

        # Kill ALL the patches
        for patch in world.patches:
            if random.random() < self.prob_death:
                self.reset_patch(patch)

    def census(self, world):

        logging.info("Censusing and saving data")

        v_population_totals = [0] * self.num_strains
        s_population_totals = [0] * self.num_strains
        total_resources = 0

        # Gather for totals from each patch
        for patch in world.patches:
            total_resources += patch.resources
            for i in range(0, self.num_strains):
                v_population_totals[i] += patch.v_populations[i]
                s_population_totals[i] += patch.s_populations[i]

        # print("\nIndividual Patch Info")
        # for patch in world.patches:
        #     print(f"Patch {patch.id}")
        #     print(f"    Vegetative Population: {str(patch.v_populations)}")
        #     print(f"    Sporulated Population: {str(patch.s_populations)}")
        #     print(f"    Resources: {patch.resources}")

            # Write to individual patch save files
            if self.save_patch_data:
                self.files[patch.id].write(f"{world.age}, {str(patch.resources)}")
                for i in range(0, self.num_strains):
                    self.files[patch.id].write(str(patch.v_populations[i]) + ',' + str(patch.s_populations[i]) + ',')

        if self.chance_by_sum_file.closed:
            print("Opening chance by sum file")
            self.chance_by_sum_file = open(f'{self.data_path}/chance_by_sum.csv', 'a')
        if self.total_file.closed:
            print("Opening totals file")
            self.total_file = open(f'{self.data_path}/totals.csv', 'a')
        self.update_chance_by_sum_csv(world, total_resources, v_population_totals, s_population_totals)
        self.update_totals_csv(world, total_resources, v_population_totals, s_population_totals)

        #Open the files until the end of the program




        print(f"\nGEN {world.age}/{self.stop_time}\nTOTALS: "
              # f"\n    Veg: {str(v_population_totals)}"
              # f"\n    Spore:{str(s_population_totals)}"
              # f"\n    Resources: {str(total_resources)}"
              )



    def stop_condition(self, world):
        if world.age > self.stop_time:
            self.last_things(world)
            return True
        else:
            return False

    def last_things(self, world):
        """
        Last steps before exiting the simulation.
        """

        # Gather for totals from each patch
        v_population_totals = [0] * self.num_strains
        s_population_totals = [0] * self.num_strains
        total_resources = 0
        for patch in world.patches:
            total_resources += patch.resources
            for i in range(0, self.num_strains):
                v_population_totals[i] += patch.v_populations[i]
                s_population_totals[i] += patch.s_populations[i]

        # Make a csv with final equilibrium
        self.init_csv(self.data_path, "final_eq.csv", ["k,", "Population,", "V pop,", "S pop,"])
        with open(f'{self.data_path}/final_eq.csv', 'a') as final_eq:
            for i in range(0, num_strains):
                final_eq.write(", ,")
                final_eq.write(f"{self.spore_chance[i]},")
                final_eq.write(f"{v_population_totals[i] + s_population_totals[i]}, {v_population_totals[i]}, {s_population_totals[i]}")
                final_eq.write("\n")






    def init_csv(self, path, name, header):
        """
        creates a csv file with the header we specify.
        Automatically adds an iteration and resources column.

        Args:
            path: location of file
            name: <filename>.csv
            header: list of strings to write in the header
        """

        # todo

        # Make the Directory if needed
        if not os.path.exists(path):
            logging.info(f"Initializing the save data files in {self.data_path}")
            os.makedirs(path)

        with open(f'{self.data_path}/{name}', 'w+') as file:

            # Make the headers of the CSV file
            file.write("Iteration, Resources,")
            for i in header:
                file.write(i)
            file.write("\n")

        return file

    def update_chance_by_sum_csv(self, world, total_resources, v_population_totals, s_population_totals):
        # Write to totals save file
        self.chance_by_sum_file.write(str(world.age) + ",")
        self.chance_by_sum_file.write(str(total_resources) + ",")
        for i in range(0, self.num_strains):
            self.chance_by_sum_file.write(f"{v_population_totals[i] + s_population_totals[i]},")
        self.chance_by_sum_file.write("\n")

    def update_totals_csv(self, world, total_resources, v_population_totals, s_population_totals):
        # Write to totals save file
        self.total_file.write(str(world.age) + ",")
        self.total_file.write(str(total_resources) + ",")
        for i in range(0, self.num_strains):
            self.total_file.write(str(v_population_totals[i]) + ',' + str(s_population_totals[i]) + ',')
        self.total_file.write("\n")


def random_probs(n):
    """
    Makes a list of random probabilities. Used to give input for large
    Args:
        n: number of strains

    Returns:
        A list of random probabilities length n
    """

    return [random.random() for x in range(0, n)]

def spaced_probs(n):
    """
    Makes a vector for the n strains with evenly spaced probabilities between them.
    Args:
        n:
        step:

    Returns:

    """

    l = []
    for i in range(0, n):
        l.append(i/n)  # Normalize so that between 0 and one

    return l

if __name__ == "__main__":

    # Make random strain probabilities

    num_strains = 1000
    #sc = spaced_probs(num_strains)
    sc = sorted(random_probs(num_strains))
    gc = [1]*num_strains
    fvs = [.2]*num_strains
    fss = [.8]*num_strains
    print(f"The probability vectors are...\n{sc}\n{gc}\n{fvs}\n{fss}")

    run(World(NStrain(num_strains, console_input=False, spore_chance=sc, germ_chance=gc, fly_s_survival=fss, fly_v_survival=fvs)))


