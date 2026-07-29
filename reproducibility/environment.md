# Execution environment

## Frozen certificate environment

- Python: 3.12.13
- Platform: Windows 10
- Third-party Python dependencies: none
- Random sampling in proof computations: none
- Truncated-global-PWC filter: not used

The verification code is platform-independent standard-library Python.
Continuous integration runs the same checks on Python 3.12.

## Commands

Full release verification:

```text
python verify_release.py
```

Individual Section 4 proof computation and tests:

```text
cd section4
python run_proof_closure.py --output reproduced_results.json
python -m unittest -v test_proof_closure.py
```

Appendix A regression:

```text
cd appendix_a
python verify_appendix_a.py
```

`verify_release.py` is preferred because it regenerates results outside
the working tree and compares them with the frozen certificates.
