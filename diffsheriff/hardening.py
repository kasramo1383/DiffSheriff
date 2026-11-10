"""
ELF binary hardening auditor. Checks NX, PIE, RELRO levels, and stack canaries.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
from elftools.elf.elffile import ELFFile


@dataclass
class HardeningResult:
    nx: bool
    pie: bool
    relro: str  # "none", "partial", "full"
    canary: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "nx": self.nx,
            "pie": self.pie,
            "relro": self.relro,
            "canary": self.canary,
        }


def inspect_elf_hardening(elf_path: Path) -> HardeningResult:
    if not elf_path.exists():
        raise FileNotFoundError(f"Target binary not found: {elf_path}")

    with open(elf_path, "rb") as f:
        elf = ELFFile(f)

        # 1. NX check: Inspect PT_GNU_STACK segment
        nx = False
        for seg in elf.iter_segments():
            if seg["p_type"] == "PT_GNU_STACK":
                # If PF_X (0x1) is unset, stack is non-executable
                nx = (seg["p_flags"] & 0x1) == 0
                break

        # 2. PIE check: ET_DYN indicates position independent executable
        pie = elf.header["e_type"] == "ET_DYN"

        # 3. RELRO check: GNU_RELRO segment + BIND_NOW tag
        has_relro_segment = any(
            s["p_type"] == "PT_GNU_RELRO" for s in elf.iter_segments()
        )
        dynamic_sec = elf.get_section_by_name(".dynamic")
        bind_now = False
        if dynamic_sec:
            for tag in dynamic_sec.iter_tags():
                if tag.entry.d_tag == "DT_BIND_NOW":
                    bind_now = True
                elif tag.entry.d_tag == "DT_FLAGS" and (tag.entry.d_val & 0x8):
                    bind_now = True
                elif tag.entry.d_tag == "DT_FLAGS_1" and (tag.entry.d_val & 0x1):
                    bind_now = True

        if has_relro_segment and bind_now:
            relro = "full"
        elif has_relro_segment:
            relro = "partial"
        else:
            relro = "none"

        # 4. Stack Canary: Check for __stack_chk_fail in dynsym or symtab
        canary = False
        symbol_tables = [
            elf.get_section_by_name(".dynsym"),
            elf.get_section_by_name(".symtab"),
        ]
        canary = any(
            sym.name == "__stack_chk_fail"
            for table in symbol_tables
            if table is not None
            for sym in table.iter_symbols()
        )

    return HardeningResult(nx=nx, pie=pie, relro=relro, canary=canary)


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
