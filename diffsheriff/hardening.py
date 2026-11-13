"""
ELF binary hardening auditor. Checks NX, PIE, RELRO levels, and stack canaries.
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class HardeningResult:
    nx: bool
    pie: bool
    relro: str  # "none", "partial", "full"
    canary: bool
    indicators: dict = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def inspect_elf_hardening(elf_path: Path) -> HardeningResult:
    from elftools.elf.elffile import ELFFile

    if not elf_path.exists():
        raise FileNotFoundError(f"Target binary not found: {elf_path}")

    with open(elf_path, "rb") as f:
        elf = ELFFile(f)
        if elf.elfclass != 64 or elf.header["e_machine"] != "EM_X86_64":
            raise ValueError("Target must be a 64-bit x86_64 ELF binary")
        if elf.header["e_type"] not in {"ET_EXEC", "ET_DYN"}:
            raise ValueError("Target ELF must be executable")

        segments = list(elf.iter_segments())
        stack_flags = [s["p_flags"] for s in segments if s["p_type"] == "PT_GNU_STACK"]
        nx = bool(stack_flags) and all(flags & 0x1 == 0 for flags in stack_flags)
        has_relro_segment = any(s["p_type"] == "PT_GNU_RELRO" for s in segments)
        has_interpreter = any(s["p_type"] == "PT_INTERP" for s in segments)
        dynamic_flags = []
        bind_now = False
        pie_marker = False
        # Program headers also work when section headers have been stripped.
        for segment in segments:
            if segment["p_type"] != "PT_DYNAMIC":
                continue
            for tag in segment.iter_tags():
                if tag.entry.d_tag in {"DT_BIND_NOW", "DT_FLAGS", "DT_FLAGS_1"}:
                    dynamic_flags.append(
                        {"tag": tag.entry.d_tag, "value": tag.entry.d_val}
                    )
                if tag.entry.d_tag == "DT_BIND_NOW":
                    bind_now = True
                elif tag.entry.d_tag == "DT_FLAGS" and (tag.entry.d_val & 0x8):
                    bind_now = True
                elif tag.entry.d_tag == "DT_FLAGS_1":
                    bind_now |= bool(tag.entry.d_val & 0x1)
                    pie_marker |= bool(tag.entry.d_val & 0x08000000)

        pie = elf.header["e_type"] == "ET_DYN" and (pie_marker or has_interpreter)

        if has_relro_segment and bind_now:
            relro = "full"
        elif has_relro_segment:
            relro = "partial"
        else:
            relro = "none"

        # 4. Stack Canary: Check for __stack_chk_fail in dynsym or symtab
        symbol_tables = [
            elf.get_section_by_name(".dynsym"),
            elf.get_section_by_name(".symtab"),
        ]
        symbols = {
            sym.name
            for table in symbol_tables
            if table is not None
            for sym in table.iter_symbols()
        }
        canary_symbols = sorted(
            symbols & {"__stack_chk_fail", "__stack_chk_fail_local"}
        )
        # Symbol names are indicators, not proof of compile flags or code coverage.
        sanitizer_symbols = {}
        for family in ("asan", "ubsan", "msan", "tsan", "lsan"):
            matches = sorted(
                name for name in symbols if name.startswith(f"__{family}_")
            )
            if matches:
                sanitizer_symbols[family] = matches
        indicators = {
            "elf_type": elf.header["e_type"],
            "gnu_stack_flags": stack_flags,
            "has_interpreter": has_interpreter,
            "df_1_pie": pie_marker,
            "gnu_relro_segment": has_relro_segment,
            "dynamic_flags": dynamic_flags,
            "canary_symbols": canary_symbols,
            "symbol_tables": [
                table.name for table in symbol_tables if table is not None
            ],
            "fortify_symbols": sorted(
                name
                for name in symbols
                if name.startswith("__") and name.endswith("_chk")
            ),
            "sanitizer_symbols": sanitizer_symbols,
        }

    return HardeningResult(nx, pie, relro, bool(canary_symbols), indicators)


def compare_hardening(
    base: HardeningResult, patch: HardeningResult
) -> Tuple[bool, List[str]]:
    """
    Checks for hardening degradation from base to patch binary.
    Returns (degradation_detected, warnings).
    """
    warnings: List[str] = []
    if base.nx and not patch.nx:
        warnings.append("Degradation: NX protection was disabled in patched binary.")
    if base.pie and not patch.pie:
        warnings.append("Degradation: PIE was disabled in patched binary.")
    if base.canary and not patch.canary:
        warnings.append(
            "Degradation: Stack canary protection was disabled in patched binary."
        )

    relro_order = {"none": 0, "partial": 1, "full": 2}
    if relro_order.get(patch.relro, 0) < relro_order.get(base.relro, 0):
        warnings.append(
            "Degradation: RELRO level was downgraded from "
            f"{base.relro} to {patch.relro}."
        )

    return len(warnings) > 0, warnings
