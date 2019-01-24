"""
This runs a few test simulations to make sure they work and spit out reasonable results.
"""

import random
import main
from world import World
from simrules.NStrainsSimple import NStrainsSimple
from simrules.TwoStrain import TwoStrain
from AM_programs.NStrain import NStrain
from general import within_percent
import networkx as nx
from simrules import helpers

def random_simulation(n):
    """ Makes a random NSTrain simulation with up to n strains and default parms"""

    num_strains = random.randint(1, n)
    rules = NStrain(num_strains, folder_name="test_no_death", spore_chance=helpers.random_probs(num_strains),
                   germ_chance=helpers.random_probs(num_strains), fly_s_survival=helpers.random_probs(num_strains),
                   fly_v_survival=helpers.random_probs(num_strains))
    rules.update_mode = random.choice(["discrete", "eq"])
    rules.colonize_mode = random.choice(["fly", "probabilities"])
    rules.fly_stomach_size = random.choice([1, 2, 10, 'type 2'])
    return rules

class TestNStrainsSimple:

    def test_no_death(self):
        """ Test that all populations spread """

        for i in range(0, 5):

            world = World(NStrainsSimple(3, nx.complete_graph(10), 0.0, 1.001, 400))
            main.simulate(world)

            for patch in world.patches:
                for population in patch.populations:
                    assert population > 0

    def test_high_death(self):
        """ Test that populations go extinct under a high dead rate """

        for i in range(0, 5):

            world = World(NStrainsSimple(2, nx.complete_graph(10), 0.5, 1.1, 500))
            main.simulate(world)

            for patch in world.patches:
                for population in patch.populations:
                    assert population == 0

    def test_stress(self):
        """ See if crashes during a long run or a heavy one"""

        # Long run
        world = World(NStrainsSimple(20, nx.complete_graph(5), 0.05, 1.0001, 100))
        main.simulate(world)
        assert True

        # High node run
        world = World(NStrainsSimple(81, nx.path_graph(99), 0.05, 1.0001, 10))
        main.simulate(world)
        assert True

    def test_trivial(self):
        """ See if crashes during a trivial graph """

        world = World(NStrainsSimple(1, nx.complete_graph(1), 0.0, 1.0001, 100))
        main.simulate(world)
        assert world.patches[0].populations[0] > 1
        world = World(NStrainsSimple(20, nx.complete_graph(1), 0.5, 1.0001, 100))
        main.simulate(world)
        assert world.patches[0].populations[0] == 0

    def test_line(self):
        """ See if crashes when on a line graph """
        world = World(NStrainsSimple(3, nx.path_graph(5), 0.01, 1.001, 100))
        main.simulate(world)

        assert True

class TestNStrain:


    # Todo: Import the helpers random number generators and fix the rules for each test. Then iterate through a random number of num_cases cases.

    def test_no_death(self):
        """ Test that all populations spread when there is no death and patches do not die"""

        for i in range(0, 5):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0
            rules.mu_s = 0
            rules.mu_R = 0
            rules.dt = .01
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 1000
            rules.num_flies = 0
            rules.fly_s_survival = [1]*rules.num_strains
            rules.fly_v_survival = [1]*rules.num_strains
            rules.prob_death = 0  # Make sure that dead prob is low
            rules.update_mode = random.choice(['eq', 'discrete'])
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) > 0
                assert sum(patch.s_populations) > 0

    def test_no_death_with_flies_that_dont_eat(self):
        """ Test that all populations spread when there is no death and patches do not die"""

        for i in range(0, 5):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0
            rules.mu_s = 0
            rules.mu_R = 0
            rules.dt = .01
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 1000
            rules.num_flies = 10
            rules.fly_stomach_size = 0
            rules.fly_s_survival = [1]*rules.num_strains
            rules.fly_v_survival = [1]*rules.num_strains
            rules.prob_death = 0  # Make sure that dead prob is low
            rules.update_mode = random.choice(['eq', 'discrete'])
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) > 0
                assert sum(patch.s_populations) > 0

    def test_no_death_with_flies(self):
        """ Test that all populations spread when there is no death and patches do not die"""
        # Todo: This test always fails if the stomach size is not type 2. I cannot figure out why. But everything else works?

        for i in range(0, 5):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0
            rules.mu_s = 0
            rules.mu_R = 0
            rules.dt = .01
            rules.resources = 500
            rules.gamma = 10
            rules.stop_time = 1000
            rules.num_flies = 3
            rules.fly_stomach_size = 'type 2'
            rules.fly_s_survival = [1]*rules.num_strains
            rules.fly_v_survival = [1]*rules.num_strains
            rules.prob_death = 0 # Make sure that dead prob is low
            rules.update_mode = random.choice(['eq', 'discrete'])
            rules.germinate_on_drop = True
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) > 0
                assert sum(patch.s_populations) > 0



    def test_heavy_death_in_patches(self):
        """ Test that all populations die when patch death is large, even if all populations are immortal."""

        for i in range(0, 5):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0
            rules.mu_s = 0
            rules.mu_R = 0
            rules.resources = 50
            rules.stop_time = 400
            rules.num_flies = 5
            rules.prob_death = 0.5  # Make this high
            world = World(rules)
            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) == 0
                assert sum(patch.s_populations) == 0

    def test_high_death(self):
        """ Test that populations go essentially extinct under a high dead rate """

        for i in range(0, 5):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.99
            rules.mu_s = 0.99
            rules.mu_R = 0.99
            rules.prob_death = 0
            rules.resources = 10
            rules.stop_time = 10000
            world = World(rules)
            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) < 1
                assert sum(patch.v_populations) >= 0
                assert sum(patch.s_populations) < 1
                assert sum(patch.s_populations) >= 0

    def test_full_death(self):
        """ Test that populations go totally extinct under a mortality rate of 1 """

        for i in range(0, 5):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 1
            rules.mu_s = 1
            rules.mu_R = 1
            rules.dt = 1
            rules.prob_death = 0
            rules.resources = 1
            rules.stop_time = 10000
            world = World(rules)
            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) < 1
                assert sum(patch.v_populations) >= 0
                assert sum(patch.s_populations) < 1
                assert sum(patch.s_populations) >= 0

    def test_many_strain(self):
        """ See if crashes during a many strain run"""

        for i in range(0, 5):
            # Long run
            rules = random_simulation(100)
            rules.worldmap = nx.complete_graph(5)
            rules.resources = 500
            rules.stop_time = 400
            world = World(rules)
            main.simulate(world)
            assert True

    def test_many_node_run(self):

        for i in range(0, 5):
            # High node run
            rules = random_simulation(20)
            rules.worldmap = nx.complete_graph(random.randint(1, 300))
            rules.resources = 2000
            rules.stop_time = 10
            world = World(rules)
            main.simulate(world)
            assert True

    def test_line(self):
        """ See if crashes when on a line graph """
        rules = random_simulation(10)
        rules.worldmap = nx.path_graph(5)
        rules.mu_v = 0.01
        rules.mu_s = 0.01
        rules.mu_R = 0.01
        rules.resources = 75
        rules.stop_time = 100
        world = World(rules)
        main.simulate(world)

        assert True

    def test_2_strain_1_with_no_colonization(self):
        """ Makes sure that if there are two strains and one cannot survive the fly then the long term eqs are equal
        That is, the second strain does not effect the long term dynamics

        We need to up the patch number for this test else stochasticity can cause it to fail
        """


        for i in range(0, 5):
            # This world is with two strains, but one cannot survive the fly
            # This test has a high percent error because it sometimes takes a long time fall to correct values
            rules = NStrain(2, folder_name="test", fly_s_survival=[.5, 0], fly_v_survival=[.8, 0], spore_chance=[.2, .8], germ_chance=[.2, .2])
            rules.worldmap = nx.complete_graph(60)
            rules.stop_time = 200000
            rules.dt = 1
            rules.prob_death = 0.005
            rules.update_mode = random.choice(['eq','discrete'])
            world = World(rules)
            main.run(world)

            # This world is with only the first strain
            rules2 = NStrain(1, folder_name="test", fly_s_survival=[.5], fly_v_survival=[.8], spore_chance=[.2], germ_chance=[.2])
            rules2.worldmap = nx.complete_graph(60)
            rules2.stop_time = 200000
            rules2.dt = 1
            rules2.prob_death = 0.005
            random.choice(['eq', 'discrete'])
            world2 = World(rules2)
            main.run(world2)


        world1pop = world.rules.sum_populations(world)[0]
        world2pop = world2.rules.sum_populations(world2)[0]

        assert within_percent(world1pop, world2pop, 0.1, epsilon=0.0005)


    def test_equlibrium_discrete_mode(self):
        """ Test that the system goes to the expected equilibrium. (Within 10%) """

        for i in range(0, 10):

            # Important: Germ chance must be set to 0 for this to work
            rules = NStrain(2, folder_name="test", fly_v_survival=[.2, .2], fly_s_survival=[.8, .8], spore_chance=[.2, .8], germ_chance=[0, 0])

            # Now setup specific parameters
            rules.c = 0.1  # Consumption rate for init_resources_per_patch.
            rules.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
            rules.mu_v = 0.1  # Background death rate for vegetative cells
            rules.mu_s = 0.05  # Background death rate for sporulated cells
            rules.mu_R = 0.01  # "death" rate for init_resources_per_patch.
            rules.gamma = 1  # Rate of resource renewal
            rules.resources = 200
            rules.dt = 1  # Timestep size
            rules.worldmap = nx.complete_graph(10)  # The worldmap
            rules.prob_death = 0.00  # Probability of a patch dying.
            rules.stop_time = 10000  # Iterations to run
            rules.num_flies = 0  # Number of flies each colonization event
            rules.fly_attack_rate = 0.3
            rules.fly_handling_time = 0.3
            rules.fly_stomach_size = random.choice([1,2,3,4,'type2'])
            rules.update_mode = 'discerete'
            rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization

            world = World(rules)

            main.run(world)

            for patch in world.patches:

                # First possible equilibrium
                # 0 → Competitor, 1 → Colonizer
                try:
                    assert within_percent(patch.resources, 6.25, 0.05)
                    assert within_percent(patch.v_populations[0], 1.5, 0.05)
                    assert within_percent(patch.s_populations[0], 0.75, 0.05)
                    assert within_percent(patch.v_populations[1], 0, 0, epsilon=0.00005)
                    assert within_percent(patch.s_populations[1], 0, 0, epsilon=0.00005)
                # Otherwise could be second possible equilibrium
                except AssertionError:
                    try:
                        assert within_percent(patch.resources, 25, 0.05)
                        assert within_percent(patch.v_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.v_populations[1], 0.3, 0.05)
                        assert within_percent(patch.s_populations[1], 2.4, 0.05)
                    # Finally could be the last possible equilibrium
                    except AssertionError:
                        assert within_percent(patch.resources, 100, 0.05)
                        assert within_percent(patch.v_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.v_populations[1], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[1], 0, 0, epsilon=0.05)

    def test_equlibrium_eq_mode(self):
        """ Test that the system goes to the expected equilibrium. (Within 10%) """

        for i in range(0, 10):

            # Important: Germ chance must be set to 0 for this to work
            rules = NStrain(2, folder_name="test", fly_v_survival=[.2, .2], fly_s_survival=[.8, .8], spore_chance=[.2, .8], germ_chance=[0, 0])

            # Now setup specific parameters
            rules.c = 0.1  # Consumption rate for init_resources_per_patch.
            rules.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
            rules.mu_v = 0.1  # Background death rate for vegetative cells
            rules.mu_s = 0.05  # Background death rate for sporulated cells
            rules.mu_R = 0.01  # "death" rate for init_resources_per_patch.
            rules.gamma = 1  # Rate of resource renewal
            rules.resources = 200
            rules.dt = 1  # Timestep size
            rules.worldmap = nx.complete_graph(10)  # The worldmap
            rules.prob_death = 0.00  # Probability of a patch dying.
            rules.stop_time = 10000  # Iterations to run
            rules.num_flies = 0  # Number of flies each colonization event
            rules.fly_attack_rate = 0.3
            rules.fly_handling_time = 0.3
            rules.fly_stomach_size = random.choice([1, 2, 3, 4, 'type2'])
            rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
            rules.update_mode = 'eq'

            world = World(rules)

            main.run(world)

            for patch in world.patches:

                # First possible equilibrium
                # 0 → Competitor, 1 → Colonizer
                try:
                    assert within_percent(patch.resources, 6.25, 0.05)
                    assert within_percent(patch.v_populations[0], 1.5, 0.05)
                    assert within_percent(patch.s_populations[0], 0.75, 0.05)
                    assert within_percent(patch.v_populations[1], 0, 0, epsilon=0.00005)
                    assert within_percent(patch.s_populations[1], 0, 0, epsilon=0.00005)
                # Otherwise could be second possible equilibrium
                except AssertionError:
                    try:
                        assert within_percent(patch.resources, 25, 0.05)
                        assert within_percent(patch.v_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.v_populations[1], 0.3, 0.05)
                        assert within_percent(patch.s_populations[1], 2.4, 0.05)
                    # Finally could be the last possible equilibrium
                    except AssertionError:
                        assert within_percent(patch.resources, 100, 0.05)
                        assert within_percent(patch.v_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.v_populations[1], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[1], 0, 0, epsilon=0.05)

# class TestTwoStrain:
#
#     def test_equlibrium(self):
#         """ Test that the system goes to the expected equilibrium. (Within 5%) """
#
#         rules = TwoStrain()
#
#         # Now setup specific parameters
#         rules.c = 0.1  # Consumption rate for init_resources_per_patch.
#         rules.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
#         rules.mu_v = 0.1  # Background death rate for vegetative cells
#         rules.mu_s = 0.05  # Background death rate for sporulated cells
#         rules.mu_R = 0.01  # "death" rate for init_resources_per_patch.
#         rules.gamma = 1  # Rate of resource renewal
#         rules.kv_fly_survival = 0.2  # Probability of surviving the fly gut
#         rules.ks_fly_survival = 0.8  # Probability of surviving the fly gut
#         rules.rv_fly_survival = 0.2  # Probability of surviving the fly gut
#         rules.rs_fly_survival = 0.8  # Probability of surviving the fly gut
#         rules.resources = 200
#         rules.sk = 0.2  # Strategy of competitor. (Chance of sporulating)
#         rules.sr = 0.8
#         rules.dt = 1  # Timestep size
#         rules.worldmap = nx.complete_graph(1)  # The worldmap
#         rules.prob_death = 0.00  # Probability of a patch dying.
#         rules.stop_time = 20000  # Iterations to run
#         rules.num_flies = 0  # Number of flies each colonization event
#         rules.fly_attack_rate = 0.3
#         rules.fly_handling_time = 0.3
#         rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
#
#         world = World(rules)
#
#         main.run(world)
#         patch = world.patches[0]
#
#         # First possible equilibrium
#         try:
#             assert within_percent(patch.resources, 6.25, 0.05)
#             assert within_percent(patch.populations['kv'], 1.5, 0.05)
#             assert within_percent(patch.populations['ks'], 0.75, 0.05)
#             assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
#             assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)
#         # Otherwise could be second possible equilibrium
#         except AssertionError:
#             try:
#                 assert within_percent(patch.resources, 25, 0.05)
#                 assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['rv'], 0.3, 0.05)
#                 assert within_percent(patch.populations['rs'], 2.4, 0.05)
#             # Finally could be the last possible equilibrium
#             except AssertionError:
#                 assert within_percent(patch.resources, 100, 0.05)
#                 assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.05)
#
#     def test_equlibrium_small_dt(self):
#         """ Test that the system goes to the expected equilibrium. (Within 5%) """
#
#         rules = TwoStrain()
#
#         # Now setup specific parameters
#         rules.c = 0.1  # Consumption rate for init_resources_per_patch.
#         rules.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
#         rules.mu_v = 0.1  # Background death rate for vegetative cells
#         rules.mu_s = 0.05  # Background death rate for sporulated cells
#         rules.mu_R = 0.01  # "death" rate for init_resources_per_patch.
#         rules.gamma = 1  # Rate of resource renewal
#         rules.kv_fly_survival = 0.2  # Probability of surviving the fly gut
#         rules.ks_fly_survival = 0.8  # Probability of surviving the fly gut
#         rules.rv_fly_survival = 0.2  # Probability of surviving the fly gut
#         rules.rs_fly_survival = 0.8  # Probability of surviving the fly gut
#         rules.resources = 200
#         rules.sk = 0.2  # Strategy of competitor. (Chance of sporulating)
#         rules.sr = 0.8
#         rules.dt = 0.1  # Timestep size
#         rules.worldmap = nx.complete_graph(1)  # The worldmap
#         rules.prob_death = 0.00  # Probability of a patch dying.
#         rules.stop_time = 100000  # Iterations to run
#         rules.num_flies = 0  # Number of flies each colonization event
#         rules.fly_attack_rate = 0.3
#         rules.fly_handling_time = 0.3
#         rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
#
#         world = World(rules)
#
#         main.run(world)
#         patch = world.patches[0]
#         # First possible equilibrium
#         try:
#             assert within_percent(patch.resources, 6.25, 0.05)
#             assert within_percent(patch.populations['kv'], 1.5, 0.05)
#             assert within_percent(patch.populations['ks'], 0.75, 0.05)
#             assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
#             assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)
#         # Otherwise could be second possible equilibrium
#         except AssertionError:
#             try:
#                 assert within_percent(patch.resources, 25, 0.05)
#                 assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['rv'], 0.3, 0.05)
#                 assert within_percent(patch.populations['rs'], 2.4, 0.05)
#             # Finally could be the last possible equilibrium
#             except AssertionError:
#                 assert within_percent(patch.resources, 100, 0.05)
#                 assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.05)
#                 assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.05)
#
#
#     def test_equlibrium_patches(self):
#         """ Same setup, but no patch death and 100 patches"""
#
#         rules = TwoStrain()
#
#         # Now setup specific parameters
#         rules.c = 0.1  # Consumption rate for init_resources_per_patch.
#         rules.alpha = 0.2  # Conversion factor for init_resources_per_patch into cells
#         rules.mu_v = 0.1  # Background death rate for vegetative cells
#         rules.mu_s = 0.05  # Background death rate for sporulated cells
#         rules.mu_R = 0.01  # "death" rate for init_resources_per_patch.
#         rules.gamma = 1  # Rate of resource renewal
#         rules.kv_fly_survival = 0.2  # Probability of surviving the fly gut
#         rules.ks_fly_survival = 0.8  # Probability of surviving the fly gut
#         rules.rv_fly_survival = 0.2  # Probability of surviving the fly gut
#         rules.rs_fly_survival = 0.8  # Probability of surviving the fly gut
#         rules.resources = 200
#         rules.sk = 0.2  # Strategy of competitor. (Chance of sporulating)
#         rules.sr = 0.8
#         rules.dt = 1  # Timestep size
#         rules.worldmap = nx.complete_graph(100)  # The worldmap
#         rules.prob_death = 0.00  # Probability of a patch dying.
#         rules.stop_time = 10000  # Iterations to run
#         rules.num_flies = 10  # Number of flies each colonization event
#         rules.fly_attack_rate = 0.3
#         rules.fly_handling_time = 0.3
#         rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
#
#         world = World(rules)
#
#         main.run(world)
#
#         for patch in world.patches:
#             # First possible equilibrium
#             try:
#                 assert within_percent(patch.resources, 6.25, 0.05)
#                 assert within_percent(patch.populations['kv'], 1.5, 0.05)
#                 assert within_percent(patch.populations['ks'], 0.75, 0.05)
#                 assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
#                 assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)
#             # Otherwise could be second possible equilibrium
#             except AssertionError:
#                 try:
#                     assert within_percent(patch.resources, 25, 0.05)
#                     assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
#                     assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
#                     assert within_percent(patch.populations['rv'], 0.3, 0.05)
#                     assert within_percent(patch.populations['rs'], 2.4, 0.05)
#                 # Finally could be the last possible equilibrium
#                 except AssertionError:
#                     assert within_percent(patch.resources, 100, 0.05)
#                     assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
#                     assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
#                     assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.05)
#                     assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.05)
