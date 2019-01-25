

class TestNStrain:

    def test_no_death(self):
        """ Test that all populations spread when there is no death and patches do not die"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(2)
            rules.worldmap = nx.complete_graph(5)
            rules.mu_v = 0
            rules.mu_s = 0
            rules.mu_R = 0
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

    def test_no_extinction(self):
        """ Test that everybody doesn't go extinct"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(4)
            rules.mu_v = 0.01
            rules.mu_s = 0.02
            rules.mu_R = 0.02
            rules.dt = .5
            rules.resources = 500
            rules.gamma = 10
            rules.stop_time = 10000
            rules.num_flies = 3
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
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(5)
            rules.mu_v = 0.001
            rules.mu_s = 0.002
            rules.mu_R = 0.002
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.spore_chance = [.4] * rules.num_strains
            rules.stop_time = 10000
            rules.num_flies = 3
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [1] * rules.num_strains
            rules.prob_death = 0.00  # Make sure that dead prob is low
            world = World(rules)

            main.simulate(world)

            assert sum(rules.sum_populations(world)[-1]) > 0.1  # The sum of all cells should be much larger than zero

    def test_no_colonization_extinction(self):
        """We expect that if strains cannot colonize then they all eventually go extinct"""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.001
            rules.mu_s = 0.001
            rules.mu_R = 0.001
            rules.prob_death = 0.01
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.fly_s_survival = [0] * rules.num_strains
            rules.fly_v_survival = [0] * rules.num_strains
            rules.stop_time = 10000
            rules.num_flies = 3
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [1] * rules.num_strains
            rules.prob_death = 0.0004  # Make sure that dead prob is low
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) == 0
                assert sum(patch.s_populations) == 0

    def test_strain_with_only_spores_goes_extinct(self):
        """ We expect that making only spores go extinct under most parameters. Test this."""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.01
            rules.mu_s = 0.02
            rules.mu_R = 0.02
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 10000
            rules.num_flies = 3
            rules.spore_chance = [1] * rules.num_strains
            rules.germ_chance = [0] * rules.num_strains
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [0] * rules.num_strains
            rules.prob_death = 0.0004  # Make sure that dead prob is low
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) == 0
                assert sum(patch.s_populations) == 0

    def test_strain_with_only_spores_goes_extinct_with_germ(self):
        """ We expect that making only spores go extinct regardless of what the others are doing.
        In this test the very first strain makes all spores."""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.01
            rules.mu_s = 0.02
            rules.mu_R = 0.02
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 10000
            rules.num_flies = 3
            rules.spore_chance = [1] * rules.num_strains
            rules.germ_chance = [random.random()] * rules.num_strains
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [0] * rules.num_strains
            rules.prob_death = 0.0004  # Make sure that dead prob is low
            world = World(rules)

            main.simulate(world)

            for patch in world.patches:
                assert sum(patch.v_populations) == 0
                assert sum(patch.s_populations) == 0

    def test_only_veg_means_extinction(self):
        """ We expect that making only veg cause to go extinct under most parameters. Test this."""

        for i in range(0, TEST_ITERATIONS):
            rules = random_simulation(10)
            rules.worldmap = nx.complete_graph(10)
            rules.mu_v = 0.01
            rules.mu_s = 0.02
            rules.mu_R = 0.02
            rules.dt = .5
            rules.resources = 50
            rules.gamma = 10
            rules.stop_time = 10000
            rules.num_flies = 3
            rules.germ_chance = [0] * rules.num_strains
            rules.spore_chance = [0] * rules.num_strains
            rules.fly_s_survival = [1] * rules.num_strains
            rules.fly_v_survival = [0] * rules.num_strains
            rules.prob_death = 0.0004  # Make sure that dead prob is low
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
            rules.mu_v = 0
            rules.mu_s = 0
            rules.mu_R = 0
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
            rules.mu_v = 0
            rules.mu_s = 0
            rules.mu_R = 0
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
        """ Test that all populations die when patch death is large, even if all populations are immortal."""

        for i in range(0, TEST_ITERATIONS):
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
