"""
Functions to help construct the simrules.
"""
import random


def sum_dicts(l):
    """
    Takes a list of dicts and merges them, summing any overlaps. Assumes that the dicts have values that are numbers.

    Examples:
        sum_dicts([{'a':10, 'b':10}, {'b':2, 'c':10}
        > {'a':10, 'b':12, 'c':10}

    Args:
        l: A list of dictionaries with number values

    Returns:
        A dictionary

    """

    merged_dict = {}
    for dictionary in l:
        for key, value in dictionary.items():
            if key in merged_dict:
                merged_dict[key] += value
            else:
                merged_dict[key] = value

    return merged_dict


def random_index_order(list_):
    """
    Takes a list and outputs a random order of indices.

    This is often used to iterate through patches in a random order.

    ex: [a, b, c] → [0, 2, 1]

    """

    random_order = list(range(0, len(list_)))
    random.shuffle(random_order)
    return random_order


def has_positive(list_):
    """ Checks if a list_ has a postive value. """
    try:
        for i in list_:
            if i > 0:
                return True
        return False

    except:
        raise Exception("has_positive has problem.")


def choose_k(k, dict_):
    """
    Take a dict where each key has a number. Choose k random keys with choice weighted by the values.
    """

    keys, values = zip(*dict_.items())
    return random.choices(keys, values, k=k)



