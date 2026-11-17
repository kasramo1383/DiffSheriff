#!/usr/bin/env python3
"""Fixed, reviewed PNG fixture expectations; unknown bytes have no oracle result.

The target uses native-format simplified reading with no palette buffer. Its
selected RGBA fixture completes; indexed-color fixtures and empty input reject.
See docs/target_scenarios.md for the independent png.h contract. This script is
not configured as a general reduced-input reference.
"""

import hashlib
import json
import sys

REVIEWED = {
    "546f711f1f5b493ad7a79a5ec0c37f30e35f59be97b92731a9ddb01a225df5d8": {
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
        "valid_input": True,
    },
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
        "exit_code": 2,
        "stdout": "",
        "stderr": "",
        "valid_input": False,
    },
    "a0d210e0261eb720677c61b59245b653eb3182cc0e089282971443397527f89a": {
        "exit_code": 2,
        "stdout": "",
        "stderr": "",
        "valid_input": False,
    },
    "00c59d578badd331af4b60d7d88eb17d26875f2ab7cbb7742dd9e4e5a3335db6": {
        "exit_code": 2,
        "stdout": "",
        "stderr": "",
        "valid_input": False,
    },
}


def main():
    digest = hashlib.sha256(sys.stdin.buffer.read()).hexdigest()
    if digest not in REVIEWED:
        print("No reviewed expectation for these PNG bytes", file=sys.stderr)
        return 2
    print(json.dumps(REVIEWED[digest]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
