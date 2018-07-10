import pytest
from general import *


def test_within_percent():

    assert within_percent(9, 10, .2) == True
    assert within_percent(10, 10, .2) == True
    assert within_percent(100, 120, 0.9) == True
    assert within_percent(100, 10, 1) == False
    assert within_percent(100, 10, 2) == False
    assert within_percent(100, 10.5, 1000) == True
    assert within_percent(1000.1, 1100, .1, epsilon=100) == True
    assert within_percent(1, 1100, 0, epsilon=100) == False
    assert within_percent(1, 0, 0.1, epsilon=1.1) == True
    assert within_percent(1, 0, 0.1, epsilon=0.1) == False

    # Test ignore sign

    assert within_percent(-9, 10, .2, ignore_sign=True) == True
    assert within_percent(-10, 10, .2, ignore_sign=True) == True
    assert within_percent(-100, 120, 0.9, ignore_sign=True) == True
    assert within_percent(-100, 10, 1, ignore_sign=True) == False
    assert within_percent(-100, 10, 2, ignore_sign=True) == False
    assert within_percent(-100, 10.5, 1000, ignore_sign=True) == True
    assert within_percent(-1000.1, 1100, .1, epsilon=100, ignore_sign=True) == True
    assert within_percent(-1, 1100, 0, epsilon=100, ignore_sign=True) == False
    assert within_percent(-1, 0, 0.1, epsilon=1.1, ignore_sign=True) == True
    assert within_percent(-1, 0, 0.1, epsilon=0.1, ignore_sign=True) == False
