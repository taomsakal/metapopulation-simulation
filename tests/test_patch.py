import pytest
import logging
import networkx as nx

from world import World
from patch import Patch
import general
from simrules import testrules

logging.basicConfig(filename='test_patch.log', level=logging.DEBUG)
logging.info('Started')


def add_double(patch):
    """ Doubles the number of populations. """
    patch.populations = general.geometric_growth(patch.populations, 2)


def complete_world():
    """ Returns a world with the world map a K_10 graph and all default patch_update functions"""
    return World(testrules.AddOne(nx.complete_graph(10)))


def path_world():
    """ Return a world that's a path graph of 4 nodes. """
    return World(testrules.AddOne(nx.path_graph(4)))


def trivial_world():
    """Return a world made up of a single node"""
    return World(testrules.AddOne(nx.complete_graph(1)))


def default_patch():
    """Returns a patch with id 0, in a trivial world"""
    return Patch(0, trivial_world())


class TestSetup:

    def test_init_defaults(self):
        patch = default_patch()
        assert patch.id == 0
        assert patch.populations == 0
        patch.update()
        assert patch.populations == 1

    def test_init_list(self):
        patch = Patch(0, trivial_world(), initial_populations=[1, 2, 3, 'a', 'b', 'c'])
        assert patch.populations == [1, 2, 3, 'a', 'b', 'c']

    def test_basic_update(self):
        def update_function(patch):
            patch.populations.append("a")

        patch = Patch(0, trivial_world(), initial_populations=[])
        patch.change_update_function(update_function)

        assert patch.populations == []
        patch.update()
        assert patch.populations == ['a']
        patch.update()
        assert patch.populations == ['a', 'a']
        patch.update()
        patch.update()
        patch.update()
        assert patch.populations == ['a', 'a', 'a', 'a', 'a']

    def test_custom_attribute_update(self):
        def update_function(patch):
            patch.populations.append(patch.type)

        patch = Patch(0, trivial_world(), initial_populations=['a'])
        patch.change_update_function(update_function)
        patch.type = 'b'

        assert patch.populations == ['a']
        patch.update()
        assert patch.populations == ['a', 'b']
        patch.update()
        assert patch.populations == ['a', 'b', 'b']
        patch.update()
        patch.update()
        patch.update()
        assert patch.populations == ['a', 'b', 'b', 'b', 'b', 'b']

    def test_add_one_ind_num(self):
        patch = Patch(0, trivial_world(), initial_populations=1)
        assert patch.populations == 1
        patch.update()
        assert patch.populations == 2
        patch.update()
        assert patch.populations == 3
        patch.update()
        assert patch.populations == 4
        assert patch.id == 0


class TestMap():
    """ Test if the patches play well with the worldmap """

    def test_neighbors_complete_world(self):
        world = complete_world()

        assert world.patches[0].id == 0
        assert world.patches[1].id == 1
        assert len(world.patches) == 10

        logging.info(world.patches[0].neighbor_ids())
        assert world.patches[0].neighbor_ids() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

        for i, patch in enumerate(world.patches):
            nids = patch.neighbor_ids()
            l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            l.remove(i)
            assert nids == l

    def test_neighbors_trivial_world(self):
        world = trivial_world()

        assert world.patches[0].id == 0
        assert len(world.patches) == 1

        logging.info(world.patches[0].neighbor_ids())
        assert world.patches[0].neighbor_ids() == []

    def test_neighbors_path_world(self):
        world = path_world()

        assert world.patches[0].id == 0
        assert world.patches[3].id == 3
        assert len(world.patches) == 4

        logging.info(world.patches[0].neighbor_ids())
        assert world.patches[0].neighbor_ids() == [1]
        assert world.patches[1].neighbor_ids() == [0, 2]
        assert world.patches[2].neighbor_ids() == [1, 3]
        assert world.patches[3].neighbor_ids() == [2]
