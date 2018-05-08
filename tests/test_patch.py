import pytest
from patch import Patch

def default_patch():
    return Patch(0)

def test_init_defaults():
    patch = default_patch()
    assert patch.id == 0
    assert patch.individuals == []
    assert patch.update_function == "Pass"
    patch.update()
    assert patch.update_function == "Pass"
    assert patch.individuals == []


def test_init_list():
    patch = Patch(0, individuals=[1, 2, 3, 'a', 'b', 'c'])
    assert patch.individuals == [1, 2, 3, 'a', 'b', 'c']

def test_basic_update():

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

def test_custom_attribute_update():

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
