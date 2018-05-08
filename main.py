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

def simulate():

    world = World()

    world.update_patches()
    world.colonize()
    world.kill_patches()

if __name__ == "__main__":
    """ Run the program. """

    logging.basicConfig(filename='simulation.log', level=logging.INFO)
    logging.info('Started')
    simulate()
    logging.info('Finished')

