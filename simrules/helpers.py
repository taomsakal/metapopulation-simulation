"""
Functions to help construct the simrules.
"""
import os
import logging
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


def merge_dicts(l):
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


def sum_dict(dict_):
    """ Sums all the values of a numeric-valued dictionary together. """

    sum_ = 0
    for value in dict_.values():
        sum_ += value

    return sum_


def init_csv(path, name, header):
    """
    creates a csv file with the header we specify.
    Automatically adds an iteration and init_resources_per_patch column.

    Args:
        path: the path to the folder the file lives in
        name: <filename>.csv
        header: list of strings to write in the header
    """

    # Make the Directory if needed
    if not os.path.exists(path):
        logging.info(f"Initializing the save data files in {path}")
        os.makedirs(path)

    with open(f'{path}/{name}', 'w+') as file:
        file.truncate()  # Make sure file is empty

        # Make the headers of the CSV file
        for i in header:
            file.write(i)
            file.write(',')
        file.write("\n")

    return file



def random_probs(n):
    """
    Makes a list of random probabilities. Used to give input for large
    Args:
        n: number of strains

    Returns:
        A list of random probabilities length n
    """

    return [random.random() for x in range(0, n)]


def spaced_probs(n):
    """
    Makes a vector for the n strains with evenly spaced probabilities between them.
    Always include the prob of 1 too
    Args:
        n:
        step:

    Returns:

    """

    l = []
    for i in range(0, n):
        l.append(i / n)  # Normalize so that between 0 and one
    l.append(1)

    return l

