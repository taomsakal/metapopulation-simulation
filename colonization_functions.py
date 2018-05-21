from collections import defaultdict
from general import sum_dicts

# Todo: this function isn't finished.
def mush_and_redistribute(world):
    """
    This does three things.

    1. Take a sum of all competitors and colonizers
    2. Flies come eat some.
    3. Each fly visits a random patch and distributes them.

    Currently the function assumes that all patches die during it.

    """
    # Make a list of all the individuals and merge them into one big dictionary.
    dict_list = []
    for patch in world:
        dict_list.append(patch.individuals)
    merged_dict = sum_dicts(dict_list)

    total_competitors = merged_dict['Competitors']
    total_colonizers = merged_dict['Colonizers']

    # Reset all patches, make sure that the individuals are set correctly

    # Now for each patch the fly will pick some yeast up, digest some, and drop the survivors in a random patch.
    def num_flies():
        """ Function to generate a number of flies. """
        return 10

    def pickup(competitors, colonizers):
        pass  # todo

    for i in range(0, num_flies()):
        hitchhikers = pickup(total_competitors, total_colonizers)
        hitchhikers[0] *= .2  # 20% of competitors survive the gut
        hitchhikers[1] *= .8  # 80% of colonizers survive

        # Drop off hitchhikers to new patch
        drop_patch = general.random_patch(world)
        drop_patch.individuals['Competitors'] = hitchhikers[0]
        drop_patch.individuals['Colonizers'] = hitchhikers[1]


