"""
Functions to help construct the simrules.
"""
import random


def typeIIresponse(resource_density, attack_rate, holding_time, max_=float('inf'), min_=0):
    """
    Returns the number of prey eaten, according to a type II functional response.

    Args:
        min: The minimum number that can be returned
        max: The maximum number that can be returned
        resource_density: Resource density
        attack_rate: The attack rate of predator
        holding_time: The holding time of the predator

    Returns:
        A float

    """


    num = (attack_rate * resource_density) / (1 + attack_rate * holding_time * resource_density)

    num = min(num, max_)
    num = max(min_, num)

    return num

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



