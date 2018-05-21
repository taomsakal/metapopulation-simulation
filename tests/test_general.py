import pytest
from general import *


def test_sum_dicts():
    assert sum_dicts([{'a': 10, 'b': 10}, {'b': 2, 'c': 10}]) == {'a': 10, 'b': 12, 'c': 10}
