"""
This has all the different functions we can use.

All functions should list additional patch/world atttributes they need, and raise Exceptions if they are not met

"""
import logging
import general

def add_one(patch):
    """
    Adds one to the individual number.
    This function is a simple one, mainly for testing.
    """
    patch.individuals += 1


def add_double(patch):
    """ Doubles the number of individuals. """
    patch.individuals = general.geometric_growth(patch.individuals, 2)


def kelly_cool_func(patch)
    patch.individuals['Competitor'] = patch.individuals['Competitor'] ** 1.6
    patch.individuals['Colonizer'] = patch.individuals['Colonizer'] ** 1.2


def three_cases(patch):
    """
    Have three cases: if both types on, only one type, or none. Give output values for these.
    """
    if not isinstance(patch.individuals, dict):
        patch.individuals = {}
        logging.warning(
            f"three_cases() is setting individuals in {patch.id} to be an empty dict, because it wasn't before.")
    individuals = patch.individuals

    if individuals['Competitors'] > 0:
        has_competitor = True
    else:
        has_competitor = False

    if individuals['Colonizers'] > 0:
        has_colonizer = True
    else:
        has_colonizer = False

    if has_competitor and has_colonizer:
        individuals['Colonizers'] = 50
        individuals['Competitors'] = 150
    elif has_competitor:
        individuals['Colonizers'] = 0
        individuals['Competitors'] = 250
    elif has_colonizer:
        individuals['Colonizers'] = 200
        individuals['Competitors'] = 0
    else:
        individuals['Colonizers'] = 0
        individuals['Competitors'] = 0


