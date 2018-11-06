import logging


class Rules:

    def __init__(self):
        pass

    def set_initial_conditions(self, world):
        """
        A function to set the initial conditions of the world, AFTER the default conditions have been set.

        Examples: After all patches have defaulted to empty, set one patch to be filled.

        Warnings: This happens after the patches are initialized, and can override the initial_populations
        parameter of a patch.
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
        and patch init_resources_per_patch.
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

    def check_param_lists(self, vect_list):
        """
        Checks that each of the parameter vectors are probability values. (Ie between zero and one)
        Args:
            vect_list: list containing the list of parameters for the NStrain model

        Returns:
            True if all values are between 0 and 1 inclusive. False otherwise

        """

        try:
            for l in vect_list:
                notprobabilties = [x for x in l if (x < 0 or x > 1)]
                if notprobabilties:  # If list empty
                    logging.warning("One of the probability parameter lists contains a param that is not a probability. "
                                    "(Ie not between 0 and 1)")
                    return False
        except:
            logging.error("One of the probability parameters is not a number! Expect problems")
            return False


        return True

    def census(self, world):
        logging.warning(f"census() for {world.name} does nothing.")

    def stop_condition(self, world):
        logging.warning(f"stop_condition() for {world.name} always returns true, so the program never stops running.")
        return True

