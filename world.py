"""
This holds the world, which describes the state of the system. We must give it specific laws for the patch_update functions.
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

    def __init__(self, worldmap, default_patch_update_function=pass_, default_individuals=0, colonize_function=pass_,
                 kill_patches_function=pass_,
                 census_function=pass_, patch_setup_function=pass_, dt=1, name="World 1"):
        """
        Initialize the world with a specific worldmap, timestep length, and patch_update functions.
        (patch_update, colonize, kill_patches, and census.)

        Args:
            worldmap: a networkx graph
            dt: the size of the timestep. (Default is 1)
            default_patch_update_function: patch_update function
            colonize_function: patch_update function
            kill_patches_function: patch_update function
            patch_setup_function: additional setup for the patches.
            census_function: patch_update function
            name: Name of the world

        Notes:
            See patchupdate_functions.py for details about the patch_update functions requirements.
            All the functions default to pass.
        """

        # Init the variables
        self.default_individuals = default_individuals
        self.patch_setup_function = patch_setup_function
        self.worldmap = worldmap
        self.name = name
        self.dt = dt
        self.patch_update = default_patch_update_function
        self.patch_update_args = None
        self.patch_update_kwargs = None
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
        Also sets the patch_update function for each patch to be the world's default patch patch_update function
        and the default individuals.

        Args:
            world_map: networkx directed graph

        Returns:
            a list of patches
        """

        patches = []
        for node in world_map.nodes():
            new_patch = Patch(node, self, update_function=self.patch_update, individuals=self.default_individuals)
            patches.append(new_patch)
            logging.info("Worldmap node {} mapped to patch {}.".format(str(node), new_patch.id))

        return patches

    def update_patches(self):
        """
        Go through each patch and patch_update it with the patch_update function the patch owns.

        Warnings: This assumes patch patch_update functions do not depend on other patches.
        This goes through each patch is sequential order, and dynamics will change depending on the order if
        patches interact during this step.
        """

        for patch in self.patches:
            patch.update()

    def colonize_function(self):
        """ Run the given colonize function. """
        self.colonize_function(self)


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
