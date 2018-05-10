import pytest
import networkx as nx

from world import World

def test_patch_generation():
    """ Test that correct number of patches are generated. """

    for n in range(1,20):
        map1 = nx.complete_graph(n)
        map2 = nx.erdos_renyi_graph(n, 0.2)
        map3 = nx.barabasi_albert_graph(n+1, 1)

        world1 = World(map1, None, None, None, None)
        world2 = World(map2, None, None, None, None)
        world3 = World(map3, None, None, None, None)

        assert len(world1.patches) == n
        assert len(world2.patches) == n
        assert len(world3.patches) == n+1  # Some parameter values for ba graph forces n > 1, so offset by one.

