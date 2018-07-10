"""
This runs a few test simulations to make sure they work and spit out reasonable results.
"""

import main
import random
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

    def test_equlibrium_normal(self):
        """ Test that the system goes to the expected equilibrium. (Within 5%)

        #Todo Turns out in general they can go to different things because negatives are not allowed...

        """

        rules = TwoStrain()

        # Now setup specific parameters
        rules.c = 0.4  # Consumption rate for resources.
        rules.alpha = 0.22  # Conversion factor for resources into cells
        rules.mu_v = 0.14  # Background death rate for vegetative cells
        rules.mu_s = 0.25  # Background death rate for sporulated cells
        rules.mu_R = 0.11  # "death" rate for resources.
        rules.gamma = 2.4  # Rate of resource renewal
        rules.kv_fly_survival = 0.3  # Probability of surviving the fly gut
        rules.ks_fly_survival = 0.7  # Probability of surviving the fly gut
        rules.rv_fly_survival = 0.2  # Probability of surviving the fly gut
        rules.rs_fly_survival = 0.8  # Probability of surviving the fly gut
        rules.resources = 20
        rules.sk = 0.4  # Strategy of competitor. (Chance of sporulating)
        rules.sr = 0.6
        rules.dt = 1  # Timestep size
        rules.worldmap = nx.complete_graph(1)  # The worldmap
        rules.prob_death = 0.00  # Probability of a patch dying.
        rules.stop_time = 10000  # Iterations to run
        rules.num_flies = 0  # Number of flies each colonization event
        rules.fly_attack_rate = 0.3
        rules.fly_handling_time = 0.3
        rules.reset_all_on_colonize = False  # If true reset all patches during a "pool" colonization



        world = World(rules)

        """ Give half the patches each strain. """
        for patch in world.patches:

            if random.random() < .5:
                patch.populations['rv'] = 300
                patch.populations['rs'] = 300
            else:
                patch.populations['kv'] = 300
                patch.populations['ks'] = 300

        main.run(world)
        patch = world.patches[0]

        test = rules.at_equilibrium(patch, 0.05, epsilon=0.0005)

        assert test == "Competitor" or test == "Colonizer" or test == "Equilibrium"

    def test_equlibrium_and_at_equilibrium(self):
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

        """ Give half the patches each strain. """
        for patch in world.patches:

            if random.random() < .5:
                patch.populations['rv'] = 300
                patch.populations['rs'] = 300
            else:
                patch.populations['kv'] = 300
                patch.populations['ks'] = 300

        main.run(world)
        patch = world.patches[0]

        # First possible equilibrium
        try:
            assert within_percent(patch.resources, 6.25, 0.05)
            assert within_percent(patch.populations['kv'], 1.5, 0.05)
            assert within_percent(patch.populations['ks'], 0.75, 0.05)
            assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
            assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)
            assert rules.at_equilibrium(patch, 0.05, epsilon=0.0005) == "Competitor"
        # Otherwise could be second possible equilibrium
        except AssertionError:
            try:
                assert within_percent(patch.resources, 25, 0.05)
                assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['rv'], 0.3, 0.05)
                assert within_percent(patch.populations['rs'], 2.4, 0.05)
                assert rules.at_equilibrium(patch, 0.05, epsilon=0.0005) == "Colonizer"
            # Finally could be the last possible equilibrium
            except AssertionError:
                assert within_percent(patch.resources, 100, 0.05)
                assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.05)
                assert rules.at_equilibrium(patch, 0.05, epsilon=0.0005) == "Extinction"


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
        # First possible equilibrium
        try:
            assert within_percent(patch.resources, 6.25, 0.05)
            assert within_percent(patch.populations['kv'], 1.5, 0.05)
            assert within_percent(patch.populations['ks'], 0.75, 0.05)
            assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
            assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)
        # Otherwise could be second possible equilibrium
        except AssertionError:
            try:
                assert within_percent(patch.resources, 25, 0.05)
                assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['rv'], 0.3, 0.05)
                assert within_percent(patch.populations['rs'], 2.4, 0.05)
            # Finally could be the last possible equilibrium
            except AssertionError:
                assert within_percent(patch.resources, 100, 0.05)
                assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.05)
                assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.05)


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
            # First possible equilibrium
            try:
                assert within_percent(patch.resources, 6.25, 0.05)
                assert within_percent(patch.populations['kv'], 1.5, 0.05)
                assert within_percent(patch.populations['ks'], 0.75, 0.05)
                assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.00005)
                assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.00005)
            # Otherwise could be second possible equilibrium
            except AssertionError:
                try:
                    assert within_percent(patch.resources, 25, 0.05)
                    assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
                    assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
                    assert within_percent(patch.populations['rv'], 0.3, 0.05)
                    assert within_percent(patch.populations['rs'], 2.4, 0.05)
                # Finally could be the last possible equilibrium
                except AssertionError:
                    assert within_percent(patch.resources, 100, 0.05)
                    assert within_percent(patch.populations['kv'], 0, 0, epsilon=0.05)
                    assert within_percent(patch.populations['ks'], 0, 0, epsilon=0.05)
                    assert within_percent(patch.populations['rv'], 0, 0, epsilon=0.05)
                    assert within_percent(patch.populations['rs'], 0, 0, epsilon=0.05)
