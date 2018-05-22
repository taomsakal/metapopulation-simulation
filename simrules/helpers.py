"""
Functions to help construct the simrules.
"""


def has_positive(list_):
    """ Checks if a list_ has a postive value. """
    try:
        for i in list_:
            if i > 0:
                return True
        return False

    except:
        raise Exception("has_positive has problem.")
