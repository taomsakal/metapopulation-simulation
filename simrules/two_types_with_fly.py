from collections import defaultdict
from general import sum_dicts
import random
import logging
from simrules import helpers
from rules import Rules


class SimpleCompetitionColonization(Rules):
    """
    A simple competition colonization model.
    """

    def __init__(self, num_strains, worldmap, prob_death, resource_values, stop_time):

        super().__init__()
        self.num_strains = num_strains  # Number of strains. Must be integer
        self.worldmap = worldmap  # The graph
        self.prob_death = prob_death  # Probability of a patch dying.
        self.resource_values = resource_values
        self.stop_time = stop_time  # Iterations to run

    def set_initial_conditions(self, world):
        """ Initial conditions for the world. This starts one patch with one of each strain """
        world.patches[0] = [1] * self.num_strains

    def reset_patch(self, patch):
        """
        Each patch starts with 0 of all individuals, unless changed by initial_conditions
        and a random resource value from resource_values.
        """
        patch.populations = [0] * self.num_strains
        patch.resource_level = random.choice(self.resource_values)

    def patch_update(self, patch):
        """
        Each individual has fitness of resource_level and reproduces by that amount.
        """

        for population in patch.populations:
            population += patch.resource_level * population * patch.world.dt

    def colonize(self, world):
        """
        A random individual is chosen from each patch and sent to a random neighbor patch.
        """

        for patch in world.patches:

            if not helpers.has_positive(patch.populations):
                s = f"Patch {patch.id} is empty, cannot colonize."
                logging.info(s)
                return s

            # Randomly select from patch, with chance proportional to population size
            source_id = random.choices(range(0, len(patch.populations)), weights=patch.populations)
            target_id = random.choice(patch.neighbor_ids())

            # Move the individual
            patch.populations[source_id] -= 1
            patch.populations[target_id] += 1

    def kill_patches(self, world):
        """ Resets population on a patch to 0 with probability prob_death """

        for patch in world.patches:
            if random.random() < self.prob_death:
                self.reset_patch(patch)

    def census(self, world):
        for patch in world:
            print(str(patch.populations))

    def stop_condition(self, world):
        return world.age > self.stop_time
# Todo: this function isn't finished.
def mush_and_redistribute(world):
    """
    This does three things.

    1. Take a sum of all yeast strains.
    2. Flies come eat some.
    3. Each fly visits a random patch and distributes those that survive the gut.

    Currently the function assumes that all patches die during it.

    """
    # Make a list of all the individuals and merge them into one big dictionary.
    dict_list = []
    for patch in world:
        dict_list.append(patch.individuals)
    merged_dict = sum_dicts(dict_list)

    # Reset all patches, make sure that the individuals are set correctly

    # Now for each patch the fly will pick some yeast up, digest some, and drop the survivors in a random patch.
    def num_flies():
        """ Function to generate a number of flies. """
        return 10

    def pickup(dict):
        pass

    for i in range(0, num_flies()):
        hitchhikers = pickup(merged_dict)
        hitchhikers[0] *= .2  # 20% of competitors survive the gut
        hitchhikers[1] *= .8  # 80% of colonizers survive

        # Drop off hitchhikers to new patch
        drop_patch = random.choice(world.patches)
        drop_patch.individuals['Competitors'] = hitchhikers[0]
        drop_patch.individuals['Colonizers'] = hitchhikers[1]


