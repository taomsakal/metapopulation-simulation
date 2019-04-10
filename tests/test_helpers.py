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

        # Check that doesn't  always output original list
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


def test_find_winner():

    # Below are per strain populations.
    # The function should return the index of the winning strains
    # The winning strain is the one with lowest sporulation chance, so the lowest value

    # Sample Populations
    a = [10, 2, 3, 4]
    b = [0, 0, 0, 0]
    c = [0, 1, 0, 1]


    d = [0, 1.5]
    e = [0, 0]
    f = [100, 100]


    sc4 = [1, .8, .04, .10]
    sc42 = [0, 1, .99, .5]
    sc43 = [0.1, 0.1, .99, .5]

    sc2 = [.1, 0]
    sc22 = [.1, .1]
    sc23 = [.23, .23]





    assert find_winner(a, b, sc4) == [2]  # All present so lowest sporulation chance wins. This is strain 2
    assert find_winner(b, a, sc4, germinate_spores=True) == [2]  # Same as above
    assert find_winner(b, a, sc4, germinate_spores=False) == []  # Empty so no winners
    assert find_winner(c, b, sc4) == [3]

    assert find_winner(a, b, sc42) == [0]  # All present so lowest sporulation chance wins. This is strain 0
    assert find_winner(b, a, sc42, germinate_spores=True) == [0]  # Same as above
    assert find_winner(b, a, sc42, germinate_spores=False) == []  # Empty so no winners
    assert find_winner(c, b, sc42) == [3]

    assert find_winner(a, b, sc43) == [0, 1]  # All present so lowest sporulation chance wins. This is strain 0 and 1
    assert find_winner(b, a, sc43, germinate_spores=True) == [0, 1]  # Same as above
    assert find_winner(b, a, sc43, germinate_spores=False) == []  # Empty so no winners
    assert find_winner(c, b, sc43) == [1]


    # For two strains
    assert find_winner(d, e, sc2) == [1]
    assert find_winner(d, e, sc22) == [1]
    assert find_winner(d, e, sc23) == [1]

    assert find_winner(f, d, sc2) == [1]
    assert find_winner(f, d, sc22) == [0, 1]
    assert find_winner(f, d, sc23) == [0, 1]

    assert find_winner(f, d, sc2, germinate_spores=True) == [1]
    assert find_winner(f, d, sc22, germinate_spores=True) == [0, 1]
    assert find_winner(f, d, sc23, germinate_spores=True) == [0, 1]

    assert find_winner(e, f, sc2, germinate_spores=True) == [1]
    assert find_winner(e, f, sc22, germinate_spores=True) == [0, 1]
    assert find_winner(e, f, sc23, germinate_spores=True) == [0, 1]

    # For a single strain

    assert find_winner([0], [2], [.2], germinate_spores=True) == [0]
    assert find_winner([0], [0], [.2], germinate_spores=True) == []
    assert find_winner([0], [0], [0], germinate_spores=True) == []
    assert find_winner([0], [0], [1], germinate_spores=True) == []
    assert find_winner([1], [23132], [1], germinate_spores=True) == [0]

    assert find_winner([0], [0], [1]) == []
    assert find_winner([0], [1], [.1]) == []
    assert find_winner([0.1], [1], [.1]) == [0]
    assert find_winner([0.1], [1], [0]) == [0]
    assert find_winner([0.1], [1], [1]) == [0]

    with pytest.raises(AssertionError):
        find_winner([11111], [1], [1111])
