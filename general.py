"""General functions used across the program"""
import logging

def pass_(*args, **kwargs):
    """ Empty function for defaults. It accepts any number of parameters. """
    logging.warning("Using the empty pass_() function in the world. This function does nothing.")
    pass
