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



