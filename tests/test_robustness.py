import unittest
from dataclasses import replace

import numpy as np

from nma_motor_rnn.connectivity import (
    ExperimentConfig,
    MotorRNN,
    frozen_drive_weights,
    gain_match_scale,
    initial_recurrent_weights,
    make_equal_plasticity_masks,
    make_extended_shared_randomness,
    make_shared_randomness,
    spectral_radius,
    structural_mask,
    train_condition,
)
from nma_motor_rnn.robustness import (
    P_VALUES,
    Condition,
    arm_conditions,
    build_network_inputs,
    parse_seeds,
)


def small_config(**changes):
    base = ExperimentConfig(
        n_units=40,
        n_training_trials=8,
        trial_duration=0.4,
        pulse_duration=0.1,
        eval_every=4,
        test_initial_states_per_target=1,
    )
    return replace(base, **changes)


class ExtendedRandomnessTests(unittest.TestCase):
    def test_prefix_and_test_set_match_the_shorter_run(self):
        short = small_config(n_training_trials=6)
        long = replace(short, n_training_trials=15)
        base = make_shared_randomness(short, 3)
        extended = make_extended_shared_randomness(long, 3, base_trials=6)
        for name in ("mask_uniform", "weight_normal", "input_weights", "decoder",
                     "test_target_indices", "test_initial_states"):
            np.testing.assert_array_equal(getattr(base, name), getattr(extended, name))
        np.testing.assert_array_equal(base.train_order, extended.train_order[:6])
        np.testing.assert_array_equal(
            base.train_initial_states, extended.train_initial_states[:6]
        )
        self.assertEqual(extended.train_order.shape, (15,))
        self.assertEqual(extended.train_initial_states.shape, (15, long.n_units))

    def test_longer_run_reproduces_the_short_checkpoint_exactly(self):
        short = small_config(n_training_trials=4, eval_every=2)
        long = replace(short, n_training_trials=8)
        short_rows, short_summary = train_condition(
            short, make_shared_randomness(short, 1), 0.2
        )
        long_rows, _ = train_condition(
            long, make_extended_shared_randomness(long, 1, base_trials=4), 0.2
        )
        at_four = [row for row in long_rows if row["checkpoint_trial"] == 4][0]
        self.assertEqual(at_four["heldout_nmse"], short_summary["final_heldout_nmse"])


class GainMatchingTests(unittest.TestCase):
    def test_gain_matched_networks_share_the_sparse_radius(self):
        config = small_config()
        shared = make_shared_randomness(config, 0)
        for arm in ("primary_gain", "control_gain"):
            radii = []
            for p_value in P_VALUES:
                plastic, weights, scale = build_network_inputs(
                    config, shared, Condition(arm, p_value)
                )
                network = MotorRNN(config, p_value, shared, plastic, weights)
                radii.append(spectral_radius(network.W_initial))
                np.testing.assert_array_equal(network.W_initial != 0, network.mask)
            np.testing.assert_allclose(radii, radii[0], rtol=1e-10)

    def test_gain_match_scale_rejects_zero_matrix(self):
        with self.assertRaises(ValueError):
            gain_match_scale(np.zeros((3, 3)), 1.0)

    def test_ungained_arms_leave_default_weights(self):
        config = small_config()
        shared = make_shared_randomness(config, 0)
        plastic, weights, scale = build_network_inputs(
            config, shared, Condition("primary", 0.2)
        )
        self.assertIsNone(plastic)
        self.assertIsNone(weights)
        self.assertEqual(scale, 1.0)


class FrozenDriveTests(unittest.TestCase):
    def setUp(self):
        self.config = small_config(n_units=60)
        self.shared = make_shared_randomness(self.config, 2)

    def test_matches_equal_plasticity_control_on_the_diagonal(self):
        control = make_equal_plasticity_masks(self.shared, P_VALUES)
        for p_value in P_VALUES[1:]:
            fraction = (p_value - 0.05) / p_value
            weights, plastic = frozen_drive_weights(
                self.config, self.shared, p_value, fraction
            )
            np.testing.assert_array_equal(plastic, control[p_value])
            np.testing.assert_allclose(
                weights,
                initial_recurrent_weights(self.config, self.shared, p_value),
                rtol=1e-12,
                atol=1e-15,
            )

    def test_zero_fraction_is_the_sparse_network(self):
        weights, plastic = frozen_drive_weights(self.config, self.shared, 0.40, 0.0)
        sparse = initial_recurrent_weights(self.config, self.shared, 0.05)
        np.testing.assert_allclose(weights, sparse, rtol=1e-12, atol=0.0)
        np.testing.assert_array_equal(plastic, structural_mask(self.shared, 0.05))

    def test_plastic_part_is_identical_across_density_at_fixed_fraction(self):
        sparse_mask = structural_mask(self.shared, 0.05)
        built = [
            frozen_drive_weights(self.config, self.shared, p_value, 0.5)
            for p_value in (0.10, 0.20, 0.40)
        ]
        for weights, plastic in built:
            np.testing.assert_array_equal(plastic, sparse_mask)
            np.testing.assert_array_equal(weights * plastic, built[0][0] * plastic)
        frozen_counts = [int((w != 0).sum() - p.sum()) for w, p in built]
        self.assertTrue(frozen_counts[0] < frozen_counts[1] < frozen_counts[2])

    def test_frozen_variance_fraction_is_respected(self):
        config = small_config(n_units=400)
        shared = make_shared_randomness(config, 0)
        weights, plastic = frozen_drive_weights(config, shared, 0.40, 0.75)
        plastic_var = float(np.sum(weights[plastic] ** 2))
        frozen_var = float(np.sum(weights[~plastic] ** 2))
        self.assertAlmostEqual(frozen_var / (frozen_var + plastic_var), 0.75, delta=0.03)
        total_per_unit = (plastic_var + frozen_var) / config.n_units
        self.assertAlmostEqual(total_per_unit, config.g**2, delta=0.15)

    def test_rejects_degenerate_arguments(self):
        with self.assertRaises(ValueError):
            frozen_drive_weights(self.config, self.shared, 0.05, 0.5)
        with self.assertRaises(ValueError):
            frozen_drive_weights(self.config, self.shared, 0.40, 1.0)

    def test_network_rejects_weights_outside_mask(self):
        weights = np.ones((self.config.n_units, self.config.n_units))
        with self.assertRaises(ValueError):
            MotorRNN(self.config, 0.10, self.shared, initial_weights=weights)

    def test_frozen_edges_do_not_change_during_training(self):
        config = small_config(n_units=40, n_training_trials=2)
        shared = make_shared_randomness(config, 0)
        weights, plastic = frozen_drive_weights(config, shared, 0.40, 0.75)
        network = MotorRNN(config, 0.40, shared, plastic, weights)
        stimuli = np.zeros((config.n_steps, config.n_targets))
        stimuli[: config.pulse_steps, 0] = 1.0
        target = np.full((config.n_steps, 2), 0.1)
        network.train_trial(stimuli, target, shared.train_initial_states[0])
        np.testing.assert_array_equal(network.W[~plastic], weights[~plastic])
        self.assertGreater(np.abs(network.W[plastic] - weights[plastic]).max(), 0.0)


class GridDefinitionTests(unittest.TestCase):
    def test_arm_conditions(self):
        self.assertEqual([c.p_value for c in arm_conditions("primary")], list(P_VALUES))
        frozen = arm_conditions("frozen")
        self.assertEqual(len(frozen), 10)
        self.assertEqual(len({c.label for c in frozen}), 10)
        with self.assertRaises(ValueError):
            arm_conditions("unknown")

    def test_parse_seeds(self):
        self.assertEqual(parse_seeds("0-3,7"), [0, 1, 2, 3, 7])


if __name__ == "__main__":
    unittest.main()
