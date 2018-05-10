"""
The Patch class. This contains three parts

1. The id of the patch (where it is on the world map)
2. The update function that moves the patch forward one time step.
3. A list of individuals in the patch.
4. A number of individuals. (Often we might ignore the individual list if we only care about numbers.)
5. A reference to the world that the patch is in. (Used so the patch knows information about the world.)

Any other attributes should be defined during patch creation. This can be done with
> patch.attribute_name = attribute_value
"""

import logging
from collections import Callable

from world import World


class Patch:

    def __init__(self, id, world="No World", update_function="Pass", individuals="Empty List", individual_num=0):
        """
        Args:
            id: The id that corresponds to the patch in the world map
            world: The world that the patch is in.
            update_function: The function that runs when we
            individuals: A list of individuals
            individual_num: The number of individuals

        Warnings: individual_num is not based off of individuals. It must be manually updated, and often one or the
        other is ignored.
        """

        # Init values
        self.individual_num = individual_num
        self.id = id
        self.update_function = update_function
        self.individuals = individuals
        if individuals == "Empty List":
            self.individuals = []

        self.world = world
        if self.world == "No World":
            logging.warning("Patch {} belongs to no world.".format(self.id))

        logging.debug("Patch {} created".format(self.id))

    def update(self):
        """
        Update the patch using whatever update function we've chosen.
        """

        logging.info("Patch {} updating with update function {}".format(self.id, self.update_function))

        if self.update_function == "Pass":
            logging.warning("No update function for patch {}.".format(self.id))
            pass
        else:
            try:
                self.update_function(self)
            except:
                if isinstance(self.update_function, Callable):
                    TypeError("update_function() for patch {} much be a function, not {}".format(self.id, type(
                        self.update_function)))
                else:
                    raise Exception("Error with update_function for patch {}.".format(self.id))

    def neighbor_ids(self):
        """
        Gets a list of all patches exactly distance 1 away.

        Returns:
            A list of patch ids.
        """

        neighbors = self.world.worldmap.neighbors(self.id)

    def census(self):
        pass
        #todo: log history of each patch
