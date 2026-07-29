"""Run the exhaustive P1/P2 proof-closure computations.

Outputs a deterministic JSON certificate.  No random generator and no
truncated-complex PWC filter is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path
from typing import Dict, List, Tuple

from local_star_state import (
    Cell,
    LocalVoxelModel,
    build_x_h,
    closure,
    collar_region,
    comparable_candidates,
    connected_components,
    e_set,
    is_face,
    is_surface,
    is_surface_1,
    local_pwc_link_condition,
    persists_in_neighborhood,
    strictly_comparable,
    theta_prime,
    voxel_star,
)

TYPES: Dict[Tuple[int, int], Tuple[int, int]] = {
    (0, 1): (1, 2),
    (0, 2): (2, 1),
    (0, 3): (3, 0),
    (1, 2): (1, 1),
    (1, 3): (2, 0),
    (2, 3): (1, 0),
}

LOWER_RANK_TYPES = {
    1: {(0, 1): (1, 0)},
    2: {
        (0, 1): (1, 1),
        (0, 2): (2, 0),
        (1, 2): (1, 0),
    },
}


def lemma_41_type(dim_x: int, dim_h: int) -> dict:
    k, m = TYPES[(dim_x, dim_h)]
    x, h = build_x_h(k, m)

    # For a square x below a cube h, x in Delta X forces the second
    # incident cube to be absent.  The parity/persistence verdict then
    # depends on a single quotient state, independently of the collar.
    if (dim_x, dim_h) == (2, 3):
        model = LocalVoxelModel(
            3,
            collar_region({x}),
            comparable_candidates(x) | {x},
        )
        h_voxel_mask = model.mask_of_voxels(voxel_star(h))
        opposite_mask = model.mask_of_voxels(voxel_star(x) - voxel_star(h))
        quotient_mask = h_voxel_mask
        assert model.is_border(x, quotient_mask)
        assert not (quotient_mask & opposite_mask)
        parity = len(e_set(model, x, h, quotient_mask)) % 2
        persists = persists_in_neighborhood(model, x, h, quotient_mask)
        return {
            "dim_x": dim_x,
            "dim_h": dim_h,
            "k": k,
            "m": m,
            "collar_voxels": len(model.voxels),
            "enumeration_mode": "quotient_by_x_star",
            "enumerated_masks": 1,
            "locally_admissible_masks": 1,
            "odd": int(parity == 1),
            "even": int(parity == 0),
            "violations": int(bool(parity) != persists),
        }

    border_targets = comparable_candidates(x) | {x}
    model = LocalVoxelModel(3, collar_region({x}), border_targets)
    h_cofaces = frozenset(
        cell
        for cell in comparable_candidates(h)
        if is_face(h, cell) and cell != h
    )

    counts = {
        "enumerated_masks": 0,
        "locally_admissible_masks": 0,
        "odd": 0,
        "even": 0,
        "violations": 0,
    }

    for mask in model.masks_containing(h):
        counts["enumerated_masks"] += 1
        if not model.is_border(x, mask):
            continue
        if any(
            coface in model.border_targets and model.is_border(coface, mask)
            for coface in h_cofaces
        ):
            continue
        if not local_pwc_link_condition(model, x, mask):
            continue

        counts["locally_admissible_masks"] += 1
        parity = len(e_set(model, x, h, mask)) % 2
        persists = persists_in_neighborhood(model, x, h, mask)
        counts["odd" if parity else "even"] += 1
        if bool(parity) != persists:
            counts["violations"] += 1

    return {
        "dim_x": dim_x,
        "dim_h": dim_h,
        "k": k,
        "m": m,
        "collar_voxels": len(model.voxels),
        "enumeration_mode": "complete_collar",
        **counts,
    }


def lower_rank_type(
    ambient_rank: int,
    dim_x: int,
    dim_h: int,
    k: int,
    m: int,
) -> dict:
    x, h = build_x_h(k, m, ambient_rank)
    border_targets = comparable_candidates(x) | {x}
    model = LocalVoxelModel(
        ambient_rank,
        collar_region({x}),
        border_targets,
    )
    h_cofaces = frozenset(
        cell
        for cell in comparable_candidates(h)
        if is_face(h, cell) and cell != h
    )
    counts = {
        "enumerated_masks": 0,
        "locally_admissible_masks": 0,
        "odd": 0,
        "even": 0,
        "violations": 0,
    }
    for mask in model.masks_containing(h):
        counts["enumerated_masks"] += 1
        if not model.is_border(x, mask):
            continue
        if any(
            coface in model.border_targets and model.is_border(coface, mask)
            for coface in h_cofaces
        ):
            continue
        if not local_pwc_link_condition(model, x, mask):
            continue
        counts["locally_admissible_masks"] += 1
        parity = len(e_set(model, x, h, mask)) % 2
        persists = persists_in_neighborhood(model, x, h, mask)
        counts["odd" if parity else "even"] += 1
        if bool(parity) != persists:
            counts["violations"] += 1
    return {
        "ambient_rank": ambient_rank,
        "dim_x": dim_x,
        "dim_h": dim_h,
        "k": k,
        "m": m,
        "collar_voxels": len(model.voxels),
        **counts,
    }


def lower_rank_inheritance() -> dict:
    """Directly close branch (ii) in ambient ranks one and two.

    In rank two only the positive-dimensional edge case needs a finite
    check; a top square has a surface boundary and rank one is
    structural.  For a rank-one poset, PWC means that its border is an
    even antichain, i.e. a separated union of 0-surfaces.
    """
    h: Cell = (1, 0)
    centers = closure(h)
    region = collar_region(centers)
    border_targets = set(centers)
    for center in centers:
        border_targets.update(comparable_candidates(center))
    model = LocalVoxelModel(2, region, border_targets)

    counts = {
        "ambient_rank_2_edge_collar_voxels": len(model.voxels),
        "ambient_rank_2_edge_masks": 0,
        "ambient_rank_2_edge_locally_admissible": 0,
        "ambient_rank_2_edge_pwc_neighborhoods": 0,
        "ambient_rank_2_edge_violations": 0,
        "border_cardinality_histogram": {},
    }
    for mask in model.masks_containing(h):
        counts["ambient_rank_2_edge_masks"] += 1
        if not all(
            local_pwc_link_condition(model, center, mask)
            for center in centers
        ):
            continue
        counts["ambient_rank_2_edge_locally_admissible"] += 1
        neighborhood = model.present_comparable_cells(h, mask)
        border = frozenset(
            cell
            for cell in neighborhood
            if not is_surface(theta_prime(neighborhood, cell), 0)
        )
        is_even_antichain = len(border) % 2 == 0 and all(
            not strictly_comparable(a, b)
            for a in border
            for b in border
            if a != b
        )
        key = str(len(border))
        histogram = counts["border_cardinality_histogram"]
        histogram[key] = histogram.get(key, 0) + 1
        if is_even_antichain:
            counts["ambient_rank_2_edge_pwc_neighborhoods"] += 1
        else:
            counts["ambient_rank_2_edge_violations"] += 1

    counts.update(
        {
            "ambient_rank_1": (
                "structural: the neighborhood of a top edge is its "
                "two-point 0-surface and has empty border"
            ),
            "ambient_rank_2_top_square": (
                "structural: the neighborhood is the square boundary, "
                "a discrete 1-surface with empty border"
            ),
        }
    )
    return counts


def lemma_43_square() -> dict:
    h: Cell = (1, 1, 0)
    boundary = frozenset(closure(h) - {h})

    # Close the border links of h and of every proper face of h.
    centers = boundary | {h}
    region = collar_region(centers)
    border_targets = set(centers)
    for center in centers:
        border_targets.update(comparable_candidates(center))
    model = LocalVoxelModel(3, region, border_targets)
    boundary_cells = tuple(sorted(boundary))

    # Precompute the exact local-PWC predicate for each center on its
    # own closed collar.  Vertex collars have 8 voxels, edge collars 12,
    # and the square collar 18.  The main 18-voxel sweep then performs
    # table lookups rather than repeated recursive surface tests.
    local_condition_tables = {}
    local_condition_supports = {}
    for center in sorted(centers):
        support = model.mask_of_voxels(collar_region({center}))
        table = {}
        submask = support
        while True:
            table[submask] = local_pwc_link_condition(model, center, submask)
            if submask == 0:
                break
            submask = (submask - 1) & support
        local_condition_supports[center] = support
        local_condition_tables[center] = table
        print(
            json.dumps(
                {
                    "precomputed_local_condition": {
                        "cell": center,
                        "dimension": sum(value % 2 for value in center),
                        "collar_voxels": support.bit_count(),
                        "states": len(table),
                    }
                },
                sort_keys=True,
            ),
            flush=True,
        )

    component_table = {}
    for signature in range(1 << len(boundary_cells)):
        cells = frozenset(
            cell
            for i, cell in enumerate(boundary_cells)
            if signature & (1 << i)
        )
        component_table[signature] = connected_components(cells)

    h_star_mask = model.mask_of_voxels(voxel_star(h))
    persistence_table = {}
    submask = h_star_mask
    while True:
        persistence_table[submask] = {
            cell: persists_in_neighborhood(model, cell, h, submask)
            for cell in boundary
        }
        if submask == 0:
            break
        submask = (submask - 1) & h_star_mask

    result = {
        "collar_voxels": len(model.voxels),
        "enumerated_masks": 0,
        "locally_admissible_masks": 0,
        "masks_with_fully_persisting_component": 0,
        "fully_persisting_components": 0,
        "components_equal_boundary": 0,
        "violations": 0,
        "component_size_histogram": {},
    }

    for mask in model.masks_containing(h):
        result["enumerated_masks"] += 1

        # This is the exact local PWC consequence needed by the claim.
        # Every border cell in closure(h) must have a 1-surface border
        # link.  Global PWC implies all these conditions.
        if not all(
            local_condition_tables[cell][mask & local_condition_supports[cell]]
            for cell in centers
        ):
            continue
        result["locally_admissible_masks"] += 1

        boundary_signature = sum(
            1 << i
            for i, cell in enumerate(boundary_cells)
            if model.is_border(cell, mask)
        )
        components = component_table[boundary_signature]
        persistence = persistence_table[mask & h_star_mask]

        mask_has_fully_persisting = False
        for component in components:
            if component and all(persistence.get(cell, False) for cell in component):
                mask_has_fully_persisting = True
                result["fully_persisting_components"] += 1
                size = str(len(component))
                histogram = result["component_size_histogram"]
                histogram[size] = histogram.get(size, 0) + 1
                if component == boundary and is_surface_1(component):
                    result["components_equal_boundary"] += 1
                else:
                    result["violations"] += 1
        if mask_has_fully_persisting:
            result["masks_with_fully_persisting_component"] += 1

    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("proof_closure_results.json"),
    )
    args = parser.parse_args()

    started = time.time()
    lemma_41: List[dict] = []
    for dim_x, dim_h in sorted(TYPES):
        row_started = time.time()
        row = lemma_41_type(dim_x, dim_h)
        row["seconds"] = round(time.time() - row_started, 6)
        print(json.dumps({"lemma_4_1": row}, sort_keys=True), flush=True)
        lemma_41.append(row)

    lower_rank_rows: List[dict] = []
    for ambient_rank, types in sorted(LOWER_RANK_TYPES.items()):
        for (dim_x, dim_h), (k, m) in sorted(types.items()):
            row = lower_rank_type(ambient_rank, dim_x, dim_h, k, m)
            print(json.dumps({"lower_rank": row}, sort_keys=True), flush=True)
            lower_rank_rows.append(row)

    lower_inheritance = lower_rank_inheritance()
    print(
        json.dumps(
            {"lower_rank_upper_free_inheritance": lower_inheritance},
            sort_keys=True,
        ),
        flush=True,
    )

    square_started = time.time()
    square = lemma_43_square()
    square["seconds"] = round(time.time() - square_started, 6)
    print(json.dumps({"lemma_4_3_square": square}, sort_keys=True), flush=True)

    module_path = Path(__file__).with_name("local_star_state.py")
    runner_path = Path(__file__)
    result = {
        "schema_version": 1,
        "scope": "ambient_rank_3",
        "admissibility": (
            "x in Delta X; h Delta-upper-free; and every relevant border "
            "cell has a discrete 1-surface border link"
        ),
        "uses_truncated_global_pwc_filter": False,
        "uses_random_sampling": False,
        "lemma_4_1": lemma_41,
        "lemma_4_1_total_violations": sum(row["violations"] for row in lemma_41),
        "lower_rank_containment": lower_rank_rows,
        "lower_rank_total_violations": sum(
            row["violations"] for row in lower_rank_rows
        ),
        "lower_rank_upper_free_inheritance": lower_inheritance,
        "lemma_4_3_square": square,
        "elapsed_seconds": round(time.time() - started, 6),
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_sha256": {
            module_path.name: sha256(module_path),
            runner_path.name: sha256(runner_path),
        },
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    assert result["lemma_4_1_total_violations"] == 0
    assert result["lower_rank_total_violations"] == 0
    assert lower_inheritance["ambient_rank_2_edge_masks"] == 48
    assert lower_inheritance["ambient_rank_2_edge_locally_admissible"] == 34
    assert lower_inheritance["ambient_rank_2_edge_pwc_neighborhoods"] == 34
    assert lower_inheritance["ambient_rank_2_edge_violations"] == 0
    assert square["violations"] == 0
    expected_lemma_41 = {
        (0, 1): (13, 0, 13),
        (0, 2): (88, 50, 38),
        (0, 3): (63, 0, 63),
        (1, 2): (2304, 1536, 768),
        (1, 3): (1536, 0, 1536),
        (2, 3): (1, 0, 1),
    }
    for row in lemma_41:
        key = (row["dim_x"], row["dim_h"])
        expected = expected_lemma_41[key]
        actual = (
            row["locally_admissible_masks"],
            row["odd"],
            row["even"],
        )
        assert actual == expected, (key, actual, expected)
    assert square["enumerated_masks"] == 196608
    assert square["locally_admissible_masks"] == 21289
    assert square["fully_persisting_components"] == 9926
    assert square["components_equal_boundary"] == 9926
    print(f"WROTE {args.output}", flush=True)


if __name__ == "__main__":
    main()
