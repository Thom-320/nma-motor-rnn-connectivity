import unittest

import numpy as np

from nma_motor_rnn.connectivity import (
    ExperimentConfig,
    MotorRNN,
    TestTrials,
    compute_manifold_metrics,
    create_reaching_task,
    evaluate_fixed_decoder,
    make_equal_plasticity_masks,
    make_shared_randomness,
    participation_ratio,
    structural_mask,
    run_q1_baseline,
    train_condition,
    velocity_nmse,
)


class ManifoldTests(unittest.TestCase):
    def test_eigenvalues_are_sorted_and_reconstruct_covariance(self):
        rng = np.random.default_rng(4)
        activity = rng.normal(size=(120, 7)) @ np.diag(np.arange(1, 8))
        result = compute_manifold_metrics(activity)
        eigenvalues = result["eigenvalues"]
        eigenvectors = result["eigenvectors"]
        self.assertTrue(np.all(np.diff(eigenvalues) <= 1e-12))
        reconstructed = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
        np.testing.assert_allclose(reconstructed, result["covariance"], atol=1e-10)

    def test_participation_ratio_is_order_invariant(self):
        eigenvalues = np.array([5.0, 2.0, 1.0, 0.5])
        self.assertAlmostEqual(
            participation_ratio(eigenvalues), participation_ratio(eigenvalues[::-1])
        )


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.config = ExperimentConfig(
            n_units=12,
            n_training_trials=2,
            eval_every=1,
            test_initial_states_per_target=1,
            trial_duration=0.3,
            pulse_duration=0.1,
        )
        self.shared = make_shared_randomness(self.config, seed=8)

    def test_zero_error_has_zero_nmse(self):
        rng = np.random.default_rng(1)
        target = rng.normal(size=(6, 10, 2))
        self.assertEqual(velocity_nmse(target.copy(), target), 0.0)

    def test_evaluation_does_not_change_weights(self):
        network = MotorRNN(self.config, 0.2, self.shared)
        stimuli, targets = create_reaching_task(self.config)
        trials = TestTrials(
            self.shared.test_target_indices, self.shared.test_initial_states
        )
        before = network.W.copy()
        evaluate_fixed_decoder(network, trials, stimuli, targets)
        np.testing.assert_array_equal(network.W, before)

    def test_test_set_is_balanced_and_shared(self):
        counts = np.bincount(
            self.shared.test_target_indices, minlength=self.config.n_targets
        )
        np.testing.assert_array_equal(counts, np.ones(self.config.n_targets, dtype=int))
        low = MotorRNN(self.config, 0.1, self.shared)
        high = MotorRNN(self.config, 0.4, self.shared)
        np.testing.assert_array_equal(low.W_in, high.W_in)
        np.testing.assert_array_equal(low.decoder, high.decoder)
        self.assertTrue(np.all(low.mask <= high.mask))

    def test_training_order_is_balanced(self):
        counts = np.bincount(
            self.shared.train_order, minlength=self.config.n_targets
        )
        self.assertLessEqual(int(counts.max() - counts.min()), 1)

    def test_saved_metadata_matches_condition(self):
        rows, summary = train_condition(self.config, self.shared, 0.2)
        self.assertTrue(all(row["p_value"] == 0.2 for row in rows))
        self.assertEqual(summary["p_value"], 0.2)
        self.assertEqual(summary["synapse_count"], summary["plastic_weight_count"])

    def test_smoke_run_is_reproducible(self):
        rows_a, summary_a = train_condition(self.config, self.shared, 0.2)
        shared_again = make_shared_randomness(self.config, seed=8)
        rows_b, summary_b = train_condition(self.config, shared_again, 0.2)
        for key in (
            "final_heldout_nmse",
            "learning_curve_auc",
            "final_d_pr",
            "final_weight_change_fro",
        ):
            self.assertAlmostEqual(summary_a[key], summary_b[key], places=12)
        np.testing.assert_allclose(
            [row["heldout_nmse"] for row in rows_a],
            [row["heldout_nmse"] for row in rows_b],
            atol=0.0,
            rtol=0.0,
        )

    def test_q1_baseline_has_exactly_fifty_trials(self):
        trial_rows, checkpoints, summary = run_q1_baseline(
            self.config, seed=8, p_value=0.10
        )
        self.assertEqual(len(trial_rows), 50)
        self.assertEqual([row["trial"] for row in trial_rows], list(range(1, 51)))
        self.assertEqual(summary["n_training_trials"], 50)
        self.assertEqual(checkpoints[-1]["checkpoint_trial"], 50)


class PlasticityControlTests(unittest.TestCase):
    def setUp(self):
        self.config = ExperimentConfig(
            n_units=16,
            p_values=(0.2, 0.5, 0.8),
            n_training_trials=2,
            eval_every=1,
            test_initial_states_per_target=1,
            trial_duration=0.3,
            pulse_duration=0.1,
        )
        self.shared = make_shared_randomness(self.config, seed=13)

    def test_equal_budget_masks_are_nested_and_equal(self):
        masks = make_equal_plasticity_masks(self.shared, self.config.p_values)
        counts = {int(mask.sum()) for mask in masks.values()}
        self.assertEqual(len(counts), 1)
        first = masks[self.config.p_values[0]]
        for p_value, mask in masks.items():
            np.testing.assert_array_equal(mask, first)
            structural = structural_mask(self.shared, p_value)
            self.assertTrue(np.all(mask <= structural))
            self.assertEqual(int(np.diag(mask).sum()), 0)

    def test_training_does_not_change_frozen_recurrent_weights(self):
        p_value = self.config.p_values[-1]
        plastic_mask = make_equal_plasticity_masks(
            self.shared, self.config.p_values
        )[p_value]
        network = MotorRNN(
            self.config,
            p_value,
            self.shared,
            plastic_mask=plastic_mask,
        )
        stimuli, targets = create_reaching_task(self.config)
        before = network.W.copy()
        network.train_trial(stimuli[0], targets[0], self.shared.train_initial_states[0])
        np.testing.assert_array_equal(network.W[~plastic_mask], before[~plastic_mask])

    def test_plastic_mask_must_be_structurally_supported(self):
        invalid = np.zeros((self.config.n_units, self.config.n_units), dtype=bool)
        invalid[0, 1] = True
        with self.assertRaises(ValueError):
            MotorRNN(self.config, 0.2, self.shared, plastic_mask=invalid)


if __name__ == "__main__":
    unittest.main()
