"""Deterministic regression tests for the proof-closure certificate."""

from __future__ import annotations

import random
import unittest

from local_star_state import (
    LocalVoxelModel,
    border_status_from_incident_voxels,
    build_x_h,
    collar_region,
    comparable_candidates,
    voxel_star,
)
from run_proof_closure import (
    LOWER_RANK_TYPES,
    TYPES,
    lemma_41_type,
    lemma_43_square,
    lower_rank_inheritance,
    lower_rank_type,
)


class ProofClosureTests(unittest.TestCase):
    def test_canonical_border_tables_against_direct_geometry(self) -> None:
        rng = random.Random(20260729)
        centers = [(0, 0, 0), (0, 0, 1), (0, 1, 1)]
        for center in centers:
            targets = comparable_candidates(center) | {center}
            model = LocalVoxelModel(3, collar_region({center}), targets)
            all_masks = list(range(1 << len(model.voxels)))
            masks = all_masks if len(all_masks) <= 4096 else rng.sample(all_masks, 4096)
            for mask in masks:
                occupied = model.occupied_voxels(mask)
                for cell in targets:
                    incident = frozenset(occupied & voxel_star(cell))
                    self.assertEqual(
                        model.is_border(cell, mask),
                        border_status_from_incident_voxels(3, cell, incident),
                    )

    def test_lemma_41_frozen_counts(self) -> None:
        expected = {
            (0, 1): (13, 0, 13),
            (0, 2): (88, 50, 38),
            (0, 3): (63, 0, 63),
            (1, 2): (2304, 1536, 768),
            (1, 3): (1536, 0, 1536),
            (2, 3): (1, 0, 1),
        }
        self.assertEqual(set(TYPES), set(expected))
        for pair, (admissible, odd, even) in expected.items():
            row = lemma_41_type(*pair)
            self.assertEqual(row["locally_admissible_masks"], admissible)
            self.assertEqual(row["odd"], odd)
            self.assertEqual(row["even"], even)
            self.assertEqual(row["violations"], 0)

    def test_square_frozen_counts(self) -> None:
        row = lemma_43_square()
        self.assertEqual(row["collar_voxels"], 18)
        self.assertEqual(row["enumerated_masks"], 196608)
        self.assertEqual(row["locally_admissible_masks"], 21289)
        self.assertEqual(row["fully_persisting_components"], 9926)
        self.assertEqual(row["components_equal_boundary"], 9926)
        self.assertEqual(row["component_size_histogram"], {"8": 9926})
        self.assertEqual(row["violations"], 0)

    def test_lower_rank_frozen_counts(self) -> None:
        expected = {
            (1, 0, 1): (1, 0, 1),
            (2, 0, 1): (9, 6, 3),
            (2, 0, 2): (6, 0, 6),
            (2, 1, 2): (16, 0, 16),
        }
        for ambient_rank, types in LOWER_RANK_TYPES.items():
            for (dim_x, dim_h), (k, m) in types.items():
                row = lower_rank_type(
                    ambient_rank, dim_x, dim_h, k, m
                )
                actual = (
                    row["locally_admissible_masks"],
                    row["odd"],
                    row["even"],
                )
                self.assertEqual(
                    actual,
                    expected[(ambient_rank, dim_x, dim_h)],
                )
                self.assertEqual(row["violations"], 0)

    def test_lower_rank_upper_free_inheritance(self) -> None:
        row = lower_rank_inheritance()
        self.assertEqual(row["ambient_rank_2_edge_collar_voxels"], 6)
        self.assertEqual(row["ambient_rank_2_edge_masks"], 48)
        self.assertEqual(row["ambient_rank_2_edge_locally_admissible"], 34)
        self.assertEqual(row["ambient_rank_2_edge_pwc_neighborhoods"], 34)
        self.assertEqual(row["ambient_rank_2_edge_violations"], 0)
        self.assertEqual(row["border_cardinality_histogram"], {"0": 16, "2": 18})


if __name__ == "__main__":
    unittest.main(verbosity=2)
