# Candidate source research

`2026-11-13-source-records.json` records public-source research against DiffSheriff
revision `f76fe091f0ff5cafd0f062005366bd647ee45b52`. The sole target proposal and
approval record is [target_scenarios.md](../../docs/target_scenarios.md).

On 2026-11-13, Python standard-library HTTP requests read four public GitHub commit
API responses and eight raw files pinned to the two proposed fix commits. Each
returned commit SHA was checked against the requested full hash, and each fix's
sole parent was checked against its proposed baseline. Selected commit metadata,
response digests, and inspected-file byte counts/digests are retained in the JSON.

This is provenance research, not a test report. No upstream source was built or
executed, no vulnerability input was run, and no instructor approval was supplied.
The upstream files and full API responses were read in memory and are not archived
here. File hashes can be checked by downloading the recorded pinned URLs and hashing
their raw bytes with SHA-256. API response hashes identify bytes observed during this
research; GitHub may change response serialization or metadata without changing a
commit, so use commit/tree/parent identities for subsequent provenance checks.

Both candidates explicitly retain `approval: pending` and `runtime_verified: false`.
The record establishes exact source references and inspected-file identities only;
it does not prove buildability, fault reachability, patch completeness, functional
expectations, or suitability for the required scenarios.
