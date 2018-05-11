"""
This holds the world, which describes the state of the system. We must give it specific laws for the update functions.
    -- patch_update() updates each patch
    -- colonize() simulates colonization
    -- kill_patches() simulates patch death
    -- census() will log
The world also has the 'worldmap' which is a networkx weighted directed graph that describes which patches
are connected together. The colonize function references this map.

Patches are generated from the world map, but they do not exist in the world map.
The map is just a reference (that may change). Every patch has an id associating a map-node to the patch.

The world also contains a Historian, which is a class that outputs


"""
import logging

from general import pass_
from patch import Patch


class World:

    def __init__(self, worldmap, patch_update_function=pass_, colonize_function=pass_, kill_patches_function=pass_,
                 census_function=pass_, dt=1, name="World 1"):
        """
        Initialize the world with a specific worldmap, timestep length, and update functions.
        (patch_update, colonize, kill_patches, and census.)

        Args:
            worldmap: a networkx graph
            dt: the size of the timestep. (Default is 1)
            patch_update_function: update function
            colonize_function: update function
            kill_patches_function: update function
            census_function: update function
            name: Name of the world

        Notes:
            See patch_update_functions.py for details about the update functions requirements.
            All the functions default to pass.
        """

        # Init the variables
        self.worldmap = worldmap
        self.name = name
        self.dt = dt
        self.patch_update = patch_update_function
        self.colonize = colonize_function
        self.kill_patches = kill_patches_function
        self.census = census_function

        self.current_iteration = 0
        self.patches = self.init_patches(self.worldmap)

        logging.info("{} created.".format(self.name))
        logging.debug("{} __dict__: {}".format(self.name, self.__dict__))

    def init_patches(self, world_map):
        """
        Initialize the patches by generating them from the world map and adding them to the patches list.

        Args:
            world_map: networkx directed graph

        Returns:
            a list of patches
        """

        patches = []
        for node in world_map.nodes():
            new_patch = Patch(node, self)
            patches.append(new_patch)
            logging.info("Worldmap node {} mapped to patch {}.".format(str(node), new_patch.id))

        return patches

    # #The below don't work and always return the exceptions. This is not important, just annoying in the logs.
    # def __str__(self):
    #     try:
    #         return self.name
    #     except:
    #         return 'aaaaaaaa'
    #
    # def __repr__(self):
    #     try:
    #         return self.name
    #     except:
    #         return "reeeeee"


class Historian():
    """
    The Historian watches the parameters we tell them to and outputs it in a log.

    By default the Historian only watches the patches.
    """
