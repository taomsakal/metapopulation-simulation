"""
This is the main simulation. It is in four parts:
    1. Patch update
    2. Colonization
    3. Patch death
    4. Census/logging
The program flows through these steps in the function simulate().
simulate() can be edited to put these steps in any order.
"""

import logging
import networkx as nx
from world import World


def simulate():
    # Change these to the needed functions
    patch_update_function = None
    colonize_function = None
    kill_patches_function = None
    census_function = None

    world = World(setup_map(), patch_update_function, colonize_function, kill_patches_function, census_function, dt=1)

    world.update_patches()
    world.colonize()
    world.kill_patches()

    return world


def setup_map():
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
