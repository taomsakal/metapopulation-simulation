"""General functions used across the program"""
import logging


def pass_(*args, **kwargs):
    """ Empty function for defaults. It accepts any number of parameters. """
    logging.warning("Using the empty pass_() function in the world. This function does nothing.")
    pass


def geometric_growth(num, r):
    """
    Each generation the current number of individuals is multiplied by r

    Args:
        num: a number
        r: the first positional arg patch.update_func_kwargs
    """

    return num + num * r


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
