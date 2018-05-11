import logging
import pytest
import networkx as nx

from world import World

logging.basicConfig(filename='test_world.log', level=logging.DEBUG)
logging.info("--- Started " + "-" * 50)


def complete_world():
    """ Returns a world with the world map a K_10 graph and all default update functions"""
    return World(nx.complete_graph(5))


def test_patch_generation():
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


def test_make_world():
    world1 = complete_world()

    assert world1.worldmap is not None
    assert world1.name == "World 1"


def test_worldmap():
    world1 = complete_world()

    assert list(world1.worldmap.nodes()) == [0, 1, 2, 3, 4]
    assert list(world1.worldmap.neighbors(0)) == [1, 2, 3, 4]
    assert list(world1.worldmap[0]) == [1, 2, 3, 4]

    assert world1.patches[0].neighbor_ids() == [1, 2, 3, 4]
