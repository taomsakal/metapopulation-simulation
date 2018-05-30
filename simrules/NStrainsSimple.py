"""
A simple simulation with n species that spreads.

Each patch has a resource value R. A species on that patch multiplies by that resource value.

Updates and colonization happen in a random order each time.
"""

import random
import logging
from simrules import helpers
from rules import Rules


class NStrainsSimple(Rules):

    def __init__(self, num_strains, worldmap, prob_death, resource_value, stop_time, dt=1):

        super().__init__()
        self.num_strains = num_strains  # Number of strains. Must be integer
        self.worldmap = worldmap  # The graph
        self.prob_death = prob_death  # Probability of a patch dying.
        self.resource_value = resource_value
        self.stop_time = stop_time  # Iterations to run
        self.dt = dt

    def set_initial_conditions(self, world):
        """
        Initial conditions for the world. This starts one patch with one of each strain
        This happens after the patches have been initialized
        """
        world.patches[0].populations = [1] * self.num_strains

    def reset_patch(self, patch):
        """
        Each patch starts with 0 of all individuals, unless changed by initial_conditions
        and a random resource value from resource_value.
        """
        patch.populations = [0] * self.num_strains
        patch.resource_level = self.resource_value

    def patch_update(self, patch):
        """
        Each individual has fitness of resource_level and reproduces by that amount.
        """

        patch.populations[:] = [strain + strain * self.resource_value * self.dt for strain in patch.populations]


    def colonize(self, world):
        """
        A random individual is chosen from each patch and sent to a random neighbor patch.
        """

        # Make a random order for each colonization event.
        order = helpers.random_index_order(world.patches)

        print("\nCOLONIZE STEP")
        for i in order:

            patch = world.patches[i]

            if not helpers.has_positive(patch.populations):
                s = f"Patch {patch.id} is empty, cannot colonize."
                logging.info(s)
                print(s)
            elif patch.random_neighbor() is None:
                print(f"Patch {patch.id} has no neighbors, so cannot colonize.")
            else:
                # Randomly select from patch's population, with chance proportional to population size
                # Remember, each population is a list
                #       [population size strain 0, population of strain 1, ... population of strain n]
                strain_id = random.choices(range(0, len(patch.populations)), weights=patch.populations)[0]
                target_patch = patch.random_neighbor()

                patch.populations[strain_id] -= 1  # Take the individual from the current patch...
                target_patch.populations[strain_id] += 1  # ... and add it to those of the new patch

                print(f"1 yeast of strain {strain_id} moved from {patch.id} to {target_patch.id}.")

    def kill_patches(self, world):
        """ Resets population on a patch to 0 with probability prob_death """

        print("\nKILL PATCHES STEP")

        for patch in world.patches:
            if random.random() < self.prob_death:
                self.reset_patch(patch)
                print(f"Patch {patch.id} killed.")

    def census(self, world):
        print(f"\n=== Time {world.age} ===============\n")
        for patch in world.patches:
            print(f"Patch {patch.id}: {str(patch.populations)}.")

    def stop_condition(self, world):
        return world.age > self.stop_time
