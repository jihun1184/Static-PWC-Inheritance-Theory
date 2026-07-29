# Manuscript-to-certificate map

## Section 4 and Section 6

| Manuscript item | Certificate path | JSON field |
|---|---|---|
| Lemma 4.1 six-type table | `section4/proof_closure_results.json` | `lemma_4_1` |
| Lemma 4.1 violation total | same | `lemma_4_1_total_violations` |
| Lemma 4.3 square table | same | `lemma_4_3_square` |
| Lower-rank parity table | same | `lower_rank_containment` |
| Rank-2 upper-free edge case | same | `lower_rank_upper_free_inheritance` |
| Proof-method declarations | same | `uses_random_sampling`, `uses_truncated_global_pwc_filter` |
| Frozen execution environment | same | `runtime` |
| Frozen source hashes | same | `source_sha256` |

Headline square fields:

| Manuscript quantity | JSON field | Frozen value |
|---|---|---:|
| masks containing the square | `lemma_4_3_square.enumerated_masks` | 196,608 |
| locally admissible masks | `lemma_4_3_square.locally_admissible_masks` | 21,289 |
| fully persisting components | `lemma_4_3_square.fully_persisting_components` | 9,926 |
| components equal to the square boundary | `lemma_4_3_square.components_equal_boundary` | 9,926 |
| violations | `lemma_4_3_square.violations` | 0 |

## Appendix A

| Manuscript item | Certificate path | JSON field |
|---|---|---|
| Coordinate model and basepoint | `appendix_a/appendix_a_results.json` | `model` |
| Three fixed endpoints | same | `fixed_endpoint_classification` |
| \(k=3,\ldots,10\) regression | same | `regression_range` |
| Global attainment at \(k=3\) | same | `global_attainment` |

The general Appendix A theorem is symbolic. The JSON file records
regression checks and the retained exact-cover result; it is not the
exhaustiveness basis of the general-\(k\) statement.
