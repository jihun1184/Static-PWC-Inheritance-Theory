
# Static PWC Inheritance Theory

Reproducibility package for the computer-assisted components supporting
*Face-Neighborhood Inheritance in P-Well-Composed Posets*.

This repository contains the closed finite-state verification for Section 4,
a deterministic regression verifier for the symbolic argument in Appendix A,
frozen machine-readable certificates, and reproducibility tests. No theorem in
the manuscript depends on random sampling.

## Verification status

- The truncated-global-PWC filter is not used.
- Lemma 4.1 is verified over explicitly defined locally admissible collar states.
- The square case of Lemma 4.3 exhausts all \(3\cdot2^{16}=196{,}608\)
  masks in its closed 18-voxel collar.
- The lower-rank cases are verified directly.
- Appendix A is proved symbolically for every \(k\ge3\); the finite computation
  included here serves only as a deterministic regression check.

Frozen headline counts:

| Check                                |      Result |
| ------------------------------------ | ----------: |
| Lemma 4.1 total violations           |           0 |
| Square masks                         |     196,608 |
| Locally admissible square masks      |      21,289 |
| Fully persisting square components   |       9,926 |
| Square-classification violations     |           0 |
| Rank-2 edge masks / admissible masks |     48 / 34 |
| Lower-rank violations                |           0 |
| Appendix A fixed-endpoint distances  | \(k-1,k,k\) |

## Repository layout

- `section4/` — collar model, exhaustive verification runner, tests, and
  frozen certificate.
- `appendix_a/` — admissibility and stabilizer regression verifier and
  frozen certificate.
- `reproducibility/` — execution environment, source hashes, and
  theorem-to-certificate mapping.
- `verify_release.py` — one-command release verification.

The manuscript source is maintained separately and is not included in this
repository.

## Reproduce

Python 3.12 is recommended. The verification code uses only the Python
standard library.

```text
python verify_release.py
```

This command:

1. regenerates the Section 4 certificate in a temporary directory;
2. compares every stable verification field with the frozen certificate;
3. verifies the recorded source hashes;
4. runs the five deterministic Section 4 tests; and
5. checks the Appendix A regression certificate for \(k=3,\ldots,10\).

Typical runtime is under two minutes on a desktop computer. Temporary results
are not written into the repository.

## Evidence classes

The repository distinguishes among:

- exhaustive finite verification;
- symbolic mathematical deductions;
- deterministic regression checks; and
- random experimental evidence concerning a separate conjecture.

Only the first three categories support the proved results. Random experimental
evidence is not part of the theorem dependency chain or the release verifier.

## Citation and license

Citation metadata are provided in `CITATION.cff`. The archival DOI will be
added after the GitHub release is deposited with Zenodo.

The code and accompanying repository documentation are released under the
MIT License.
