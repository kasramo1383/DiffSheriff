# Correlation uncertainty and exit-priority verification

This checkpoint addresses generic-tool F08 and F11 on parent revision `d4ec949`.
Selected-target stacks, matrices, independent functional references and final delivery
remain separate acceptance work in [the roadmap](../../../docs/roadmap.md).

## Reproduced defect and correction

Function-level attribution previously chose one of several matching edited hunks by
stack-frame order and then line distance. Those properties cannot establish which edit
is relevant. Two correlator cases reproduced that arbitrary selection; a pipeline case
showed it allowing PASS despite ambiguous attribution. `red.xml` retains all three
failures and the successful tests from that pre-fix run.

The fallback now requires a single matching edited hunk. Multiple matches yield
Inconclusive with an explicit ambiguity reason and no selected hunk. Actual edited-line
runtime intersections retain precedence. A single function relation is labelled as
such, never as proof of branch execution or causation. Missing declaration/path evidence,
changing replay evidence and unsatisfied independent behavior cannot establish Fixed.

## Exit priorities

The new CLI tests exercise all 16 combinations of operational failure, confirmed
security finding, functional regression and incomplete analysis. Late operational
failures occur after earlier observations so the tests also check preservation of
already collected findings. CLI exit, console, exported report and retained run report
must agree. Security and functional failures remain independent of the selected code.
Existing priority logic passed these checks and needed no production change.

## Verification and scope

- `focused.xml`: correlator, pipeline and reporter checks after the correction.
- `full-linux.xml`: complete suite, including the harmless native Docker matrix.
- `build-failed.log`: the normal image build was blocked by Docker Hub HTTP 403
  while fetching Ubuntu metadata. `lint-failed.log` retains an initial verification
  stop on three overlong test strings; the strings were split and lint passed.
- `verify-linux.log`: successful `bash verify.sh` using the existing recorded runtime
  as execution environment, with the current staged validator running on the host.
- `verification.json`: actual counts, commands, image identity and wheel install check.
- `source-sha256.json`: normalized hashes of all tested Python source/test files,
  matched against a snapshot of the staged files in Linux temporary storage.
- `package/`: wheel from that full verification, imported and invoked outside source.
- `artifact-sha256.json`: retained artifact byte hashes, excluding itself.

The temporary snapshot has no ignored developer state. It verifies the generic tool;
it does not satisfy F12's selected-target clean-room validation. Synthetic sanitizer
observations in pipeline fixtures establish logic behavior, not native vulnerabilities.
The native fixture remains harmless and returns Inconclusive because it has no baseline
security defect. No selected-target acceptance, hosted CI, approval or defense is claimed.

To reproduce with the declared development dependencies from the project root:

```sh
python3 -m pytest -q tests/test_correlator.py tests/test_pipeline.py tests/test_reporter.py
docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
bash verify.sh
```
