import logging
import pytest
import networkx as nx

from world import World
from patch import Patch
import general
from simrules import testrules


logging.basicConfig(filename='test_world.log', level=logging.DEBUG)
logging.info("--- Started " + "-" * 50)


def add_one(patch):
    """
    Adds one to the individual number.
    This function is a simple one, mainly for testing.
    """
    patch.populations += 1


def add_double(patch):
    """ Doubles the number of populations. """
    patch.populations = general.geometric_growth(patch.populations, 2)

def complete_world():
    """ Returns a world with the world map a K_10 graph and all default patch_update functions"""
    return World(testrules.AddOne(nx.complete_graph(5)))

def path_world():
    """ Return a world that's a path graph of 4 nodes. """
    return World(testrules.AddOne(nx.path_graph(4)))


def trivial_world():
    """Return a world made up of a single node"""
    return World(testrules.AddOne(nx.complete_graph(1)))


def default_patch():
    """Returns a patch with id 0, in a trivial world"""
    return Patch(0, trivial_world())

# =========================

class TestInit:
    def test_patch_generation(self):
        """ Test that correct number of patches are generated. """

        for n in range(1, 20):
            rules1 = testrules.AddOne(nx.complete_graph(n))
            rules2 = testrules.AddOne(nx.erdos_renyi_graph(n, 0.2))
            rules3 = testrules.AddOne(nx.barabasi_albert_graph(n + 1, 1))

            world1 = World(rules1)
            world2 = World(rules2)
            world3 = World(rules3)

            assert len(world1.patches) == n
            assert len(world2.patches) == n
            assert len(world3.patches) == n + 1  # Some parameter values for ba graph forces n > 1, so offset by one.


    def test_make_world(self):
        world1 = complete_world()

        assert world1.worldmap is not None
        assert world1.name == "World 1"

        assert world1.patches[0].populations == 0
        assert len(world1.patches) == 5

        world2 = World(testrules.AddOne(nx.path_graph(100)), name="wowee")

        assert world2.worldmap is not None
        assert world2.name == "wowee"

        assert world2.patches[0].populations == 0
        assert len(world2.patches) == 100


    def test_worldmap(self):
        world1 = complete_world()

        assert list(world1.worldmap.nodes()) == [0, 1, 2, 3, 4]
        assert list(world1.worldmap.neighbors(0)) == [1, 2, 3, 4]
        assert list(world1.worldmap[0]) == [1, 2, 3, 4]

        assert world1.patches[0].neighbor_ids() == [1, 2, 3, 4]

class TestPatchUpdates:

    def test_add_one(self):

        world1 = World(complete_world())

        assert world1.patches[0].populations == 0
        world1.update_patches()
        assert world1.patches[0].populations == 1

        world1.update_patches()
        for patch in world1.patches:
            assert patch.populations == 2

        for i in range(1, 100):
            world1.update_patches()
            for patch in world1.patches:
                assert patch.populations == 2 + i

    def test_add_one_complex(self):

        world1 = World(path_world())

        world1.patches[0].populations = 3
        assert world1.patches[0].populations == 3
        assert world1.patches[1].populations == 0
        assert world1.patches[2].populations == 0
        assert world1.patches[3].populations == 0

        world1.update_patches()
        world1.update_patches()
        assert world1.patches[0].populations == 5
        assert world1.patches[1].populations == 2
        assert world1.patches[2].populations == 2
        assert world1.patches[3].populations == 2

        # Change the patch_update function to the same function
        world1.patches[0].update_function = add_one
        world1.update_patches()
        assert world1.patches[0].populations == 6
        assert world1.patches[1].populations == 3
        assert world1.patches[2].populations == 3
        assert world1.patches[3].populations == 3

        # Now change the patch_update function for only patch 0
        world1.patches[0].update_function = add_double
        world1.update_patches()
        assert world1.patches[0].populations == 6 + 12
        assert world1.patches[1].populations == 4
        assert world1.patches[2].populations == 4
        assert world1.patches[3].populations == 4
