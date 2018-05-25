import logging


class Rules:

    def __init__(self):
        pass

    def set_initial_conditions(self, world):
        """
        A function to set the initial conditions of the world, AFTER the default conditions have been set.

        Examples: After all patches have defaulted to empty, set one patch to be filled.
        """

        logging.warning(f"set_initial_conditions() for world {world.name} does nothing.")

    def reset_patch(self, patch):
        """
        Resets the patch to the default value. This function also runs to initialize patches.
        """

        logging.warning(f"reset_patch() for {patch.id} in {patch.world.name} does nothing.")

    def patch_update(self, patch):
        """
        Runs the population dynamics in a patch for one timestep. This usually manipulates population levels
        and patch resources.
        """

        logging.warning(f"patch_update() for {patch.id} in {patch.world.name} does nothing.")

    def colonize(self, world):
        """
        Allows each patch the chance to colonize.

        Warnings:
            One must decide if this happens in parallel or is sequential.
        """

        logging.warning(f"colonize() for {world.name} does nothing.")

    def kill_patches(self, world):
        """ Used for iterating through patches and killing them with some probability.
        Can also be used for other versions of patch manipulation"""

        logging.warning(f"kill_patches() for {world.name} does nothing.")

    def census(self, world):
        logging.warning(f"census() for {world.name} does nothing.")

    def stop_condition(self, world):
        logging.warning(f"stop_condition() for {world.name} always returns true, so the program never stops running.")
        return True

