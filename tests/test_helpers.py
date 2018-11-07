import pytest
from simrules.helpers import *


def test_random_index_order():
    list_ = ['a', 23, 0]

    was_different = False
    for i in range(0, 100):

        newlist = random_index_order(list_)

        # Check if legal list
        assert newlist == [0, 1, 2] or newlist == [1, 0, 2] or newlist == [1, 2, 0] or newlist == [0, 2, 1] \
               or newlist == [2, 1, 0] or newlist == [2, 0, 1]

        # Check that doesn't always output original list
        if newlist != [0, 1, 2]:
            was_different = True

    assert was_different


def test_choose_k():
    k = 1
    d = {'a': 1, 'b': 1, 'c': 10}
    c = choose_k(k, d)

    assert c == ['a'] or c == ['b'] or c == ['c']

    k = 1
    d = {'a': 100, 'b': 0, 'c': 0}
    c = choose_k(k, d)
    assert c == ['a']
    k = 3
    c = choose_k(k, d)
    assert c == ['a', 'a', 'a']

    k = 100
    d = {'a': 1, 'b': 1, 'c': 1}
    c = choose_k(k, d)
    assert 'a' in c
    assert 'b' in c
    assert 'c' in c


def test_merge_dicts():
    assert merge_dicts([{'a': 10, 'b': 10}, {'b': 2, 'c': 10}]) == {'a': 10, 'b': 12, 'c': 10}


def test_sum_dict():
    assert sum_dict({}) == 0
    assert sum_dict({'a': 0}) == 0
    assert sum_dict({'a': 0, 'b': 0}) == 0
    assert sum_dict({'a': 0, 'b': 1}) == 1
    assert sum_dict({'a': 0, 'b': 1, 'c': 2}) == 3
    assert sum_dict({'a': 0, 'b': 1, 'c': 2, 'd': .3}) == 3.3


def test_has_positive():
    a = [1, 2, 3]
    b = [0, 0, 0, 0, 0, 1]
    c = [0, 0, 0, 0, 0, -1]
    d = []
    e = [-2, -2]
    f = [-2, 100000]
    g = [0]

    assert has_positive(a) == True
    assert has_positive(b) == True
    assert has_positive(c) == False
    assert has_positive(d) == False
    assert has_positive(e) == False
    assert has_positive(f) == True
    assert has_positive(g) == False

