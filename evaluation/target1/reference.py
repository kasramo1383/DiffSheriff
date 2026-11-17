#!/usr/bin/env python3
"""Expected driver status for the documented bounded zlib compression contract.

zlib.h documents Z_FINISH/Z_STREAM_END and deflateBound. All byte strings in
this selected size range are valid compression data, including memory-error
reproducers. This predicts API completion/status, not compressed output bytes.
"""

import json
import sys

MAX_INPUT_BYTES = 65536


def expected_result(payload):
    if len(payload) > MAX_INPUT_BYTES:
        raise ValueError("outside the reviewed zlib input scope (65536 bytes)")
    return {"exit_code": 0, "stdout": "", "stderr": "", "valid_input": True}


def main():
    try:
        result = expected_result(sys.stdin.buffer.read(MAX_INPUT_BYTES + 1))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
