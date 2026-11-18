"""Delivered target expectations and fresh-runner source setup."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zlib

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "evaluation/target1"


def test_zlib_corpus_and_generated_validity_agree_with_reference():
    from diffsheriff.config import DiffSheriffConfig
    from diffsheriff.pipeline import discover_cases

    config = DiffSheriffConfig.from_yaml(TARGET / "correct.yaml")
    discovered, _ = discover_cases(config)
    functional_ids = {
        "regression/" + p.stem
        for p in (TARGET / "generated-regressions").glob("*.json")
        if json.loads(p.read_text())["kind"] == "functional"
    }
    enrolled = [c for c in discovered if c["id"] in functional_ids]
    assert len(enrolled) == 2
    assert all(c["valid_input"] and c["suite"] == "valid" for c in enrolled)
    expectations = json.loads((TARGET / "suites/expected.json").read_text())
    cases = []
    for key, expected in expectations.items():
        suite, name = key.split("/", 1)
        directory = "invalid" if suite == "malicious" else suite
        cases.append((TARGET / "suites" / directory / name, expected))
    for manifest in (TARGET / "generated-regressions").glob("*.json"):
        item = json.loads(manifest.read_text())
        path = manifest.parent / item["input"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
        cases.append((path, {**item["expected"], "valid_input": item["valid_input"]}))
    for path, expected in cases:
        payload = path.read_bytes()
        # An independent system implementation accepts the selected byte streams.
        assert zlib.decompress(zlib.compress(payload)) == payload
        result = subprocess.run(
            [sys.executable, str(TARGET / "reference.py")],
            input=payload,
            capture_output=True,
            check=True,
        )
        assert json.loads(result.stdout) == expected
        assert expected["valid_input"] is True


@pytest.mark.parametrize("size,code", [(0, 0), (65536, 0), (65537, 2)])
def test_zlib_reference_scope_is_explicit(size, code):
    result = subprocess.run(
        [sys.executable, str(TARGET / "reference.py")],
        input=b"x" * size,
        capture_output=True,
    )
    assert result.returncode == code
    if code:
        assert not result.stdout and b"outside the reviewed" in result.stderr
    else:
        assert json.loads(result.stdout)["valid_input"]


def preparation_script():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/validate_target.yml").read_text()
    )
    steps = workflow["jobs"]["validate"]["steps"]
    prep = next(
        i
        for i, step in enumerate(steps)
        if step.get("name") == "Prepare target sources"
    )
    validate = next(
        i for i, step in enumerate(steps) if step.get("name") == "Run patch validation"
    )
    assert prep < validate
    return steps[prep]["run"]


def copy_bundles(tmp_path):
    for target in ("target1", "target2"):
        (tmp_path / "targets" / target).mkdir(parents=True)
        (tmp_path / "evaluation" / target).mkdir(parents=True)
        shutil.copyfile(
            ROOT / "targets" / target / "source.bundle",
            tmp_path / "targets" / target / "source.bundle",
        )


@pytest.mark.skipif(sys.platform == "win32", reason="CI uses bash on Linux")
def test_workflow_prepares_all_configured_commits_without_developer_state(tmp_path):
    copy_bundles(tmp_path)
    subprocess.run(
        ["bash", "-e", "-c", preparation_script()],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    for config in (ROOT / "evaluation").glob("target*/*.yaml"):
        item = yaml.safe_load(config.read_text())["target"]
        repo = tmp_path / "evaluation" / config.parent.name / "repository"
        for ref in (item["base_ref"], item["patch_ref"]):
            result = subprocess.run(
                ["git", "-C", str(repo), "cat-file", "-t", ref],
                check=True,
                capture_output=True,
                text=True,
            )
            assert result.stdout.strip() == "commit"
    png_repo = tmp_path / "evaluation/target2/repository"
    png_base = yaml.safe_load((PNG / "correct.yaml").read_text())["target"]["base_ref"]
    sample = subprocess.check_output(
        ["git", "-C", str(png_repo), "show", png_base + ":pngtest.png"]
    )
    assert sample == (PNG / "suites/valid/valid.png").read_bytes()
    # A second invocation cannot overwrite existing source or local modifications.
    marker = tmp_path / "evaluation/target1/repository/local-work"
    marker.write_text("keep")
    result = subprocess.run(
        ["bash", "-e", "-c", preparation_script()], cwd=tmp_path, capture_output=True
    )
    assert result.returncode != 0 and marker.read_text() == "keep"
    assert b"Refusing to overwrite" in result.stderr


@pytest.mark.skipif(sys.platform == "win32", reason="CI uses bash on Linux")
def test_workflow_missing_bundle_fails_before_validation(tmp_path):
    copy_bundles(tmp_path)
    (tmp_path / "targets/target1/source.bundle").unlink()
    result = subprocess.run(
        ["bash", "-e", "-c", preparation_script()], cwd=tmp_path, capture_output=True
    )
    assert result.returncode != 0
    assert not (tmp_path / "evaluation/target1/repository").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="CI uses bash on Linux")
@pytest.mark.parametrize("second", ["ready", "missing", "occupied", "symlink"])
def test_workflow_preflights_both_bundle_destinations(tmp_path, second):
    fixture = tmp_path / "fixture"
    fixture.mkdir()

    def git(*args):
        return subprocess.check_output(
            ["git", "-C", str(fixture), *args], text=True, stderr=subprocess.PIPE
        ).strip()

    git("init", "--initial-branch=main")
    (fixture / "readme.txt").write_text("harmless bundle fixture")
    git("add", "readme.txt")
    git(
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-m",
        "Fixture",
    )
    head = git("rev-parse", "HEAD")
    for target in ("target1", "target2"):
        bundle = tmp_path / "targets" / target / "source.bundle"
        bundle.parent.mkdir(parents=True)
        if target == "target1" or second != "missing":
            git("bundle", "create", str(bundle), "--all")

    first = tmp_path / "evaluation/target1/repository"
    last = tmp_path / "evaluation/target2/repository"
    last.parent.mkdir(parents=True)
    if second == "occupied":
        last.mkdir()
        (last / "marker.txt").write_text("keep")
    elif second == "symlink":
        last.symlink_to(fixture, target_is_directory=True)

    result = subprocess.run(
        ["bash", "-e", "-c", preparation_script()], cwd=tmp_path, capture_output=True
    )
    if second == "ready":
        assert result.returncode == 0, result.stderr
        for checkout in (first, last):
            assert (
                subprocess.check_output(
                    ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
                ).strip()
                == head
            )
    else:
        assert result.returncode != 0
        assert not first.exists()
        if second == "occupied":
            assert (last / "marker.txt").read_text() == "keep"
        elif second == "symlink":
            assert last.is_symlink() and last.resolve() == fixture
            assert (last / "readme.txt").read_text() == "harmless bundle fixture"
        else:
            assert not last.exists()


PNG = ROOT / "evaluation/target2"


def test_png_fixture_expectations_are_fixed_and_unknown_inputs_have_no_oracle():
    from diffsheriff.config import DiffSheriffConfig
    from diffsheriff.pipeline import discover_cases

    cfg = DiffSheriffConfig.from_yaml(PNG / "correct.yaml")
    assert cfg.test_suites.independent_reference_command == []
    cases, _ = discover_cases(cfg)
    cases = [case for case in cases if not case["id"].startswith("regression/")]
    assert len(cases) == 4  # Review the corpus, not future generated cases.
    for case in cases:
        result = subprocess.run(
            [sys.executable, str(PNG / "reference.py")],
            input=case["payload"],
            capture_output=True,
            check=True,
        )
        assert json.loads(result.stdout) == {
            **case["expected"],
            "valid_input": case["valid_input"],
        }
        if case["id"] == "valid/valid.png":
            assert case["payload"][25] == 6  # RGBA, the selected valid fixture.
            assert case["expected"]["exit_code"] == 0
        elif case["suite"] == "malicious":
            assert case["payload"][25] == 3  # Native indexed format needs a colormap.
            assert not case["valid_input"] and case["expected"]["exit_code"] == 2
    unknown = subprocess.run(
        [sys.executable, str(PNG / "reference.py")],
        input=b"unreviewed bytes",
        capture_output=True,
    )
    assert unknown.returncode == 2 and not unknown.stdout


@pytest.mark.skipif(sys.platform == "win32", reason="uses the Linux C compiler")
@pytest.mark.parametrize("phase,expected", [(0, 2), (1, 2), (2, 0), (3, 3)])
def test_png_driver_checks_begin_finish_and_allocation_failures(
    tmp_path, phase, expected
):
    repo = tmp_path / "repo"
    subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            str(ROOT / "targets/target2/source.bundle"),
            str(repo),
        ],
        check=True,
        capture_output=True,
    )
    cfg = yaml.safe_load((PNG / "correct.yaml").read_text())["target"]
    driver = subprocess.check_output(
        ["git", "-C", str(repo), "show", cfg["patch_ref"] + ":driver/png_driver.c"]
    )
    (tmp_path / "png_driver.c").write_bytes(driver)
    (tmp_path / "png.h").write_text("""
typedef unsigned char *png_bytep;
typedef struct { unsigned version, width, height; } png_image;
#define PNG_IMAGE_VERSION 1
#define PNG_IMAGE_SIZE(image) 8
int png_image_begin_read_from_file(png_image *, const char *);
int png_image_finish_read(png_image *, void *, void *, int, void *);
void png_image_free(png_image *);
""")
    (tmp_path / "harness.c").write_text("""
#include <stdlib.h>
#include <assert.h>
#include "png.h"
static int phase, cleaned;
int png_image_begin_read_from_file(png_image *p, const char *f) {
    (void)f; p->height=1; return phase != 0;
}
int png_image_finish_read(png_image *p, void *b, void *data, int row, void *map) {
    (void)p; (void)b; (void)data; (void)row; (void)map; return phase != 1;
}
void png_image_free(png_image *p) { (void)p; ++cleaned; }
static void *allocate(size_t n) { return phase == 3 ? NULL : malloc(n); }
#define malloc allocate
#define main target_main
#include "png_driver.c"
#undef malloc
#undef main
int main(int argc, char **argv) {
    (void)argc; phase=atoi(argv[1]);
    char *args[]={"driver", "--file", "fixture"};
    int result=target_main(3,args); assert(cleaned == 1); return result;
}
""")
    # The header is included by both harness and real driver.
    header = tmp_path / "png.h"
    header.write_text(
        "#ifndef FIXTURE_PNG_H\n#define FIXTURE_PNG_H\n"
        + header.read_text()
        + "\n#endif\n"
    )
    subprocess.run(
        [
            "cc",
            "-I",
            str(tmp_path),
            str(tmp_path / "harness.c"),
            "-o",
            str(tmp_path / "program"),
        ],
        check=True,
        capture_output=True,
    )
    result = subprocess.run(
        [str(tmp_path / "program"), str(phase)], capture_output=True
    )
    assert result.returncode == expected
    assert not result.stdout and not result.stderr
