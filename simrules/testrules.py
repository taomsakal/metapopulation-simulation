import logging
from rules import Rules

class AddOne(Rules):

    def __init__(self, worldmap):
        self.worldmap = worldmap

    def reset_patch(self, patch):
        """
        Resets the patch to the default value. This function also runs to initialize patches.
        """

        patch.populations = 0

    def patch_update(self, patch):
        """
        Runs the population dynamics in a patch for one timestep. This usually manipulates population levels
        and patch init_resources_per_patch.
        """

        patch.populations += 1
