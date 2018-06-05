"""General functions used across the program"""
import logging


def pass_(*args, **kwargs):
    """ Empty function for defaults. It accepts any number of parameters. """
    logging.warning("Using the empty pass_() function in the world. This function does nothing.")
    pass


# Todo: Make this specific for each class


def geometric_growth(num, r):
    """
    Each generation the current number of individuals is multiplied by r

    Args:
        num: a number
        r: the first positional arg patch.update_func_kwargs
    """

    return num + num * r


def within_percent(num, reference_num, p, epsilon=0):
    """
    Returns true if num is within a certain percent of the refence num.

    epsilon is added to the error thershold (useful for if the reference number is 0

    Examples:
        Is 9 within 20% of 10?
        >>> within_percent(9, 10, 0.2) == True

    """

    margin = p * reference_num
    margin += epsilon


    if reference_num - margin <= num <= reference_num + margin:
        return True

    return False
