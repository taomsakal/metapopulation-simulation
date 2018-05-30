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
from rules import Rules

class World:

    def __init__(self, rules, name="World 1"):
        """
        Creates a world with a certain set of simrules

        Args:
            rules: A set of simrules, which is a simrules object.
            name: a name for the world
        """

        # Safety type check
        if not issubclass(type(rules), Rules):
            raise TypeError(f"The rules for {name} is of type {type(rules)}, which is not a subclass of Rules.")


        self.rules = rules
        self.name = name
        self.age = 0
        self.worldmap = rules.worldmap

        self.patches = self.init_patches(self.worldmap)

        logging.info("{} created.".format(self.name))
        logging.debug("{} __dict__: {}".format(self.name, self.__dict__))

    def init_patches(self, world_map):
        """
        Initialize the patches by generating them from the world map and adding them to the patches list.
        Also sets the patch_update function for each patch to be the world's default patch patch_update function
        and the default populations.

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

    def update_patches(self):
        """
        Go through each patch and patch_update it with the patch_update function the patch owns.

        Warnings: This assumes patch patch_update functions do not depend on other patches.
        This goes through each patch is sequential order, and dynamics will change depending on the order if
        patches interact during this step.
        """

        for patch in self.patches:
            patch.update()

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
