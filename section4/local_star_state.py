"""Canonical finite local-state model for the Section 4 proof closure.

Cells use doubled coordinates. Top-dimensional voxels therefore have
odd coordinates. A finite voxel mask represents the intersection of an
ambient cubical complex with a rigorously closed local voxel region.

The key design choice is that no truncated-complex PWC test is used.
Instead, global PWC contributes only its exact local consequence:
for every border cell z under consideration, theta'_{Delta X}(z) is a
discrete 1-surface.  The voxel region is enlarged until the border
status of every cell in those links is determined by the mask.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product
from typing import Dict, FrozenSet, Iterable, Iterator, List, Sequence, Set, Tuple

Cell = Tuple[int, ...]


def dim(cell: Cell) -> int:
    return sum(value % 2 for value in cell)


def is_face(sub: Cell, sup: Cell) -> bool:
    for lower, upper in zip(sub, sup):
        if upper % 2 == 0:
            if lower != upper:
                return False
        elif abs(lower - upper) > 1:
            return False
    return True


def strictly_comparable(a: Cell, b: Cell) -> bool:
    return a != b and (is_face(a, b) or is_face(b, a))


@lru_cache(maxsize=None)
def closure(cell: Cell) -> FrozenSet[Cell]:
    choices: List[Sequence[int]] = []
    for value in cell:
        choices.append((value - 1, value, value + 1) if value % 2 else (value,))
    return frozenset(product(*choices))


@lru_cache(maxsize=None)
def voxel_star(cell: Cell) -> FrozenSet[Cell]:
    """All top-dimensional grid voxels having ``cell`` as a face."""
    choices: List[Sequence[int]] = []
    for value in cell:
        choices.append((value,) if value % 2 else (value - 1, value + 1))
    return frozenset(product(*choices))


def connected_components(cells: Iterable[Cell]) -> Tuple[FrozenSet[Cell], ...]:
    remaining = set(cells)
    components: List[FrozenSet[Cell]] = []
    while remaining:
        seed = remaining.pop()
        component = {seed}
        stack = [seed]
        while stack:
            current = stack.pop()
            adjacent = {other for other in remaining if strictly_comparable(current, other)}
            remaining.difference_update(adjacent)
            component.update(adjacent)
            stack.extend(adjacent)
        components.append(frozenset(component))
    return tuple(components)


@lru_cache(maxsize=None)
def theta_prime(cells: FrozenSet[Cell], h: Cell) -> FrozenSet[Cell]:
    return frozenset(cell for cell in cells if strictly_comparable(cell, h))


@lru_cache(maxsize=None)
def is_surface(cells: FrozenSet[Cell], rank: int) -> bool:
    if rank == -1:
        return not cells
    if rank == 0:
        return len(cells) == 2
    if len(connected_components(cells)) != 1:
        return False
    return all(is_surface(theta_prime(cells, cell), rank - 1) for cell in cells)


@lru_cache(maxsize=None)
def is_surface_1(cells: FrozenSet[Cell]) -> bool:
    """Fast exact specialization of the recursive discrete 1-surface test."""
    if not cells or len(connected_components(cells)) != 1:
        return False
    for cell in cells:
        neighbors = theta_prime(cells, cell)
        if len(neighbors) != 2:
            return False
    return True


def complex_from_voxels(voxels: Iterable[Cell]) -> FrozenSet[Cell]:
    cells: Set[Cell] = set()
    for voxel in voxels:
        cells.update(closure(voxel))
    return frozenset(cells)


@lru_cache(maxsize=None)
def border_status_from_incident_voxels(
    ambient_rank: int,
    cell: Cell,
    occupied_incident_voxels: FrozenSet[Cell],
) -> bool:
    """Exact rank-three border status of ``cell``.

    A cell's strict neighborhood is determined by the occupied voxels in
    its candidate-voxel star.  The returned value is False when the cell
    is absent.
    """
    if not occupied_incident_voxels:
        return False
    cells = complex_from_voxels(occupied_incident_voxels)
    if cell not in cells:
        return False
    return not is_surface(theta_prime(cells, cell), ambient_rank - 1)


@lru_cache(maxsize=None)
def canonical_border_status(
    ambient_rank: int,
    cell_dimension: int,
    occupied_sign_patterns: FrozenSet[Tuple[int, ...]],
) -> bool:
    """Border status modulo translation and coordinate permutation.

    Only the signs on the cell's fixed axes matter.  This reduces all
    border-table construction to 277 canonical occupancy patterns over
    dimensions 0, 1, 2, and 3, rather than recomputing translated copies.
    """
    if not occupied_sign_patterns:
        return False
    codimension = ambient_rank - cell_dimension
    canonical_cell: Cell = tuple([0] * codimension + [1] * cell_dimension)
    occupied_voxels = frozenset(
        tuple(list(signs) + [1] * cell_dimension)
        for signs in occupied_sign_patterns
    )
    return border_status_from_incident_voxels(
        ambient_rank, canonical_cell, occupied_voxels
    )


def incident_sign_pattern(cell: Cell, voxel: Cell) -> Tuple[int, ...]:
    return tuple(
        voxel[axis] - cell[axis]
        for axis in range(len(cell))
        if cell[axis] % 2 == 0
    )


def comparable_candidates(cell: Cell) -> FrozenSet[Cell]:
    full_star_complex = complex_from_voxels(voxel_star(cell))
    return frozenset(
        candidate
        for candidate in full_star_complex
        if strictly_comparable(cell, candidate)
    )


def collar_region(centers: Iterable[Cell]) -> FrozenSet[Cell]:
    """Voxel region closing all border decisions in the centers' links.

    For every center z, the region contains the complete voxel star of
    every possible cell comparable with z.  Hence membership in Delta X
    is determined for every element of theta'_X(z).
    """
    voxels: Set[Cell] = set()
    for center in centers:
        voxels.update(voxel_star(center))
        for comparable in comparable_candidates(center):
            voxels.update(voxel_star(comparable))
    return frozenset(voxels)


class LocalVoxelModel:
    def __init__(
        self,
        ambient_rank: int,
        voxels: Iterable[Cell],
        border_targets: Iterable[Cell],
    ):
        self.ambient_rank = ambient_rank
        self.voxels: Tuple[Cell, ...] = tuple(sorted(set(voxels)))
        self.index = {voxel: i for i, voxel in enumerate(self.voxels)}
        self.border_targets: FrozenSet[Cell] = frozenset(border_targets)
        self.star_masks: Dict[Cell, int] = {}
        self.border_tables: Dict[Cell, Dict[int, bool]] = {}

        for cell in self.border_targets:
            incident = voxel_star(cell)
            if not incident.issubset(self.index):
                missing = sorted(incident.difference(self.index))
                raise ValueError(f"region is not closed for {cell}; missing {missing}")
            star_mask = self.mask_of_voxels(incident)
            self.star_masks[cell] = star_mask
            table: Dict[int, bool] = {}
            submask = star_mask
            while True:
                occupied = frozenset(
                    self.voxels[i]
                    for i in range(len(self.voxels))
                    if submask & (1 << i)
                )
                sign_patterns = frozenset(
                    incident_sign_pattern(cell, voxel) for voxel in occupied
                )
                table[submask] = canonical_border_status(
                    self.ambient_rank, dim(cell), sign_patterns
                )
                if submask == 0:
                    break
                submask = (submask - 1) & star_mask
            self.border_tables[cell] = table

    def mask_of_voxels(self, voxels: Iterable[Cell]) -> int:
        mask = 0
        for voxel in voxels:
            mask |= 1 << self.index[voxel]
        return mask

    def occupied_voxels(self, mask: int) -> FrozenSet[Cell]:
        return frozenset(
            voxel
            for i, voxel in enumerate(self.voxels)
            if mask & (1 << i)
        )

    def cell_present(self, cell: Cell, mask: int) -> bool:
        incident = voxel_star(cell)
        return any(
            voxel in self.index and mask & (1 << self.index[voxel])
            for voxel in incident
        )

    def is_border(self, cell: Cell, mask: int) -> bool:
        star_mask = self.star_masks[cell]
        return self.border_tables[cell][mask & star_mask]

    def border_link(self, center: Cell, mask: int) -> FrozenSet[Cell]:
        return frozenset(
            cell
            for cell in comparable_candidates(center)
            if cell in self.border_targets and self.is_border(cell, mask)
        )

    def present_comparable_cells(self, center: Cell, mask: int) -> FrozenSet[Cell]:
        return frozenset(
            cell
            for cell in comparable_candidates(center)
            if self.cell_present(cell, mask)
        )

    def masks_containing(self, cell: Cell) -> Iterator[int]:
        required = self.mask_of_voxels(voxel_star(cell))
        for mask in range(1 << len(self.voxels)):
            if mask & required:
                yield mask


def build_x_h(k: int, m: int, ambient_rank: int = 3) -> Tuple[Cell, Cell]:
    dim_x = ambient_rank - k - m
    x = tuple([0] * (k + m) + [1] * dim_x)
    h = tuple([1] * k + [0] * m + [1] * dim_x)
    return x, h  # type: ignore[return-value]


def local_pwc_link_condition(model: LocalVoxelModel, cell: Cell, mask: int) -> bool:
    """Necessary local consequence of global PWC at a border cell."""
    if not model.is_border(cell, mask):
        return True
    return is_surface(
        model.border_link(cell, mask),
        model.ambient_rank - 2,
    )


def e_set(model: LocalVoxelModel, x: Cell, h: Cell, mask: int) -> FrozenSet[Cell]:
    theta_x = model.present_comparable_cells(x, mask)
    neighborhood_h = model.present_comparable_cells(h, mask)
    theta_x_in_neighborhood_h = frozenset(
        cell
        for cell in neighborhood_h
        if cell != x and strictly_comparable(cell, x)
    )
    return frozenset((theta_x - theta_x_in_neighborhood_h) - {h})


def persists_in_neighborhood(
    model: LocalVoxelModel, x: Cell, h: Cell, mask: int
) -> bool:
    neighborhood_h = model.present_comparable_cells(h, mask)
    theta_x_in_neighborhood_h = frozenset(
        cell
        for cell in neighborhood_h
        if cell != x and strictly_comparable(cell, x)
    )
    return not is_surface(
        theta_x_in_neighborhood_h,
        model.ambient_rank - 2,
    )
