"""
This has all the different functions we can use.
The universal is that each function is initialized with a patch, which is the patch that owns it.

If the function has arguments other than patch then these must be keyword arguments, and
we must also change update_function_parameters.
"""

def add_one(patch, *args, **kwargs):
    """
    Adds one to the individual number.
    This function is a simple one, mainly for testing.
    """
    patch.individual_num += 1

def exponential_growth(patch, r, *args, **kwargs):
    """
    Each generation the current number of individuals is multiplied by r

    Args:
        patch: the patch the function is operating on.
        r: the reproductive rate
    """

    patch.individual_num *= r

