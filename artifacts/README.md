# Retained project artifacts

These artifacts are deliberately versioned. Generated and synthetic evidence is
relevant project output; dependency caches and temporary work directories are not.
Git preserves artifact bytes without line-ending conversion so recorded hashes
remain meaningful across Windows and Linux checkouts.

## Native verification

- `native/native-tests.xml`: retained Linux test results, 91 tests and zero failures,
  errors, or skips. This includes the harmless native Docker smoke test.
- `native/native-validation-report.json`: the native fixture's report from that
  verification snapshot. It records 36 suite executions, functional PASS, and exit
  40 because no baseline security flaw exists in the harmless program.
- `native/cli-run/`: a separate earlier standalone CLI invocation, including its own
  `report.json`, patch diff, original source ZIPs, four built binaries/source trees,
  and input files. Its commit IDs and runtime image ID intentionally differ from
  the later verification report. Do not combine their identities or hashes.

The reports preserve the original execution paths and image IDs as provenance.
Those temporary paths need not exist on another machine, and Docker runtime images
are external dependencies. Source archives and binaries for the earlier CLI run
are retained under `native/cli-run/`; this directory is not a real vulnerability
reproducer or proof of course-target acceptance.

## Package

`package/diffsheriff-0.1.0-py3-none-any.whl` is the built Python distribution of the
implementation at commit `07914aa`. The following pulled commit changes documentation
only. The wheel includes the implementation gaps recorded in `docs/roadmap.md`.

The native fixture safely echoes input bytes. It contains no vulnerability, exploit,
or bypass. Synthetic diagnostic tests check validator logic; approved real targets
and their acceptance evidence remain outstanding.
