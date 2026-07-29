"""Verify every frozen proof certificate in this release."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SECTION4 = ROOT / "section4"
APPENDIX_A = ROOT / "appendix_a"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def without_runtime_fields(value):
    if isinstance(value, dict):
        return {
            key: without_runtime_fields(child)
            for key, child in value.items()
            if key not in {"elapsed_seconds", "runtime", "seconds", "source_sha256"}
        }
    if isinstance(value, list):
        return [without_runtime_fields(child) for child in value]
    return value


def verify_section4() -> None:
    frozen_path = SECTION4 / "proof_closure_results.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))

    for filename, expected in frozen["source_sha256"].items():
        actual = sha256(SECTION4 / filename)
        assert actual == expected, (filename, actual, expected)

    with tempfile.TemporaryDirectory(prefix="pwc-proof-") as temp_dir:
        reproduced_path = Path(temp_dir) / "proof_closure_results.json"
        subprocess.run(
            [
                sys.executable,
                "run_proof_closure.py",
                "--output",
                str(reproduced_path),
            ],
            cwd=SECTION4,
            check=True,
        )
        reproduced = json.loads(reproduced_path.read_text(encoding="utf-8"))

    assert without_runtime_fields(reproduced) == without_runtime_fields(frozen)
    subprocess.run(
        [sys.executable, "-m", "unittest", "-v", "test_proof_closure.py"],
        cwd=SECTION4,
        check=True,
    )


def verify_appendix_a() -> None:
    sys.path.insert(0, str(APPENDIX_A))
    from verify_appendix_a import verify  # pylint: disable=import-outside-toplevel

    frozen = json.loads(
        (APPENDIX_A / "appendix_a_results.json").read_text(encoding="utf-8")
    )
    regression = frozen["regression_range"]
    actual_rows = [
        verify(k) for k in range(regression["k_min"], regression["k_max"] + 1)
    ]
    assert actual_rows == regression["rows"]
    assert regression["violations"] == 0


def main() -> None:
    verify_section4()
    verify_appendix_a()
    print("RELEASE VERIFICATION PASSED")
    print("Section 4: frozen certificate reproduced; 5 tests passed")
    print("Appendix A: k=3..10 regression certificate reproduced")


if __name__ == "__main__":
    main()
