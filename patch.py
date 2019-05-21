"""
The Patch class. This contains three parts

1. The id of the patch (where it is on the world map)
2. The patch_update function that moves the patch forward one time step.
3. A list of populations in the patch. (These can just represent a single individual)
5. A reference to the world that the patch is in. (Used so the patch knows information about the world.)

Any other attributes should be defined during patch creation. This can be done with
> patch.attribute_name = attribute_value
"""

import logging
import random
from collections import Callable
from general import pass_


class Patch:

    def __init__(self, id_, world, initial_populations=None):
        """
        Args:
            id_: The id that corresponds to the patch in the world map.
            world: The world that the patch is in.
            initial_populations: Overrides the initial population reset_patch gives, unless set to None.
        """

        # Init values
        self.id = id_
        self.patch_update = world.rules.patch_update
        self.world = world

        # Setup the patches
        self.reset_patch = world.rules.reset_patch
        self.reset_patch(self)

        if initial_populations is not None:
            self.populations = initial_populations  # Override

        self._safety_check()

        logging.info("Patch {} created".format(self.id))
        logging.debug("Patch {} values:{}".format(self.id, self.__dict__))

    def _safety_check(self):
        """ A quick check to make sure all values are well defined after initialization. """

        if self.world is None:
            logging.critical("Patch {} belongs to no world!".format(self.id))
            raise Exception("Patch {} belongs to no world!".format(self.id))

        if not hasattr(self.world, "worldmap"):
            error = "Patch {} of world {} has no worldmap!".format(self.id, self.world)
            logging.critical(error)
            raise Exception(error)

        # Test populations is good.
        # if self.populations is None:
        #     logging.warning(f"Patch {self.id} has initiated with None for populations.")

    def update(self):
        """
        Update the patch using whatever patch_update function we've chosen.

        Args:
            use_local: if true uses the patches' update fuction. Otherwise use the world rule's one.
            (These are generally the same, unless the patch function has been manually rewritten.)
        """

        # logging.debug("Patch {} updating with patch_update function {}".format(self.id, self.update))

        # try:
        self.patch_update(self)
        # except:
        #     if isinstance(self.update, Callable):
        #         raise TypeError("patch_update() for patch {} must be a function, not {}".format(self.id, type(
        #             self.update)))
        #     else:
        #         raise Exception("Error with patch_update for patch {}.".format(self.id))

    def neighbor_ids(self, self_loop=True):
        """
        Gets a list of all patches exactly distance 1 away.
        If self_loop is True then the patch is a neighbor of itself.

        Returns:
            A list of patch ids.
        """

        neighbors = self.world.worldmap[self.id]  # This goes to the worldmap adjacency matrix to find all neighbors
        nbs = list(neighbors)\

        if self_loop:
            nbs.append(self.id)

        return sorted(nbs)

    def random_neighbor(self):
        """ Returns a random neighboring patch """

        ids = self.neighbor_ids()

        # If no neighbors return None
        if not ids:
            return None

        id = random.choice(ids)
        return self.world.patches[id]

    def random_neighbors(self, n):
        """ Returns n random neighbor patches, without duplicates """

        l = []
        for i in range(0, n):
            l.append(self.random_neighbor())
        return l

    def change_update_function(self, func):
        """
        Changes the patch_update function to something else.
        """

        self.patch_update = func

    def census(self):
        pass
        # todo: log history of each patch
