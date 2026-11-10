"""ELF parsing checks against minimal real binary fixtures."""

import struct
import pytest

from diffsheriff.hardening import (
    HardeningResult,
    compare_hardening,
    inspect_elf_hardening,
)


def elf_fixture(path, *, machine=62, executable_stack=False, pie=True):
    ident = b"\x7fELF" + bytes([2, 1, 1]) + bytes(9)
    header = struct.pack(
        "<HHIQQQIHHHHHH",
        3 if pie else 2,
        machine,
        1,
        0x1000,
        64,
        0,
        0,
        64,
        56,
        2,
        64,
        0,
        0,
    )
    stack = struct.pack(
        "<IIQQQQQQ", 0x6474E551, 7 if executable_stack else 6, 0, 0, 0, 0, 0, 16
    )
    relro = struct.pack("<IIQQQQQQ", 0x6474E552, 4, 0, 0, 0, 0, 0, 1)
    path.write_bytes(ident + header + stack + relro)


def test_elf_hardening_reads_real_headers(tmp_path):
    path = tmp_path / "binary"
    elf_fixture(path)
    assert inspect_elf_hardening(path) == HardeningResult(True, True, "partial", False)
    elf_fixture(path, executable_stack=True, pie=False)
    assert inspect_elf_hardening(path) == HardeningResult(
        False, False, "partial", False
    )


def test_non_x86_64_elf_is_rejected(tmp_path):
    path = tmp_path / "binary"
    elf_fixture(path, machine=183)
    with pytest.raises(ValueError, match="x86_64"):
        inspect_elf_hardening(path)


def test_hardening_downgrades_are_all_reported():
    degraded, warnings = compare_hardening(
        HardeningResult(True, True, "full", True),
        HardeningResult(False, False, "none", False),
    )
    assert degraded and len(warnings) == 4
