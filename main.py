"""
This is the main simulation. It is in four parts:
    1. Patch update
    2. Colonization
    3. Patch death
    4. Census/logging
The program flows through these steps in the function simulate().
simulate() can be edited to put these steps in any order.
"""

def simulate():

    world = World()

    world.update_patches()
    world.colonize()
    world.kill_patches()


