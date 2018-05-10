"""
A networkx graph that describes where each patch is in relation to the others.
Each node has an id, and the patches correspond to the node that shares their id.

Note that the worldmap is just a map; no information is contained in the nodes.

"""



# class Worldmap():
#     """ The worldmap networkx graph. """
#
#     def __init__(self, nx_graph):
#         """
#         The worldmap is a networkx graph where nodes are patches and connections are immediate neighbors.
#
#         Args:
#             nx_graph: A networkx graph
#         """
