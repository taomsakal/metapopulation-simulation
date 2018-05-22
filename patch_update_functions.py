"""
This has all the different functions we can use.

All functions should list additional patch/world atttributes they need, and raise Exceptions if they are not met

"""
import logging
import general






def three_cases(patch):
    """
    Have three cases: if both types on, only one type, or none. Give output values for these.
    """
    if not isinstance(patch.populations, dict):
        patch.populations = {}
        logging.warning(
            f"three_cases() is setting populations in {patch.id} to be an empty dict, because it wasn't before.")
    populations = patch.populations

    if populations['Competitors'] > 0:
        has_competitor = True
    else:
        has_competitor = False

    if populations['Colonizers'] > 0:
        has_colonizer = True
    else:
        has_colonizer = False

    if has_competitor and has_colonizer:
        populations['Colonizers'] = 50
        populations['Competitors'] = 150
    elif has_competitor:
        populations['Colonizers'] = 0
        populations['Competitors'] = 250
    elif has_colonizer:
        populations['Colonizers'] = 200
        populations['Competitors'] = 0
    else:
        populations['Colonizers'] = 0
        populations['Competitors'] = 0


