# Static PWC Inheritance Theory

Reproducibility package for the computer-assisted portions of
*Face-Neighborhood Inheritance in P-Well-Composed Cubical Face Posets*.

The package contains the closed finite-state proof for Section 4, the
self-contained Appendix A regression verifier, frozen machine-readable
certificates, and deterministic tests. The main theorem does not depend
on random sampling.

## Proof status

- The truncated-global-PWC filter is not used.
- Lemma 4.1 is checked over explicit locally admissible collar states.
- The square case of Lemma 4.3 exhausts all \(3\cdot2^{16}=196{,}608\)
  masks in its closed 18-voxel collar.
- The lower-rank branch is checked directly.
- Appendix A is symbolic for every \(k\ge3\); its finite computation is
  a regression test only.

Frozen headline counts:

| Check | Result |
|---|---:|
| Lemma 4.1 total violations | 0 |
| Square masks | 196,608 |
| Locally admissible square masks | 21,289 |
| Fully persisting square components | 9,926 |
| Square-classification violations | 0 |
| Rank-2 edge masks / admissible masks | 48 / 34 |
| Lower-rank violations | 0 |
| Appendix A fixed-endpoint distances | \(k-1,k,k\) |

## Repository layout

- `section4/` — collar model, exhaustive proof runner, tests, certificate,
  and proof-dependency report.
- `appendix_a/` — admissibility and stabilizer regression verifier,
  certificate, and closure report.
- `reproducibility/` — execution environment and manuscript-to-certificate
  mapping.
- `manuscript/` — proof-closed canonical Markdown and the final consistency
  audit used to freeze this release.
- `verify_release.py` — one-command release verification.

## Reproduce

Python 3.12 is recommended; the code uses only the standard library.

```text
python verify_release.py
```

This command:

1. regenerates the Section 4 certificate in a temporary directory;
2. compares every stable proof field with the frozen certificate;
3. verifies the recorded source hashes;
4. runs the five deterministic Section 4 tests; and
5. checks the Appendix A certificate for \(k=3,\ldots,10\).

Typical runtime is under two minutes on a desktop computer. Generated
temporary results are not written into the repository.

## Evidence classes

The release distinguishes:

- exhaustive finite proof components;
- symbolic deductions;
- deterministic regression checks; and
- random evidence for the separate No-Shrinkage Conjecture.

Random conjecture evidence is discussed in the manuscript but is not
part of the proof dependency chain or this release verifier.

## Citation and license

Citation metadata are provided in `CITATION.cff`. The archival DOI will
be added after the GitHub release is deposited with Zenodo.

The code and accompanying repository documentation are released under
the MIT License.
