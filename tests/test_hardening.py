"""ELF parsing checks against minimal real binary fixtures."""

import struct
import pytest

from diffsheriff.hardening import (
    HardeningResult,
    compare_hardening,
    inspect_elf_hardening,
)


def elf_fixture(
    path,
    *,
    machine=62,
    executable_stack=False,
    pie=True,
    marker=True,
    interpreter=False,
    bind_now=False,
):
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
        4 + int(interpreter),
        64,
        0,
        0,
    )
    stack = struct.pack(
        "<IIQQQQQQ", 0x6474E551, 7 if executable_stack else 6, 0, 0, 0, 0, 0, 16
    )
    relro = struct.pack("<IIQQQQQQ", 0x6474E552, 4, 0, 0, 0, 0, 0, 1)
    flags = (0x08000000 if marker else 0) | int(bind_now)
    offset = 64 + 56 * (4 + int(interpreter))
    data = struct.pack("<QQQQQQ", 0x6FFFFFFB, flags, 5, offset + 48, 0, 0)
    load = struct.pack("<IIQQQQQQ", 1, 4, 0, 0, 0, offset + 49, offset + 49, 1)
    dynamic = struct.pack(
        "<IIQQQQQQ",
        2,
        6,
        offset,
        0,
        0,
        len(data),
        len(data),
        8,
    )
    interp = struct.pack("<IIQQQQQQ", 3, 4, 0, 0, 0, 0, 0, 1) if interpreter else b""
    path.write_bytes(
        ident + header + stack + relro + load + dynamic + interp + data + b"\0"
    )


def test_elf_hardening_reads_real_headers(tmp_path):
    path = tmp_path / "binary"
    elf_fixture(path)
    result = inspect_elf_hardening(path)
    assert (result.nx, result.pie, result.relro, result.canary) == (
        True,
        True,
        "partial",
        False,
    )
    assert result.to_dict()["indicators"] == {
        "elf_type": "ET_DYN",
        "gnu_stack_flags": [6],
        "has_interpreter": False,
        "df_1_pie": True,
        "gnu_relro_segment": True,
        "dynamic_flags": [{"tag": "DT_FLAGS_1", "value": 0x08000000}],
        "canary_symbols": [],
        "symbol_tables": [],
        "fortify_symbols": [],
        "sanitizer_symbols": {},
    }
    elf_fixture(path, executable_stack=True, pie=False)
    result = inspect_elf_hardening(path)
    assert (result.nx, result.pie, result.relro, result.canary) == (
        False,
        False,
        "partial",
        False,
    )


@pytest.mark.parametrize(
    "marker,interpreter,pie",
    [(False, False, False), (False, True, True), (True, False, True)],
)
def test_pie_requires_executable_evidence(tmp_path, marker, interpreter, pie):
    path = tmp_path / "binary"
    elf_fixture(path, marker=marker, interpreter=interpreter, bind_now=True)
    result = inspect_elf_hardening(path)
    assert result.pie is pie
    assert result.relro == "full"
    assert result.indicators["dynamic_flags"][0]["value"] & 1


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


def test_elf_symbol_evidence_is_separate_from_build_labels(tmp_path):
    path = tmp_path / "binary"
    elf_fixture(path)
    data = bytearray(path.read_bytes())
    section_names = b"\0.shstrtab\0.strtab\0.symtab\0"
    strings = bytearray(b"\0")
    symbols = bytearray(24)
    for name in (
        "__stack_chk_fail",
        "__memcpy_chk",
        "__asan_init",
        "__ubsan_handle_add_overflow",
        "ordinary",
    ):
        symbols.extend(struct.pack("<IBBHQQ", len(strings), 0x12, 0, 0, 0, 0))
        strings.extend(name.encode() + b"\0")
    sections = [bytes(64)]
    for name, kind, body, link, entry_size in (
        (1, 3, section_names, 0, 0),
        (11, 3, strings, 0, 0),
        (19, 2, symbols, 2, 24),
    ):
        sections.append(
            struct.pack(
                "<IIQQQQIIQQ",
                name,
                kind,
                0,
                0,
                len(data),
                len(body),
                link,
                1 if kind == 2 else 0,
                1,
                entry_size,
            )
        )
        data.extend(body)
    struct.pack_into("<Q", data, 40, len(data))
    struct.pack_into("<HHH", data, 58, 64, len(sections), 1)
    path.write_bytes(data + b"".join(sections))
    result = inspect_elf_hardening(path)
    assert result.canary
    assert result.indicators["symbol_tables"] == [".symtab"]
    assert result.indicators["fortify_symbols"] == ["__memcpy_chk"]
    assert result.indicators["sanitizer_symbols"] == {
        "asan": ["__asan_init"],
        "ubsan": ["__ubsan_handle_add_overflow"],
    }
