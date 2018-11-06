from collections import defaultdict
import random
from main import run
import networkx as nx
from world import World
import logging
from simrules import helpers
from rules import Rules
import general


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
        self.c = 0.2  # Consumption rate for init_resources_per_patch.
        self.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
        self.mu_v = 0.1  # Background death rate for vegetative cells
        self.mu_s = 0.05  # Background death rate for sporulated cells
        self.mu_R = 0.01  # "death" rate for init_resources_per_patch.
        self.activation = 0.015  # vegetation factor
        self.gamma = 10  # Rate of resource renewal
        self.kv_fly_survival = 0.001  # Probability of surviving the fly gut
        self.ks_fly_survival = 0.8  # Probability of surviving the fly gut
        self.rv_fly_survival = 0.001  # Probability of surviving the fly gut
        self.rs_fly_survival = 0.8  # Probability of surviving the fly gut
        self.resources = 50  # Initial init_resources_per_patch
        self.sk = 0.01  # Strategy of competitor. (Chance of sporulating)
        self.sr = 0.4  # Strategy of colonizer

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

        self.files = []
        # self.total_file = open('save_data/gen_totals.csv', 'a+')  # Saving is currently broken for this

    def set_initial_conditions(self, world):
        """ Give half the patches each strain. """

        # For each patch, select a strain to fill the patch
        for patch in world.patches:

            if random.random() < .5:
                patch.populations['rv'] = 5
                patch.populations['rs'] = 5
            else:
                patch.populations['kv'] = 5
                patch.populations['ks'] = 5

        # Open save files to write to
        # for patch in world.patches:
        #     self.files.append(open('save_data/patch_' + str(patch.id) + '.csv', 'a+'))

    def reset_patch(self, patch):
        """
        Each patch starts with 0 of all individuals, unless changed by initial_conditions
        and a resource level of 0.
        """

        patch.populations = {'rv': 0, 'kv': 0, 'rs': 0, 'ks': 0}  # Reset populations to 0

        # Reset patch parameters
        patch.c = self.c
        patch.alpha = self.alpha
        patch.activation = self.activation
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

        # Calculate the changes in the populations and init_resources_per_patch
        change_rv = patch.alpha * patch.c * patch.resources * patch.populations['rv'] * (1 - patch.sr) - patch.mu_v * \
                    patch.populations['rv'] + patch.activation * patch.resources * patch.populations['rs']
        change_rs = patch.alpha * patch.c * patch.resources * patch.populations['rv'] * patch.sr - patch.mu_s * \
                    patch.populations['rs'] - patch.activation * patch.resources * patch.populations['rs']
        change_kv = patch.alpha * patch.c * patch.resources * patch.populations['kv'] * (1 - patch.sk) - patch.mu_v * \
                    patch.populations['kv'] + patch.activation * patch.resources * patch.populations['ks']
        change_ks = patch.alpha * patch.c * patch.resources * patch.populations['kv'] * patch.sk - patch.mu_s * \
                    patch.populations['ks'] - patch.activation * patch.resources * patch.populations['ks']
        change_resources = - patch.c * patch.resources * patch.populations['kv'] - patch.c * patch.resources * \
                           patch.populations['rv'] + patch.gamma - patch.mu_R * patch.resources

        # Change the current population values.
        patch.populations['rv'] += change_rv * self.dt
        patch.populations['rs'] += change_rs * self.dt
        patch.populations['kv'] += change_kv * self.dt
        patch.populations['ks'] += change_ks * self.dt
        patch.resources += change_resources * self.dt

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
            num_eaten = int(helpers.typeIIresponse(helpers.sum_dict(patch.populations), self.fly_attack_rate,
                                                   self.fly_handling_time))

            # print(f"num_eaten for patch {patch.id}: {num_eaten}")

            if self.drop_single_yeast:
                num_eaten = 1
                # todo: does having this before survival-probabilities effect the simulation?

            # If actually eat any yeast, then see which survive and drop into new neighboring patch.
            if num_eaten > 0:

                try:
                    hitchhikers = random.choices(list(patch.populations.keys()), list(patch.populations.values()),
                                                 k=num_eaten)
                except IndexError:
                    if helpers.sum_dict(patch.populations) > 0:
                        raise Exception(
                            f"Cannot choose hitchikers in patch {patch.id} with population {patch.populations}")
                    else:
                        logging.info(f"Patch {patch.id} is empty, the fly dies a slow death of starvation...")
                        hitchhikers = {}

                # print(patch.populations)
                # print(hitchhikers)
                survivors = {'rv': 0, 'rs': 0, 'kv': 0, 'ks': 0}
                for key in hitchhikers:
                    if key == 'rv':
                        patch.populations['rv'] -= self.yeast_size
                        if random.random() < self.rv_fly_survival:
                            survivors['rv'] += self.yeast_size
                    if key == 'rs':
                        patch.populations['rs'] -= self.yeast_size
                        if random.random() < self.rs_fly_survival:
                            survivors['rs'] += self.yeast_size
                    if key == 'kv':
                        patch.populations['kv'] -= self.yeast_size
                        if random.random() < self.kv_fly_survival:
                            survivors['kv'] += self.yeast_size
                    if key == 'ks':
                        patch.populations['ks'] -= self.yeast_size
                        if random.random() < self.ks_fly_survival:
                            survivors['ks'] += self.yeast_size

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

        sum_dicts = helpers.merge_dicts([patch.populations for patch in world.patches])  # Sum populations from patch
        total_resources = 0
        for patch in world.patches:  # Sum init_resources_per_patch from each patch
            total_resources += patch.resources

        print("\nIndividual Patch Info")
        for patch in world.patches:
            print(f"Patch {patch.id}")
            print(f"    Population: {str(patch.populations)}")
            print(f"    Resources: {patch.resources}")

            # Append data to patch save files
            # self.files[patch.id].write(str(patch.populations['rv']) + ',' + str(patch.populations['rs']) + ',' +
            #                            str(patch.populations['kv']) + ',' + str(patch.populations['ks']) + ',' +
            #                            str(patch.resources) + '\n')

        print(f"\nGEN {world.age} TOTALS: {str(sum_dicts)}.")

        # Append data to gen_totals file
        # Saving is currently broken Totals file removed to not break test
        # self.total_file.write(str(sum_dicts['rv']) + ',' + str(sum_dicts['rs']) + ',' +
        #                       str(sum_dicts['kv']) + ',' + str(sum_dicts['ks']) + ',' +
        #                       str(total_resources) + '\n')

    def stop_condition(self, world):
        return world.age > self.stop_time


if __name__ == "__main__":
    run(World(TwoStrain()))
