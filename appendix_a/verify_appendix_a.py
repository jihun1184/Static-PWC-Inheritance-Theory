"""Deterministic verification of the self-contained Appendix A model."""

from itertools import product


ALPHABET = ("A", "F", "T")


def admissible(word):
    return "A" in word


def fixed_by_stabilizer_of_v(word):
    """Stab(A,F,...,F) fixes coordinate 0 and permutes the rest."""
    return len(set(word[1:])) <= 1


def hamming(left, right):
    return sum(a != b for a, b in zip(left, right))


def verify(k):
    states = list(product(ALPHABET, repeat=k))
    e_states = [word for word in states if admissible(word)]
    p0 = ("A",) * k
    v = ("A",) + ("F",) * (k - 1)
    fixed_endpoints = [
        word
        for word in e_states
        if word not in {p0, v} and fixed_by_stabilizer_of_v(word)
    ]
    expected = {
        ("A",) + ("T",) * (k - 1),
        ("F",) + ("A",) * (k - 1),
        ("T",) + ("A",) * (k - 1),
    }

    assert len(e_states) == 3**k - 2**k
    assert len(e_states) % 2 == 1
    assert p0 in e_states
    assert len(e_states) - 1 == 3**k - 2**k - 1
    assert set(fixed_endpoints) == expected
    assert sorted(hamming(v, word) for word in fixed_endpoints) == [
        k - 1,
        k,
        k,
    ]

    # The locally sharp orbit pairs states with the same unique A-position.
    sharp_pairs = set()
    for a_position in range(k):
        left = tuple("A" if i == a_position else "F" for i in range(k))
        right = tuple("A" if i == a_position else "T" for i in range(k))
        assert admissible(left) and admissible(right)
        assert hamming(left, right) == k - 1
        sharp_pairs.add(frozenset((left, right)))
    assert len(sharp_pairs) == k
    assert len(set().union(*sharp_pairs)) == 2 * k

    return {
        "k": k,
        "admissible_states": len(e_states),
        "matching_domain_states": len(e_states) - 1,
        "fixed_endpoint_distances": [k - 1, k, k],
        "sharp_orbit_pairs": k,
    }


if __name__ == "__main__":
    print("k  |E|  |E\\{p0}|  fixed distances  sharp pairs")
    for rank_gap in range(3, 11):
        row = verify(rank_gap)
        print(
            f"{row['k']:>2}  {row['admissible_states']:>5}  "
            f"{row['matching_domain_states']:>8}  "
            f"{str(row['fixed_endpoint_distances']):>15}  "
            f"{row['sharp_orbit_pairs']:>11}"
        )
