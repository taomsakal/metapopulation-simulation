from collections import defaultdict
import random
from main import run
import networkx as nx
import logging
from simrules import helpers
from rules import Rules


class SimpleCompetitionColonization(Rules):
    """
    A simple competition colonization model. There are two strains and possibilities:
        1. A patch has both types
        2. A patch has one type
    Patches go to an equilibrium, then a fly comes, grabs n random cells, and distributes them.
    """

    def __init__(self):

        super().__init__()
        self.worldmap = nx.complete_graph(14)  # The worldmap
        self.prob_death = 0.05  # Probability of a patch dying.
        self.stop_time = 1000  # Iterations to run

        self.num_flies = 10  # Number of flies each colonization event
        self.eqboth = (50, 200)  # Final values when both the competitor and colonizer are in the patch
        self.eqr = (300, 0)  # ... when only colonizer
        self.eqk = (0, 250)  # ... when only competitor

        self.death_prob_r = 0.8  # Probability of colonizer surviving fly gut
        self.death_prob_v = 0.2  # Probability of competitor surviving fly gut

        self.fly_size = 10  # How many yeast cells one fly takes

        self.reset_all_on_colonize = True

    def set_initial_conditions(self, world):
        """ Start with two patches, one of only competitors and one of colonizers. """
        populations = world.patches[0].populations
        populations['rv'] = 100
        populations['kv'] = 100

    def reset_patch(self, patch):
        """
        Each patch starts with 0 of all individuals, unless changed by initial_conditions
        and a random resource value from resource_value.
        """

        patch.populations = {'rv': 0, 'kv': 0}
        print(f"Patch {patch.id} has been reset.")

    def patch_update(self, patch):
        """
        Each individual has fitness of resource_level and reproduces by that amount.
        """

        pop = patch.populations

        if pop['rv'] > 0 and pop['kv'] > 0:
            pop['rv'], pop['kv'] = self.eqboth
        elif pop['rv'] > 0:
            pop['rv'], pop['kv'] = self.eqr
        elif pop['kv'] > 0:
            pop['rv'], pop['kv'] = self.eqk

    def colonize(self, world):
        """
        This does three things.

        1. Take a sum of all yeast strains.
        2. Flies come eat some.
        3. Each fly visits a random patch and distributes those that survive the gut.

        We don't bother taking away the eaten yeast because so few are eaten.

        """

        # Make a list of all the populations and merge them into one big dictionary.
        dict_list = []
        for patch in world.patches:
            dict_list.append(patch.populations)
        pool = helpers.sum_dicts(dict_list)

        if self.reset_all_on_colonize:
            for patch in world.patches:
                self.reset_patch(patch)

        for i in range(0, self.num_flies):

            # Now each fly picks up fly_size yeast cells
            chosen = helpers.choose_k(self.fly_size, pool)

            # Each chosen cell has chance of dying. Colonizers have lower chance.
            survivors = []
            for yeast in chosen:
                if yeast == 'rv':
                    if random.random() < self.death_prob_r:
                        survivors.append(yeast)
                elif yeast == 'kv':
                    if random.random() < self.death_prob_v:
                        survivors.append(yeast)
                else:
                    raise Exception(f"The yeast {yeast} is not 'rv' or 'rs'.")

            # Choose a patch and drop the survivors into it.
            drop_patch = random.choice(world.patches)
            for yeast in survivors:
                if yeast == 'rv':
                    drop_patch.populations['rv'] += 1
                elif yeast == 'kv':
                    drop_patch.populations['kv'] += 1

    def kill_patches(self, world):
        """ Resets population on a patch to 0 with probability prob_death """

        for patch in world.patches:
            if random.random() < self.prob_death:
                self.reset_patch(patch)

    def census(self, world):

        print("\n")
        print("=" * 30)

        sum_r = 0
        sum_k = 0
        for patch in world.patches:
            sum_r += patch.populations['rv']
            sum_k += patch.populations['kv']
        print(f"\nGEN {world.age} TOTALS: rv: {sum_r}, kv: {sum_k}")

        print("\nIndividual Patch Populations")
        for patch in world.patches:
            print(f"Patch {patch.id}: {str(patch.populations)}")

    def stop_condition(self, world):
        return world.age > self.stop_time


if __name__ == "__main__":
    run(SimpleCompetitionColonization())
