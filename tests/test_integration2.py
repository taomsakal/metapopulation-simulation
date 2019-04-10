import random
import pytest
import hypothesis

import main
from world import World
from simrules.NStrainsSimple import NStrainsSimple
from simrules.TwoStrain import TwoStrain
from AM_programs.NStrain import NStrain
from general import within_percent
import networkx as nx
from simrules import helpers


TEST_ITERATIONS = 3  # The number of times to loop each test. We can increase this to reduce chance of getting lucky in one simulation

def random_simulation(n):
    """ Makes a random NSTrain simulation with up to n strains and default parms"""

    num_strains = random.randint(1, n)
    rules = NStrain(num_strains, folder_name="test_no_death", spore_chance=helpers.random_probs(num_strains),
                   germ_chance=helpers.random_probs(num_strains), fly_s_survival=helpers.random_probs(num_strains),
                   fly_v_survival=helpers.random_probs(num_strains), save_data=False)
    rules.update_mode = random.choice(["discrete", "eq"])

    rules.colonize_mode = random.choice(["fly", "probabilities"])
    rules.fly_stomach_size = random.choice([1, 2, 10, 'type 2'])

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
    rules.num_flies = random.randint(0, 10)  # Number of flies each colonization event
    rules.fly_attack_rate = 0.3
    rules.fly_handling_time = 0.3
    rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization

    return rules

class TestNStrainsSimple:

    def test_no_death(self):
        """ Test that all populations spread """

        for i in range(0, TEST_ITERATIONS):

            world = World(NStrainsSimple(3, nx.complete_graph(10), 0.0, 1.001, 400))
            main.simulate(world)

            for patch in world.patches:
                for population in patch.populations:
                    assert population > 0

    def test_high_death(self):
        """ Test that populations go extinct under a high dead rate """

        for i in range(0, ):

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

class TestNStrainStress:

    def test_many_strain(self):
        """ See if crashes during a many strain run"""

        for i in range(0, TEST_ITERATIONS):
            # Long run
            rules = random_simulation(100)
            rules.worldmap = nx.complete_graph(5)
            rules.resources = 500
            rules.stop_time = 400
            world = World(rules)
            main.simulate(world)
            assert True

    def test_many_node_run(self):

        for i in range(0, TEST_ITERATIONS):
            # High node run
            rules = random_simulation(20)
            rules.worldmap = nx.complete_graph(random.randint(100, 300))
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


class TestNStrainEq:

    def test_no_unlimited_growth(self):
        """Strain number should not get massive"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)


            rules.worldmap = nx.complete_graph(100)
            rules.mu_v = 0.1
            rules.mu_s = 0.04
            rules.mu_R = 0.04
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 3000
            rules.num_flies = 3
            rules.prob_death = 0.00004  # Make sure that dead prob is low

            world = World(rules)

            rules.print_params()

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) < 10*(10**10)
                assert sum(patch.s_populations) < 10*(10**10)
                # assert sum(patch.v_populations) >= 0  # Current eq does allow things to be zero
                # assert sum(patch.s_populations) >= 0

    def test_no_unlimited_growth_low_mu_eq(self):
        """Strain number should not get massive. There was a bug that if mu_v < 0.09 then this happens
        """

        # Todo: there is still a bug where this happens if mode is not "eq"

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)


            rules.worldmap = nx.complete_graph(100)
            rules.mu_v = 0.01
            rules.mu_s = 0.004
            rules.mu_R = 0.004
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 3000
            rules.num_flies = 3
            rules.prob_death = 0.00004  # Make sure that dead prob is low
            rules.update_mode = "eq"

            world = World(rules)

            rules.print_params()

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) < 10*(10**10)
                assert sum(patch.s_populations) < 10*(10**10)
                # assert sum(patch.v_populations) >= 0  # Current eq does allow things to be zero
                # assert sum(patch.s_populations) >= 0


    def test_n_strain_all_but_one_with_no_pop(self):
        """ Just having one strain should be the same as having n but with only the first one having any population
        """

        for i in range(0, TEST_ITERATIONS):

            # This world is with two strains, but one cannot survive the fly
            # This test has a high percent error because it sometimes takes a long time fall to correct values
            rules = NStrain(2, folder_name="test", fly_s_survival=[.5, 0], fly_v_survival=[.8, 0], spore_chance=[.2, .8], germ_chance=[.2, .2])
            rules.worldmap = nx.complete_graph(100)
            rules.stop_time = 2000
            rules.dt = 1
            rules.prob_death = 0.0005
            rules.v_population_totals = [x if i == 0 else 0 for i, x in enumerate(rules.v_population_totals)]
            rules.v_population_totals = [x if i == 0 else 0 for i, x in enumerate(rules.s_population_totals)]
            world = World(rules)
            # rules.update_mode = "discrete"
            main.run(world)

            # This world is with only the first strain
            rules2 = NStrain(1, folder_name="test", fly_s_survival=[.5], fly_v_survival=[.8], spore_chance=[.2], germ_chance=[.2])
            rules2.worldmap = nx.complete_graph(100)
            rules2.stop_time = 2000
            rules2.dt = 1
            # rules2.update_mode = "discrete"
            rules2.prob_death = 0.0005
            world2 = World(rules2)
            main.run(world2)




        world1pop = sum(world.rules.sum_populations(world)[-1])
        world2pop = sum(world2.rules.sum_populations(world2)[-1])

        assert within_percent(world1pop, world2pop, 0.15, epsilon=0.0005)



    def test_2_strain_1_with_no_colonization_discrete(self):
        """ Makes sure that if there are two strains and one cannot survive the fly then the long term eqs are equal
        That is, the second strain does not effect the long term dynamics

        We need to up the patch number for this test else stochasticity can cause it to fail
        """


        for i in range(0, TEST_ITERATIONS):

            # This world is with two strains, but one cannot survive the fly
            # This test has a high percent error because it sometimes takes a long time fall to correct values.
            # We are mostly testing that the values aren't way way different
            rules = NStrain(2, folder_name="test", fly_s_survival=[.5, 0], fly_v_survival=[.8, 0], spore_chance=[.2, .8], germ_chance=[.2, .2])
            rules.worldmap = nx.complete_graph(20)
            rules.stop_time = 5000
            rules.dt = 1
            rules.num_flies = 0
            rules.prob_death = 0.0005
            rules.colonization_prob_slope = 0
            world = World(rules)
            rules.update_mode = "discrete"
            main.run(world)

            # This world is with only the first strain
            rules2 = NStrain(1, folder_name="test", fly_s_survival=[.5], fly_v_survival=[.8], spore_chance=[.2], germ_chance=[.2])
            rules2.worldmap = nx.complete_graph(20)
            rules2.stop_time = 5000
            rules2.dt = 1
            rules2.update_mode = "discrete"
            rules2.colonization_prob_slope = 0
            rules2.num_flies = 0
            rules2.prob_death = 0.0005
            world2 = World(rules2)
            main.run(world2)


        world1pop = world.rules.sum_populations(world)[0]
        world2pop = world2.rules.sum_populations(world2)[0]

        assert within_percent(world1pop, world2pop, 0.35, epsilon=0.0005)

    def test_2_strain_1_with_no_colonization_eq(self):
        """ Makes sure that if there are two strains and one cannot survive the fly then the long term eqs are equal
        That is, the second strain does not effect the long term dynamics

        We need to up the patch number for this test else stochasticity can cause it to fail
        """

        # TODO This test is broken

        for i in range(0, TEST_ITERATIONS):

            # This world is with two strains, but one cannot survive the fly
            # This test has a high percent error because it sometimes takes a long time fall to correct values
            rules = NStrain(2, folder_name="test", fly_s_survival=[.5, 0], fly_v_survival=[.8, 0], spore_chance=[.2, .8], germ_chance=[.2, .2])
            rules.worldmap = nx.complete_graph(100)
            rules.stop_time = 3000
            rules.dt = 1
            rules.prob_death = 0.0005
            world = World(rules)
            rules.colonization_prob_slope = 0
            rules.num_flies = 0
            rules.update_mode = "eq"
            main.run(world)

            # This world is with only the first strain
            rules2 = NStrain(1, folder_name="test", fly_s_survival=[.5], fly_v_survival=[.8], spore_chance=[.2], germ_chance=[.2])
            rules2.worldmap = nx.complete_graph(100)
            rules2.stop_time = 3000
            rules2.dt = 1
            rules2.colonization_prob_slope = 0
            rules2.num_flies = 0
            rules2.update_mode = "eq"
            rules2.prob_death = 0.0005
            world2 = World(rules2)
            main.run(world2)


        world1pop = world.rules.sum_populations(world)[0]
        world2pop = world2.rules.sum_populations(world2)[0]

        assert within_percent(world1pop, world2pop, 0.25, epsilon=0.0005)

    def test_same_strain_have_equal_fixation_chance(self):


        sums = []
        for i in range(0, TEST_ITERATIONS*2):
            # This world is with two strains, but one cannot survive the fly
            # This test has a high percent error because it sometimes takes a long time fall to correct values
            rules = NStrain(2, folder_name="test", fly_s_survival=[.5, .5], fly_v_survival=[.8, .8], spore_chance=[.8, .8], germ_chance=[.2, .2])
            rules.worldmap = nx.complete_graph(100)
            rules.stop_time = 2000
            rules.dt = 1
            rules.prob_death = 0.001
            world = World(rules)
            main.run(world)

            rules2 = NStrain(2, folder_name="test", fly_s_survival=[.5, .5], fly_v_survival=[.8, .8],
                            spore_chance=[.8, .8], germ_chance=[.2, .2])
            rules2.worldmap = nx.complete_graph(100)
            rules2.stop_time = 2000
            rules2.dt = 1
            rules2.prob_death = 0.001
            world2 = World(rules2)
            main.run(world2)


            pop1 = sum(world.rules.sum_populations(world)[-1])
            pop2 = sum(world2.rules.sum_populations(world)[-1])


            if pop1 + pop2 != 0:
                freq = pop1 / (pop1 + pop2)
                sums.append(freq)

        average = sum(sums)/len(sums)

        assert within_percent(average, .5, 0.15, epsilon=0.0005)

    def test_equlibrium_discrete_mode(self):
        """ Test that the system goes to the expected equilibrium. (Within 10%) """

        for i in range(0, TEST_ITERATIONS):

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
            rules.worldmap = nx.complete_graph(3)  # The worldmap
            rules.prob_death = 0.00  # Probability of a patch dying.
            rules.stop_time = 5000  # Iterations to run
            rules.num_flies = 0  # Number of flies each colonization event
            rules.fly_attack_rate = 0.3
            rules.fly_handling_time = 0.3
            rules.fly_stomach_size = random.choice([1,2,3,4,'type2'])
            rules.update_mode = 'discrete'
            rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization

            world = World(rules)

            main.run(world)

            for patch in world.patches:

                # First possible equilibrium
                # 0 → Competitor, 1 → Colonizer
                try:
                    assert within_percent(patch.resources, 6.25, 0.15)
                    assert within_percent(patch.v_populations[0], 1.5, 0.15)
                    assert within_percent(patch.s_populations[0], 0.75, 0.15)
                    assert within_percent(patch.v_populations[1], 0, 0, epsilon=0.00005)
                    assert within_percent(patch.s_populations[1], 0, 0, epsilon=0.00005)
                # Otherwise could be second possible equilibrium
                except AssertionError:
                    try:
                        assert within_percent(patch.resources, 25, 0.15)
                        assert within_percent(patch.v_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.v_populations[1], 0.3, 0.15)
                        assert within_percent(patch.s_populations[1], 2.4, 0.15)
                    # Finally could be the last possible equilibrium
                    except AssertionError:
                        assert within_percent(patch.resources, 100, 0.15)
                        assert within_percent(patch.v_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[0], 0, 0, epsilon=0.05)
                        assert within_percent(patch.v_populations[1], 0, 0, epsilon=0.05)
                        assert within_percent(patch.s_populations[1], 0, 0, epsilon=0.05)

    def test_equlibrium_eq_mode_one_step(self):
        """ Test that the system goes to the expected equilibrium in a single step"""

        for i in range(0, TEST_ITERATIONS):

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
            rules.stop_time = 1  # Iterations to run
            rules.num_flies = 0  # Number of flies each colonization event
            rules.fly_attack_rate = 0.3
            rules.fly_handling_time = 0.3
            rules.fly_stomach_size = random.choice([1, 2, 3, 4, 'type2'])
            rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
            rules.update_mode = 'eq'

            world = World(rules)

            main.run(world)

            for patch in world.patches:

                print("Resources ", patch.resources)
                print("v_pops ", patch.v_populations)
                print("s_pops", patch.s_populations)

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

    def test_equlibrium_eq_mode_many_steps(self):
        """ Test that the system goes to the expected equilibrium in a single step"""

        for i in range(0, TEST_ITERATIONS):

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
            rules.stop_time = 123  # Iterations to run
            rules.num_flies = 0  # Number of flies each colonization event
            rules.fly_attack_rate = 0.3
            rules.fly_handling_time = 0.3
            rules.fly_stomach_size = random.choice([1, 2, 3, 4, 'type2'])
            rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization
            rules.update_mode = 'eq'

            world = World(rules)

            main.run(world)

            for patch in world.patches:

                print("Resources ", patch.resources)
                print("v_pops ", patch.v_populations)
                print("s_pops", patch.s_populations)

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

class TestNStrainExtinctionPresistence:

    def test_no_death(self):
        """ Test that all populations spread when there is no death and patches do not die"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(2)
            rules.worldmap = nx.complete_graph(5)
            rules.mu_v = 0.0001
            rules.mu_s = 0.0001
            rules.mu_R = 0.0001
            rules.dt = .01
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 5000
            rules.num_flies = 0
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [1] * rules.num_strains
            rules.prob_death = 0  # Make sure that dead prob is low
            rules.colonize_mode = 'fly'  # There must be no colonization else one strain can drive the other extinct
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) > 0
                assert sum(patch.s_populations) > 0

    def test_no_extinction_discrete(self):
        """ Test that everybody doesn't go extinct.
        This is important because was bug that even one fly can make everybody go extinct."""

        for i in range(0, TEST_ITERATIONS*3):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(30)
            rules.mu_v = 0.1
            rules.mu_s = 0.0002
            rules.mu_R = 0.0002
            rules.dt = .1
            rules.resources = 500
            rules.gamma = 10
            rules.stop_time = 1000
            rules.update_mode = "discrete"
            rules.colonize_mode = "fly"
            rules.num_flies = 1
            rules.yeast_size = 0.0001
            rules.fly_s_survival = [.8] * rules.num_strains
            rules.fly_v_survival = [.2] * rules.num_strains
            rules.prob_death = 0  # Make sure that dead prob is zero, then can iterate through all patches
            world = World(rules)

            main.simulate(world)

            rules.print_params(world)

            for patch in world.patches:
                assert rules.total_pop > 0
                assert sum(patch.s_populations) > 0
                assert sum(patch.v_populations) > 0

        # Todo: repeat this test for eq

    def test_no_extinction_eq(self):
        """ Test that everybody doesn't go extinct.
        This is important because was bug that even one fly can make everybody go extinct."""

        for i in range(0, TEST_ITERATIONS*3):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(30)
            rules.mu_v = 0.1
            rules.mu_s = 0.0002
            rules.mu_R = 0.0002
            rules.dt = .1
            rules.resources = 500
            rules.gamma = 10
            rules.stop_time = 1000
            rules.update_mode = "eq"
            rules.colonize_mode = "probabilities"
            rules.num_flies = 1
            rules.yeast_size = 0.0001
            rules.fly_s_survival = [.8] * rules.num_strains
            rules.fly_v_survival = [.2] * rules.num_strains
            rules.prob_death = 0  # Make sure that dead prob is zero, then can iterate through all patches
            world = World(rules)

            main.simulate(world)

            rules.print_params(world)

            for patch in world.patches:
                assert rules.total_pop > 0
                assert sum(patch.s_populations) > 0
                assert sum(patch.v_populations) > 0

    def test_no_extinction_with_patch_death(self):
        """ Test that everybody doesn't go extinct"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(5)
            rules.worldmap = nx.complete_graph(30)
            rules.mu_v = 0.1
            rules.mu_s = 0.001
            rules.mu_R = 0.001
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.spore_chance = [.5] * rules.num_strains
            rules.stop_time = 1000
            rules.num_flies = 3
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [1] * rules.num_strains
            rules.prob_death = 0.0000001  # Make sure that dead prob is very low
            world = World(rules)

            main.simulate(world)

            print(rules.sum_populations(world)[-1])
            assert sum(rules.sum_populations(world)[-1]) > 1  # The sum of all cells should be much larger than zero

    def test_no_colonization_extinction(self):
        """We expect that if strains cannot colonize then they all eventually go extinct, even if cells are nearly immortal"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.00001
            rules.mu_s = 0.00001
            rules.mu_R = 0.00001
            rules.prob_death = 0.01
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.fly_s_survival = [0] * rules.num_strains
            rules.fly_v_survival = [0] * rules.num_strains
            rules.stop_time = 2000
            rules.colonize_mode = "fly"
            rules.num_flies = 0  # Make sure cannot colonize
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [1] * rules.num_strains
            rules.prob_death = 0.04  # Make sure that dead prob is high so test goes fast
            world = World(rules)

            rules.print_params()

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) < 1
                assert sum(patch.v_populations) >= 0
                assert sum(patch.s_populations) < 1
                assert sum(patch.s_populations) >= 0


    def test_extinct_no_resource_renewal(self):
        """We expect that if strains cannot colonize then they all eventually go extinct
        This test takes care of bugs where population can grow without bound"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.001
            rules.mu_s = 0.001
            rules.mu_R = 0.001
            rules.prob_death = 0.01
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 0
            rules.stop_time = 10000
            rules.num_flies = 3
            rules.prob_death = 0.0004  # Make sure that dead prob is low
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) < 1
                assert sum(patch.v_populations) >= 0
                assert sum(patch.s_populations) < 1
                assert sum(patch.s_populations) >= 0

    def test_extinct_no_resources(self):
        """Very low resource rate means tiny population"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.001
            rules.mu_s = 0.001
            rules.mu_R = 0.001
            rules.prob_death = 0.01
            rules.dt = .5
            rules.resources = 50
            rules.gamma = .0001
            rules.stop_time = 10000
            rules.num_flies = 3
            rules.prob_death = 0.0004  # Make sure that dead prob is low
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) < 1
                assert sum(patch.v_populations) >= 0
                assert sum(patch.s_populations) < 1
                assert sum(patch.s_populations) >= 0

    def test_strain_with_only_spores_goes_extinct_no_germination(self):
        """ We expect that making only spores go extinct under most parameters. Test this."""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(5)
            rules.stop_time = 10000
            rules.spore_chance = [1] * rules.num_strains
            rules.germ_chance = [0] * rules.num_strains
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [0] * rules.num_strains
            rules.germinate_on_drop = False
            rules.prob_death = 0.000  # Make sure that dead prob is low
            world = World(rules)

            main.simulate(world)

            # Check that is real small but not negative
            for patch in world.patches:
                assert sum(patch.v_populations) < 1
                assert sum(patch.v_populations) >= 0
                assert sum(patch.s_populations) < 1
                assert sum(patch.s_populations) >= 0
    #
    # def test_strain_with_only_spores_lives_with_germ(self):
    #     """ We expect that making only spores does not go extinct if they germinate?"""
    #
    #     for i in range(0, TEST_ITERATIONS):
    #         rules = random_simulation(10)
    #         rules.worldmap = nx.complete_graph(10)
    #         rules.spore_chance = [1] * rules.num_strains
    #         rules.germ_chance = [random.random()] * rules.num_strains
    #         rules.fly_s_survival = [0.8] * rules.num_strains
    #         rules.fly_v_survival = [0.2] * rules.num_strains
    #         rules.stop_time = 10000
    #         rules.prob_death = 0.0004  # Make sure that dead prob is low
    #         rules.germinate_on_drop = True
    #         world = World(rules)
    #
    #         main.simulate(world)
    #
    #         for patch in world.patches:
    #             assert sum(patch.v_populations) < 1
    #             assert sum(patch.s_populations) < 1

    def test_only_veg_means_extinction(self):
        """ We expect that making only veg cause to go extinct under most parameters. Test this."""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.germ_chance = [0] * rules.num_strains
            rules.spore_chance = [0] * rules.num_strains
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [0] * rules.num_strains
            rules.prob_death = 0.04  # Make sure that dead prob is low
            rules.stop_time = 400
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) == 0
                assert sum(patch.s_populations) == 0

    def test_no_death_with_flies_that_dont_eat(self):
        """ Test that all populations spread when there is no death and patches do not die"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.0001
            rules.mu_s = 0.0001
            rules.mu_R = 0.0001
            rules.dt = .01
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 1000
            rules.num_flies = 10
            rules.fly_stomach_size = 0
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [1] * rules.num_strains
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

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.0001
            rules.mu_s = 0.0001
            rules.mu_R = 0.0001
            rules.dt = .01
            rules.resources = 500
            rules.gamma = 10
            rules.stop_time = 1000
            rules.num_flies = 3
            rules.fly_stomach_size = 'type 2'
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [1] * rules.num_strains
            rules.prob_death = 0  # Make sure that dead prob is low
            rules.germinate_on_drop = True
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) > 0
                assert sum(patch.s_populations) > 0

    def test_heavy_death_in_patches(self):
        """ Test that all populations die when patch death is large, even if all populations are near immortal."""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.00001
            rules.mu_s = 0.00001
            rules.mu_R = 0.00001
            rules.resources = 50
            rules.stop_time = 1000
            rules.num_flies = 5
            rules.prob_death = 0.9  # Make this high
            world = World(rules)
            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) == 0
                assert sum(patch.s_populations) == 0

    def test_high_death(self):
        """ Test that populations go essentially extinct under a high dead rate """

        for i in range(0, TEST_ITERATIONS):
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

        for i in range(0, TEST_ITERATIONS):
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
