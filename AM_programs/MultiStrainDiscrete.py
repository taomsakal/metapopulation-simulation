from collections import defaultdict
import random
from main import run
import networkx as nx
from world import World
import logging
from simrules import helpers
from rules import Rules
import general


class MultiStrainDiscrete(Rules):
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

    def __init__(self, console_input=True):

        super().__init__()

        # Default patch specific parameters
        # (These are passed into the patch, which always uses it's own, meaning we can change these per patch.)
        self.c = 0.2  # Consumption rate for resources.
        self.alpha = 0.2  # Conversion factor for resources into cells
        self.mu_v = 0.1  # Background death rate for vegetative cells
        self.mu_s = 0.05  # Background death rate for sporulated cells
        self.mu_R = 0.01  # "death" rate for resources.
        self.gamma = 10  # Rate of resource renewal
        self.console_input = console_input

        if console_input:
            self.resources = float(input("Initial Resources: "))  # Initial resources, input from user
            self.num_strains = int(input("Number of Strains: "))  # Number of strains to test
        else:
            self.resources = 50
            self.num_strains = 2

        self.spore_chance = []
        self.germ_chance = []
        self.fly_v = []
        self.fly_s = []

        if console_input:
            for i in range(0, self.num_strains):  # Iterates through each strain
                print("Strain " + str(i + 1))
                self.spore_chance.append(float(input("Chance of Sporulation: ")))  # Chance to sporulate
                self.germ_chance.append(float(input("Germination Factor: ")))  # Chance to reactivate from sporulation
                # Chance for vegetative cells to survive fly
                self.fly_v.append(float(input("Vegetative Cell Fly Survival Chance : ")))
                # Chance for sporulated cells to survive fly
                self.fly_s.append(float(input("Sporulated Cell Fly Survival Chance : ")))
        else:
            self.spore_chance = [0.1] * self.num_strains
            self.germ_chance = [0.015] * self.num_strains
            self.fly_v = [0.001] * self.num_strains
            self.fly_s = [0.8] * self.num_strains

        # Global Parameters
        self.dt = 0.01  # Timestep size
        self.worldmap = nx.complete_graph(100)  # The worldmap
        self.prob_death = 0.00004  # Probability of a patch dying.
        self.stop_time = 100000  # Iterations to run
        self.num_flies = 50  # Number of flies each colonization event

        # The number of yeast eaten is a type 2 functional response
        self.fly_attack_rate = 0.3
        self.fly_handling_time = 0.3

        self.drop_single_yeast = False  # If true only pick one survivor to drop, instead of all
        self.yeast_size = 0.01  # Size of a single yeast
        self.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
        # Ie mush all current patches into a pool and redistribute to new patches.

        if console_input:
            self.files = []
            self.total_file = open('save_data/gen_totals.csv', 'a+')

    def set_initial_conditions(self, world):
        """ Give half the patches each strain. """
        initial_v = []
        initial_s = []

        if self.console_input:
            for i in range(0, self.num_strains):  # Iterate through each strain
                # Initial Vegetative Cells
                initial_v.append(float(input("Initial Vegetative Cells of Strain " + str(i + 1) + ": ")))
                # Initial Sporulated Cells
                initial_s.append(float(input("Initial Sporulated Cells of Strain " + str(i + 1) + ": ")))
        else:
            for i in range(0, self.num_strains):
                initial_v.append(5)
                initial_s.append(5)

        for patch in world.patches:  # Iterate through each patch
            rand_strain = random.randrange(0, self.num_strains)  # Randomly select a strain
            # Fill the patch with a single strain
            patch.v_populations[rand_strain] = initial_v[rand_strain]
            patch.s_populations[rand_strain] = initial_s[rand_strain]

        # Prepare an array of save files for each patch
        if self.console_input:
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
        patch.germ_chance = self.germ_chance
        patch.fly_v = self.fly_v
        patch.fly_s = self.fly_s
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

            if self.drop_single_yeast:
                num_eaten = 1
                # todo: does having this before survival-probabilities effect the simulation?

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
                        if random.random() < self.fly_v[j]:
                            v_survivors[j] += self.yeast_size
                    else:
                        patch.s_populations[j-self.num_strains] -= self.yeast_size
                        if random.random() < self.fly_s[j-self.num_strains]:
                            s_survivors[j-self.num_strains] += self.yeast_size

                # Add the survivors to a random neighboring patch.
                # If no neighbors then the fly vanishes
                drop_patch = patch.random_neighbor()
                if drop_patch is not None:
                    drop_patch.v_populations = [x+y for x, y in zip(drop_patch.v_populations, v_survivors)]
                    drop_patch.s_populations = [x+y for x, y in zip(drop_patch.s_populations, s_survivors)]

    def kill_patches(self, world):
        """ Resets population on a patch to 0 with probability prob_death """

        # Kill ALL the patches
        for patch in world.patches:
            if random.random() < self.prob_death:
                self.reset_patch(patch)

    def census(self, world):

        print("\n")
        print("=" * 30)

        v_population_totals = [0] * self.num_strains
        s_population_totals = [0] * self.num_strains
        total_resources = 0

        # Gather for totals from each patch
        for patch in world.patches:
            for i in range(0, self.num_strains):
                v_population_totals[i] += patch.v_populations[i]
                s_population_totals[i] += patch.s_populations[i]
            total_resources += patch.resources

        print("\nIndividual Patch Info")
        for patch in world.patches:
            print(f"Patch {patch.id}")
            print(f"    Vegetative Population: {str(patch.v_populations)}")
            print(f"    Sporulated Population: {str(patch.s_populations)}")
            print(f"    Resources: {patch.resources}")

            # Write to individual patch save files
            if self.console_input:
                for i in range(0, self.num_strains):
                    self.files[patch.id].write(str(patch.v_populations[i]) + ',' + str(patch.s_populations[i]) + ',')
                self.files[patch.id].write(str(patch.resources) + '\n')

        print(f"\nGEN {world.age} TOTALS: {str(v_population_totals) + str(s_population_totals) + str(total_resources)}")

        # Write to gen_totals save file
        if self.console_input:
            for i in range(0, self.num_strains):
                self.total_file.write(str(v_population_totals[i]) + ',' + str(s_population_totals[i]) + ',')
            self.total_file.write(str(total_resources) + '\n')

    def stop_condition(self, world):
        return world.age > self.stop_time


if __name__ == "__main__":
    run(World(MultiStrainDiscrete(True)))
