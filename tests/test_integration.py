"""
This runs a few test simulations to make sure they work and spit out reasonable results.
"""

import main
from world import World
from simrules.NStrainsSimple import NStrainsSimple
from simrules.TwoStrain import TwoStrain
from general import within_percent
import networkx as nx


class TestNStrainsSimple:

    def test_no_death(self):
        """ Test that all populations spread """

        for i in range(0, 10):

            world = World(NStrainsSimple(3, nx.complete_graph(10), 0.0, 1.001, 400))
            main.simulate(world)

            for patch in world.patches:
                for population in patch.populations:
                    assert population > 0

    def test_high_death(self):
        """ Test that populations go extinct under a high dead rate """

        for i in range(0, 10):

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

class TestTwoStrain:

    def test_equlibrium(self):
        """ Test that the system goes to the expected equilibrium. (Within 5%) """

        rules = TwoStrain()

        # Now setup specific parameters
        rules.c = 0.1  # Consumption rate for resources.
        rules.alpha = 0.2  # Conversion factor for resources into cells
        rules.mu_v = 0.1  # Background death rate for vegetative cells
        rules.mu_s = 0.05  # Background death rate for sporulated cells
        rules.mu_R = 0.01  # "death" rate for resources.
        rules.gamma = 1  # Rate of resource renewal
        rules.kv_fly_survival = 0.2  # Probability of surviving the fly gut
        rules.ks_fly_survival = 0.8  # Probability of surviving the fly gut
        rules.rv_fly_survival = 0.2  # Probability of surviving the fly gut
        rules.rs_fly_survival = 0.8  # Probability of surviving the fly gut
        rules.resources = 200
        rules.sk = 0.2  # Strategy of competitor. (Chance of sporulating)
        rules.sr = 0.8
        rules.dt = 1  # Timestep size
        rules.worldmap = nx.complete_graph(1)  # The worldmap
        rules.prob_death = 0.00  # Probability of a patch dying.
        rules.stop_time = 1000  # Iterations to run
        rules.num_flies = 0  # Number of flies each colonization event
        rules.fly_attack_rate = 0.3
        rules.fly_handling_time = 0.3
        rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization

        world = World(rules)

        main.run(world)
        patch = world.patches[0]

        assert within_percent(patch.resources, 6.25, 0.05)

        assert within_percent(patch.populations['kv'], 1.5, 0.05)
        assert within_percent(patch.populations['ks'], 0.75, 0.05)
        assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
        assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)

    def test_equlibrium_small_dt(self):
        """ Test that the system goes to the expected equilibrium. (Within 5%) """

        rules = TwoStrain()

        # Now setup specific parameters
        rules.c = 0.1  # Consumption rate for resources.
        rules.alpha = 0.2  # Conversion factor for resources into cells
        rules.mu_v = 0.1  # Background death rate for vegetative cells
        rules.mu_s = 0.05  # Background death rate for sporulated cells
        rules.mu_R = 0.01  # "death" rate for resources.
        rules.gamma = 1  # Rate of resource renewal
        rules.kv_fly_survival = 0.2  # Probability of surviving the fly gut
        rules.ks_fly_survival = 0.8  # Probability of surviving the fly gut
        rules.rv_fly_survival = 0.2  # Probability of surviving the fly gut
        rules.rs_fly_survival = 0.8  # Probability of surviving the fly gut
        rules.resources = 200
        rules.sk = 0.2  # Strategy of competitor. (Chance of sporulating)
        rules.sr = 0.8
        rules.dt = 0.1  # Timestep size
        rules.worldmap = nx.complete_graph(1)  # The worldmap
        rules.prob_death = 0.00  # Probability of a patch dying.
        rules.stop_time = 10000  # Iterations to run
        rules.num_flies = 0  # Number of flies each colonization event
        rules.fly_attack_rate = 0.3
        rules.fly_handling_time = 0.3
        rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization

        world = World(rules)

        main.run(world)
        patch = world.patches[0]

        assert within_percent(patch.resources, 6.25, 0.05)

        assert within_percent(patch.populations['kv'], 1.5, 0.05)
        assert within_percent(patch.populations['ks'], 0.75, 0.05)
        assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
        assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)

    def test_equlibrium_patches(self):
        """ Same setup, but no patch death and 100 patches"""

        rules = TwoStrain()

        # Now setup specific parameters
        rules.c = 0.1  # Consumption rate for resources.
        rules.alpha = 0.2  # Conversion factor for resources into cells
        rules.mu_v = 0.1  # Background death rate for vegetative cells
        rules.mu_s = 0.05  # Background death rate for sporulated cells
        rules.mu_R = 0.01  # "death" rate for resources.
        rules.gamma = 1  # Rate of resource renewal
        rules.kv_fly_survival = 0.2  # Probability of surviving the fly gut
        rules.ks_fly_survival = 0.8  # Probability of surviving the fly gut
        rules.rv_fly_survival = 0.2  # Probability of surviving the fly gut
        rules.rs_fly_survival = 0.8  # Probability of surviving the fly gut
        rules.resources = 200
        rules.sk = 0.2  # Strategy of competitor. (Chance of sporulating)
        rules.sr = 0.8
        rules.dt = 1  # Timestep size
        rules.worldmap = nx.complete_graph(100)  # The worldmap
        rules.prob_death = 0.00  # Probability of a patch dying.
        rules.stop_time = 1000  # Iterations to run
        rules.num_flies = 10  # Number of flies each colonization event
        rules.fly_attack_rate = 0.3
        rules.fly_handling_time = 0.3
        rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization

        world = World(rules)

        main.run(world)

        for patch in world.patches:
            assert within_percent(patch.resources, 6.25, 0.05)
            assert within_percent(patch.populations['kv'], 1.5, 0.05)
            assert within_percent(patch.populations['ks'], 0.75, 0.05)
            assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
            assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)