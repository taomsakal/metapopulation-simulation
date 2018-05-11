import pytest
import logging
import networkx as nx

from world import World
from patch import Patch

logging.basicConfig(filename='test_patch.log', level=logging.DEBUG)
logging.info('Started')


def complete_world():
    """ Returns a world with the world map a K_10 graph and all default update functions"""
    return World(nx.complete_graph(10))


def trivial_world():
    """Return a world made up of a single node"""
    return World(nx.complete_graph(1))


def default_patch():
    """Returns a patch with id 0, in a trivial world"""
    return Patch(0, trivial_world())


class TestSetup:

    def test_init_defaults(self):
        patch = default_patch()
        assert patch.id == 0
        assert patch.individuals == []
        assert patch.individual_num == 0
        patch.update()
        assert patch.individuals == []
        assert patch.individual_num == 0

    def test_init_list(self):
        patch = Patch(0, trivial_world(), individuals=[1, 2, 3, 'a', 'b', 'c'])
        assert patch.individuals == [1, 2, 3, 'a', 'b', 'c']
        assert patch.individual_num == 0

    def test_basic_update(self):
        def update_function(patch):
            patch.individuals.append("a")

        patch = Patch(0, trivial_world(), update_function=update_function)

        assert patch.individuals == []
        patch.update()
        assert patch.individuals == ['a']
        patch.update()
        assert patch.individuals == ['a', 'a']
        patch.update()
        patch.update()
        patch.update()
        assert patch.individuals == ['a', 'a', 'a', 'a', 'a']
        assert patch.individual_num == 0

    def test_custom_attribute_update(self):
        def update_function(patch):
            patch.individuals.append(patch.type)

        patch = Patch(0, trivial_world(), update_function=update_function, individuals=['a'])
        patch.type = 'b'

        assert patch.individuals == ['a']
        patch.update()
        assert patch.individuals == ['a', 'b']
        patch.update()
        assert patch.individuals == ['a', 'b', 'b']
        patch.update()
        patch.update()
        patch.update()
        assert patch.individuals == ['a', 'b', 'b', 'b', 'b', 'b']

    def test_add_one_ind_num(self):
        from patch_update_functions import add_one
        patch = Patch(0, trivial_world(), update_function=add_one, individual_num=1)
        assert patch.individual_num == 1
        patch.update()
        assert patch.individual_num == 2
        patch.update()
        assert patch.individual_num == 3
        patch.update()
        assert patch.individual_num == 4
        assert patch.individuals == []
        assert patch.id == 0


class TestMap():
    """ Test if the patches play well with the worldmap """

    def test_neighbors(self):
        world = complete_world()

        assert world.patches[0].id == 0
        assert world.patches[1].id == 1
        assert len(world.patches) == 10

        logging.info(world.patches[0].neighbor_ids())
        assert world.patches[0].neighbor_ids() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

        for n in range(0, 10):
            nids = world.patches[n].neighbor_ids()
            assert nids == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].remove(n)
