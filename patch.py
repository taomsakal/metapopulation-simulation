"""
The Patch class. This contains three parts

1. The id of the patch (where it is on the world map)
2. The update function that moves the patch forward one time step.
3. A list of individuals in the patch.

Any other attributes should be defined during patch creation. This can be done with
> patch.attribute_name = attribute_value
"""

import logging
from collections import Callable


class Patch:

    def __init__(self, id, update_function="Pass", individuals="Empty List"):
        """
        Args:
            id: The id that corresponds to the patch in the world map
            update_function: The function that runs when we
            individuals: A list of individuals
        """

        # Init values
        self.id = id
        self.update_function = update_function
        self.individuals = individuals
        if individuals == "Empty List":
            self.individuals = []

    def update(self):
        """
        Update the patch using whatever update function we've chosen.
        """

        if self.update_function == "Pass":
            logging.warning("No update function for patch {}.".format(self.id))
            pass
        else:
            try:
                self.update_function(self)
            except:
                if isinstance(self.update_function, Callable):
                    TypeError("update_function() for patch {} much be a function, not {}".format(self.id, type(
                        self.update_function)))
                else:
                    raise Exception("Error with update_function for patch {}.".format(self.id))

    def census(self):
        pass
        #todo: log history of each patch
