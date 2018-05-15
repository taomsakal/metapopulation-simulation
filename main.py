"""
This is the main simulation. It is in four parts:
    1. Patch patch_update
    2. Colonization
    3. Patch death
    4. Census/logging
The program flows through these steps in the function simulate().
simulate() can be edited to put these steps in any order.

The Simulation itself is an object. This is so we can stop it, save it, and then return to it later.
"""

import logging
import networkx as nx
from world import World

# Change these to the needed functions
DEFAULT_PATCH_UPDATE_FUNCTION = None
COLONIZE_FUNCTION = None
KILL_PATCHES_FUNCTION = None
CENSUS_FUNCTION = None

class Simuation():

    def __init__(self):
       """ Init the simulation, which holds the world(s) and the default functions for it. """

    def simulate(self, iterations):
        """
        Run the simulation.

        Args:
            iterations: number of timesteps to run for.

        Returns: The world after the simulation is over.

        """

        world = World(self.setup_map(), DEFAULT_PATCH_UPDATE_FUNCTION, COLONIZE_FUNCTION, KILL_PATCHES_FUNCTION, CENSUS_FUNCTION, dt=1)

        for i in range(0, iterations):
            world.update_patches()
            world.colonize()
            world.kill_patches()

        return world


    def setup_map(self):
        """
        Return a worldmap.
        """
        return nx.complete_graph(20)


    if __name__ == "__main__":
        """ Run the program. """

        logging.basicConfig(filename='simulation.log', level=logging.INFO)
        logging.info('Started')
        simulate()
        logging.info('Finished')
