"""
This has all the different functions we can use.

All functions should list additional patch/world atttributes they need, and raise Exceptions if they are not met

"""


def add_one(patch):
    """
    Adds one to the individual number.
    This function is a simple one, mainly for testing.
    """
    patch.individuals += 1


def add_double(patch):
    """ Doubles the number of individuals. """
    patch.individuals = helper.geometric_growth(patch.individuals, 2)


def kelly_cool_func(patch):
    patch.individuals = patch.individuals ** 1.6


# Below are helper functions for constructing the patch update functions.
# ===================================================================

class Helper:
    """
    This is simply an organizational class to emphasize that we cannot use these as functions directly.
    """

    def geometric_growth(self, num, r):
        """
        Each generation the current number of individuals is multiplied by r

        Args:
            num: a number
            r: the first positional arg patch.update_func_kwargs
        """

        return num + num * r


helper = Helper()
