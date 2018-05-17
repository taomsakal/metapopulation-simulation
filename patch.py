"""
The Patch class. This contains three parts

1. The id of the patch (where it is on the world map)
2. The patch_update function that moves the patch forward one time step.
3. A list of individuals in the patch.
4. A number of individuals. (Often we might ignore the individual list if we only care about numbers.)
5. A reference to the world that the patch is in. (Used so the patch knows information about the world.)

Any other attributes should be defined during patch creation. This can be done with
> patch.attribute_name = attribute_value
"""

import logging
from collections import Callable
from general import pass_


class Patch:

    def __init__(self, id_, world, update_function=pass_, individuals=None, additional_setup_func=pass_):
        """
        Args:
            id_: The id that corresponds to the patch in the world map
            world: The world that the patch is in.
            update_function: The function that runs when we
            individuals: Some data structure to keep track of individuals. Defaults to the number 0.
            additional_setup_func: function to do additional setup

        Warnings: individual_num is not based off of individuals. It must be manually updated, and often one or the
        other is ignored. They have different names for clarity.
        """

        # Init values
        self.additional_setup_func = additional_setup_func
        self.id = id_

        if individuals is None:
            logging.warning(f"Patch {self.id} has no individuals. Defaulting to 0")
            self.individuals = 0
        else:
            self.individuals = individuals

        self.update_function = update_function

        self.world = world
        if self.world is None:
            logging.critical("Patch {} belongs to no world!".format(self.id))
            raise Exception("Patch {} belongs to no world!".format(self.id))
        if not hasattr(self.world, "worldmap"):
            error = "Patch {} of world {} has no worldmap!".format(self.id, self.world)
            logging.critical(error)
            raise Exception(error)

        self.additional_setup_func(self)  # Do any aditional setup needed

        logging.info("Patch {} created".format(self.id))
        logging.debug("Patch {} values:{}".format(self.id, self.__dict__))

    def update(self):
        """
        Update the patch using whatever patch_update function we've chosen.
        """

        logging.debug("Patch {} updating with patch_update function {}".format(self.id, self.update))

        try:
            self.update_function(self)
        except:
            if isinstance(self.update, Callable):
                raise TypeError("patch_update() for patch {} must be a function, not {}".format(self.id, type(
                    self.update)))
            else:
                raise Exception("Error with patch_update for patch {}.".format(self.id))

    def neighbor_ids(self):
        """
        Gets a list of all patches exactly distance 1 away.

        Returns:
            A list of patch ids.
        """

        neighbors = self.world.worldmap[self.id]  # This goes to the worldmap adjacency matrix to find all neighbors
        return list(neighbors)

    def change_update_function(self, function):
        """
        Changes the patch_update function to something else.

        Args:
            function: function to change it to
            *args: arguments of function
            **kwargs: keyword arguments of function
        """

        self.update_function = function

    def census(self):
        pass
        # todo: log history of each patch
