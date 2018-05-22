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
from simrules.one_species import OneSpecies


def simulate(world):
    """
    Run the simulation on the world.
    """

    while not world.rules.stop_condition():
        world.update_patches()
        world.colonize()
        world.kill_patches()
        world.census()
        world.age += 1

    logging.info(f"Finished simulating world {world.name}")
    return world


if __name__ == "__main__":
    """ Run the program. """

    logging.basicConfig(filename='simulation.log', level=logging.INFO)
    logging.info('Started')

    world1 = World(OneSpecies(3, nx.complete_graph(10), 0.1, [1.1], 1000))
    simulate(world1)

    logging.info('Finished')
