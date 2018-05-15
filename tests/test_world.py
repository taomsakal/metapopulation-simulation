import logging
import pytest
import networkx as nx

from world import World
from patch import Patch
from patch_update_functions import add_one, exponential_growth

logging.basicConfig(filename='test_world.log', level=logging.DEBUG)
logging.info("--- Started " + "-" * 50)


def complete_world():
    """ Returns a world with the world map a K_10 graph and all default patch_update functions"""
    return World(nx.complete_graph(5))

def path_world():
    """ Return a world that's a path graph of 4 nodes. """
    return World(nx.path_graph(4))


def trivial_world():
    """Return a world made up of a single node"""
    return World(nx.complete_graph(1))


def default_patch():
    """Returns a patch with id 0, in a trivial world"""
    return Patch(0, trivial_world())

# =========================

class TestInit:
    def test_patch_generation(self):
        """ Test that correct number of patches are generated. """

        for n in range(1, 20):
            map1 = nx.complete_graph(n)
            map2 = nx.erdos_renyi_graph(n, 0.2)
            map3 = nx.barabasi_albert_graph(n + 1, 1)

            world1 = World(map1, None, None, None, None)
            world2 = World(map2, None, None, None, None)
            world3 = World(map3, None, None, None, None)

            assert len(world1.patches) == n
            assert len(world2.patches) == n
            assert len(world3.patches) == n + 1  # Some parameter values for ba graph forces n > 1, so offset by one.


    def test_make_world(self):
        world1 = complete_world()

        assert world1.worldmap is not None
        assert world1.name == "World 1"


    def test_worldmap(self):
        world1 = complete_world()

        assert list(world1.worldmap.nodes()) == [0, 1, 2, 3, 4]
        assert list(world1.worldmap.neighbors(0)) == [1, 2, 3, 4]
        assert list(world1.worldmap[0]) == [1, 2, 3, 4]

        assert world1.patches[0].neighbor_ids() == [1, 2, 3, 4]

class TestPatchUpdates:

    def test_add_one(self):

        world1 = World(nx.complete_graph(5), default_patch_update_function=add_one)

        assert world1.patches[0].individual_num == 0
        world1.update_patches()
        assert world1.patches[0].individual_num == 1

        world1.update_patches()
        for patch in world1.patches:
            assert patch.individual_num == 2

        for i in range(1, 100):
            world1.update_patches()
            for patch in world1.patches:
                assert patch.individual_num == 2 + i

    def test_add_one_complex(self):

        world1 = World(nx.path_graph(4), default_patch_update_function=add_one)

        world1.patches[0].individual_num = 3
        assert world1.patches[0].individual_num == 3
        assert world1.patches[1].individual_num == 0
        assert world1.patches[2].individual_num == 0
        assert world1.patches[3].individual_num == 0

        world1.update_patches()
        world1.update_patches()
        assert world1.patches[0].individual_num == 5
        assert world1.patches[1].individual_num == 2
        assert world1.patches[2].individual_num == 2
        assert world1.patches[3].individual_num == 2

        # Now change the patch_update function for only patch 0
        world1.patches[0].change_update_function(exponential_growth, 2)
        world1.update_patches()
        assert world1.patches[0].individual_num == 10
        assert world1.patches[1].individual_num == 3
        assert world1.patches[2].individual_num == 3
        assert world1.patches[3].individual_num == 3
