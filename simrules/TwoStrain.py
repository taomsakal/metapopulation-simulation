from collections import defaultdict
import random
from main import run
import networkx as nx
from world import World
import logging
from simrules import helpers
from rules import Rules


class TwoStrain(Rules):
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

    def __init__(self):

        super().__init__()

        # Default patch specific parameters
        # (These are passed into the patch, which always uses it's own, meaning we can change these per patch.)
        self.c = 0.2  # Consumption rate for resources.
        self.alpha = 0.2  # Conversion factor for resources into cells5
        self.mu_v = 0.1  # Background death rate for vegetative cells
        self.mu_s = 0.05  # Background death rate for sporulated cells
        self.mu_R = 0.01  # "death" rate for resources.
        self.gamma = 10  # Rate of resource renewal
        self.kv_fly_survival = 0.2  # Probability of surviving the fly gut
        self.ks_fly_survival = 0.8  # Probability of surviving the fly gut
        self.rv_fly_survival = 0.2  # Probability of surviving the fly gut
        self.rs_fly_survival = 0.8  # Probability of surviving the fly gut
        self.resources = 200
        self.sk = 0.2  # Strategy of competitor. (Chance of sporulating)
        self.sr = 0.4

        # Global Parameters
        self.dt = 1  # Timestep size
        self.worldmap = nx.complete_graph(100)  # The worldmap
        self.prob_death = 0.05  # Probability of a patch dying.
        self.stop_time = 1000  # Iterations to run
        self.num_flies = 50  # Number of flies each colonization event

        # The number of yeast eaten is a type 2 functional response
        self.fly_attack_rate = 0.3
        self.fly_handling_time = 0.3

        self.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
        # Ie mush all current patches into a pool and redistribute to new patches.

    def set_initial_conditions(self, world):
        """ Give half the patches each strain. """
        for patch in world.patches:

            if random.random() < .5:
                patch.populations['rv'] = 30
                patch.populations['rs'] = 30
            else:
                patch.populations['kv'] = 30
                patch.populations['ks'] = 30

    def reset_patch(self, patch):
        """
        Each patch starts with 0 of all individuals, unless changed by initial_conditions
        and a resource level of 0.
        """

        patch.populations = {'rv': 0, 'kv': 0, 'rs': 0, 'ks': 0}  # Reset populations to 0

        patch.c = self.c
        patch.alpha = self.alpha
        patch.mu_v = self.mu_v
        patch.mu_s = self.mu_s
        patch.mu_R = self.mu_R
        patch.gamma = self.gamma
        patch.kv_fly_survival = self.kv_fly_survival
        patch.ks_fly_survival = self.ks_fly_survival
        patch.rv_fly_survival = self.rv_fly_survival
        patch.rs_fly_survival = self.rs_fly_survival
        patch.resources = self.resources
        patch.sk = self.sk
        patch.sr = self.sr

        print(f"Patch {patch.id} has been reset.")

    def patch_update(self, patch):
        """
        Each individual has fitness of resource_level and reproduces by that amount.
        """

        # Calculate the changes in the populations and resources
        change_rv = patch.alpha * patch.c * patch.resources * patch.populations['rv'] * (1 - patch.sr) - patch.mu_v * \
                    patch.populations['rv']
        change_rs = patch.alpha * patch.c * patch.resources * patch.populations['rv'] * (patch.sr) - patch.mu_s * \
                    patch.populations['rs']
        change_kv = patch.alpha * patch.c * patch.resources * patch.populations['kv'] * (1 - patch.sk) - patch.mu_v * \
                    patch.populations['kv']
        change_ks = patch.alpha * patch.c * patch.resources * patch.populations['kv'] * patch.sk - patch.mu_s * \
                    patch.populations['ks']
        change_resources = - patch.c * patch.resources * patch.populations['kv'] - patch.c * patch.resources * \
                           patch.populations['rv'] + patch.gamma - patch.mu_R * patch.resources

        # Change the current population values.
        patch.populations['rv'] += change_rv * self.dt
        patch.populations['rs'] += change_rs * self.dt
        patch.populations['kv'] += change_kv * self.dt
        patch.populations['ks'] += change_ks * self.dt
        patch.resources += change_resources

        # make sure none become negative
        for key, value in patch.populations.items():
            if value < 0:
                patch.populations[key] = 0

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
            num_eaten = int(helpers.typeIIresponse(helpers.sum_dict(patch.populations), self.fly_attack_rate, self.fly_handling_time))

            #print(f"num_eaten for patch {patch.id}: {num_eaten}")

            # If actually eat any yeast, then see which survive and drop into new neighboring patch.
            if num_eaten > 0:



                hitchhikers = random.choices(list(patch.populations.keys()), list(patch.populations.values()),
                                             k=num_eaten)

                #print(patch.populations)
                #print(hitchhikers)
                survivors = {'rv': 0, 'rs': 0, 'kv': 0, 'ks': 0}
                for key in hitchhikers:
                    if key == 'rv':
                        if random.random() < self.rv_fly_survival:
                            survivors['rv'] += 1
                    if key == 'rs':
                        if random.random() < self.rs_fly_survival:
                            survivors['rs'] += 1
                    if key == 'kv':
                        if random.random() < self.kv_fly_survival:
                            survivors['kv'] += 1
                    if key == 'ks':
                        if random.random() < self.ks_fly_survival:
                            survivors['ks'] += 1

                # Add the survivors to a random neighboring patch.
                # If no neighbors then the fly vanishes
                drop_patch = patch.random_neighbor()
                if drop_patch is not None:
                    drop_patch.populations = helpers.merge_dicts([drop_patch.populations, survivors])

    def kill_patches(self, world):
        """ Resets population on a patch to 0 with probability prob_death """

        for patch in world.patches:
            if random.random() < self.prob_death:
                self.reset_patch(patch)

    def census(self, world):

        print("\n")
        print("=" * 30)

        sum_dicts = helpers.merge_dicts([patch.populations for patch in world.patches])

        print("\nIndividual Patch Info")
        for patch in world.patches:
            print(f"Patch {patch.id}")
            print(f"    Population: {str(patch.populations)}")
            print(f"    Resources: {patch.resources}")

        print(f"\nGEN {world.age} TOTALS: {str(sum_dicts)}.")

    def stop_condition(self, world):
        return world.age > self.stop_time


if __name__ == "__main__":

    run(World(TwoStrain()))
