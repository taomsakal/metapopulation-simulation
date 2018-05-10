"""
This has all the different functions we can use.
The universal is that each function is initialized with a patch, which is the patch that owns it.
"""

def add_one(patch):
    """
    Adds one to the individual number.
    This function is a simple one, mainly for testing.
    """
    patch.individual_num += 1


