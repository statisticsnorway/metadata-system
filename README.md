# Metadata System

Create, publish and use metadata for datasets, instance variables, concept variables and classifications.

See [docs](https://statisticsnorway.github.io/metadata-system) for more information.

## Shared development guidance

This is the Home Repo for shared Metadata development guidance. Agents start
with the root `AGENTS.md`; humans can use the
[repository and lifecycle catalogue](docs/repositories.md),
shared [Kotlin](docs/standards/kotlin.md), [Python](docs/standards/python.md) and
[TypeScript](docs/standards/typescript.md) guidance,
[documented standards gaps](docs/standards/gaps.md) and [optional skills](docs/skills.md).
Repository-specific architecture and domain decisions remain local.
Deprecated repositories are historical references, not consolidation targets.

Standalone clones use the [local-first Home pointer contract](docs/repositories.md#shared-guidance-resolution);
an unpushed Home branch must be activated locally before dependent work.

## Development

Run `make install` to configure your local development environment.

All available make targets:

<!-- make-help-start -->

```
install                        Install the dev environment (tools, pre-commit hooks and git repos)
install-tools                  Install the dev tools with uv
update-readme                  Update the README.md file
collect-adrs                   Copy the ADRs of the sibling repos into docs/adr/ and refresh their nav
doctor                         Ensure that local tools and environment settings are configured correctly
update-git-repos               Pull all related git repos
serve-docs                     Serve docs locally
```

<!-- make-help-end -->
