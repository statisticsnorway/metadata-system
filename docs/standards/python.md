# Shared Python guidance

For Python work, read the target repository's local guidance first. The
maintained reference is Dapla Toolbelt Metadata; deprecated Datadoc Editor and
the generated Datadoc Model are historical comparisons, not upgrade targets.

- Use **uv** for environment and dependency management, preserving the target's
  lockfile and dependency groups.
- Use **Nox** for repeatable test, lint and type-check sessions. Resolve supported
  Python versions and session commands from the target's configuration.
- Write focused **pytest** tests using existing fixtures and mocking helpers.
- Use **Ruff** for linting and formatting with the target's rules and exclusions.
- Use **mypy** with the target's configured checks. Toolbelt explicitly uses
  non-strict checking; shared guidance does not turn on strict mode.
- Preserve **generated-code exceptions**. Toolbelt excludes its generated
  Vardef client from Ruff, coverage and relevant mypy checks. Regenerate clients
  through their source workflow rather than treating generated files as
  handwritten code or widening exceptions to application code.

Evidence: Toolbelt's
[contributor guide](https://github.com/statisticsnorway/dapla-toolbelt-metadata/blob/main/CONTRIBUTING.md),
[Nox sessions](https://github.com/statisticsnorway/dapla-toolbelt-metadata/blob/main/noxfile.py)
and [project configuration](https://github.com/statisticsnorway/dapla-toolbelt-metadata/blob/main/pyproject.toml).
Resolve these paths in the [local clone](../repositories.md) for current commands,
versions and rules; this document does not cache them.

Coverage policy needs a separate decision: the contributor guide says 100%,
while the configured report threshold is 80%. [Record the discrepancy](gaps.md)
and retain current enforcement; neither number is a new shared requirement.
No dependency, CI, framework or threshold changes follow from this guidance.
