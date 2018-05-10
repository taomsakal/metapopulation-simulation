import pytest
import networkx as nx

from patch import Patch

def complete_world:

    return World()

def default_patch():
    return Patch(0)

class TestSetup():

    def test_init_defaults(self):
        patch = default_patch()
        assert patch.id == 0
        assert patch.individuals == []
        assert patch.update_function == "Pass"
        assert patch.individual_num == 0
        patch.update()
        assert patch.update_function == "Pass"
        assert patch.individuals == []
        assert patch.individual_num == 0


    def test_init_list(self):
        patch = Patch(0, individuals=[1, 2, 3, 'a', 'b', 'c'])
        assert patch.individuals == [1, 2, 3, 'a', 'b', 'c']
        assert patch.individual_num == 0

    def test_basic_update(self):

        def update_function(patch):
            patch.individuals.append("a")

        patch = Patch(0, update_function=update_function)

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

        patch = Patch(0, update_function=update_function, individuals=['a'])
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
        patch = Patch(0, update_function=add_one, individual_num=1)
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


    test_neighbors():



