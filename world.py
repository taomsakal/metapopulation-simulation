"""
This holds the world, which describes the state of the system. We must give it specific laws for the update functions.
    -- patch_update() updates each patch
    -- colonize() simulates colonization
    -- kill_patches() simulates patch death
    -- census() will log
The world also has the 'landscape_map,' which is a networkx weighted directed graph that describes which patches
are connected together. The colonize function references this map.

Patches are generated from the landscape map, but they do not exist in the landscape map.
The map is just a reference (that may change). Every patch has an id associating a map-node to the patch.

The world also contains a Historian, which is a class that outputs


"""

class World():

    def __init__(self, landscape_map, patch_update_function, colonize_function, kill_patches_function, census_function, dt=1):
        """

        Args:
            landscape_map: a networkx graph
            dt: the size of the timestep. (Default is 1)
            patch_update_function: update function
            colonize_function: update function
            kill_patches_function: update function
            census_function: update function

        Notes:
            See update_functions.py for details about the update functions requirements.
        """

        # Init the variables
        self.landscape_map = landscape_map
        self.patches = self.init_patches(self.landscape_map)
        self.dt = dt
        self.patch_update = patch_update_function
        self.colonize = colonize_function
        self.kill_patches = kill_patches_function
        self.census = census_function

        self.current_iteration = 0


    def init_patches(self, landscape_map):
        """
        Initialize the patches by generating them from the landscape map and adding them to the patches list.

        Args:
            landscape_map: networkx directed graph

        Returns:
            a list of patches
        """

        patches = []
        for node in landscape_map.nodes():
            new_patch = Patch(node) #Todo: give id and maybe attributes
            patches.append(new_patch)

        return patches

class Historian():
    """
    The Historian watches the parameters we tell them to and outputs it in a log.

    By default the Historian only watches the patches.
    """

