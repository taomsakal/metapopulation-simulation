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

from simrules import helpers
from world import World
from simrules.NStrainsSimple import NStrainsSimple


def simulate(world):
    """
    Run the simulation on the world.
    Remember that each world has it's own set of rules.
    """

    world.rules.set_initial_conditions(world)
    while not world.rules.stop_condition(world):
        world.rules.census(world)
        world.rules.colonize(world)
        world.update_patches()
        world.rules.kill_patches(world)
        world.age += 1

    world.rules.census(world)
    logging.info(f"Finished simulating world {world.name}")
    return world


def run(world, log_name='simulation.log'):
    """ Run the program. """

    logging.basicConfig(filename='simulation.log', level=logging.INFO)
    logging.info('Started')
    simulate(world)
    logging.info('Finished')
