# Repository preferences

- Preserve relevant project artifacts in Git, including real and synthetic fixtures,
  reports, source archives, retained build/replay evidence, and distributable packages.
- Put durable generated evidence and packages under `artifacts/`. Do not exclude an
  artifact merely because it is generated, synthetic, or a binary.
- Exclude temporary files, dependency caches, scratch test directories, intermediate
  builds, and one-off scripts tied to temporary paths.
- Keep evidence honest: label synthetic fixtures and infrastructure smoke tests, and
  preserve the distinction between different runs and real-target acceptance.
- Prepare and stage requested changes, then provide the exact `git commit -m "..."`
  command. The user performs the commit and push unless explicitly instructed otherwise.
