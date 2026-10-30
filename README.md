# Metadata System

Create, publish and use metadata for datasets, instance variables, concept variables and classifications.

See [docs](https://statisticsnorway.github.io/metadata-system) for more information.

The Metadata System is composed of a collection of libraries and services:

<!-- linked-repos-start -->
* [datadoc-editor](https://github.com/statisticsnorway/datadoc-editor)
* [ssb-datadoc-model](https://github.com/statisticsnorway/ssb-datadoc-model)
* [dapla-toolbelt-metadata](https://github.com/statisticsnorway/dapla-toolbelt-metadata)
* [klass](https://github.com/statisticsnorway/klass)
* [vardef](https://github.com/statisticsnorway/vardef)
* [metadata-api-gateway](https://github.com/statisticsnorway/metadata-api-gateway)
* [dapla-metadata-iac](https://github.com/statisticsnorway/dapla-metadata-iac)
* [ssb-dataportal](https://github.com/statisticsnorway/ssb-dataportal)
* [datadoc-service](https://github.com/statisticsnorway/datadoc-service)
* [metamapper](https://github.com/statisticsnorway/metamapper)
* [metamapper-dispatcher](https://github.com/statisticsnorway/metamapper-dispatcher)
<!-- linked-repos-end -->

## Diagrams

Diagrams are generated with Archify and committed as standalone HTML, so building and
publishing the docs needs no diagram toolchain.

> Archify is an **agent skill, not a project tool**. Nothing pins its version in the repo
> — there is no `make` target or CI step for it, and diagram work is normally done
> conversationally with a coding agent that has the skill installed: you describe the model
> or the change, the agent edits the JSON and rebuilds. The committed HTML is what keeps
> that arrangement safe — the docs build never needs the CLI, and a reviewer sees the
> rendered result.

- Edit `docs/diagrams/<name>.archify.json`, never the generated HTML.
- Commit `docs/diagrams/<name>.html` alongside it; MkDocs copies it verbatim to
  `diagrams/<name>.html`.
- The page that embeds it (`docs/diagrams/index.md`) uses an iframe so the site navigation
  stays visible. A new diagram needs that page plus an entry in `mkdocs.yml`.
- `.archify/` holds scratch output and receipts and is gitignored.

Regenerate after changing the JSON:

```bash
node <archify>/bin/archify.mjs finalize architecture \
  docs/diagrams/metadata-relationships.archify.json \
  docs/diagrams/metadata-relationships.html \
  --quality showcase
```

The build is deterministic: unchanged source produces a byte-identical file, so the commit
diff only reflects real edits. Preview with `make serve-docs`;
`docs/metadata-relationships.md` §12 has the same instructions in context.

## ADRs

ADRs from the other repositories are copied into `docs/adr/<repo>/` and published
alongside this repository's own, so they can be read on the docs site without access to
those repositories. The copies are committed, which keeps the docs build free of
cross-repository access — several of the sources are internal.

Refresh them after pulling the sibling repos; `make collect-adrs` rewrites the copies,
the overview page and the generated nav block in `mkdocs.yml`:

```bash
make update-git-repos
make collect-adrs
```

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
## Shared workflows

### Grype security scan

Add this workflow to a consuming repository:

````yaml
name: Dependency scan

on:
  workflow_dispatch:
  schedule:
    - cron: "0 0 * * *"

jobs:
  grype-scan:
    uses: statisticsnorway/metadata-system/.github/workflows/dependency-scan.yaml@v1
    permissions:
      contents: read
      security-events: write
      packages: read
      actions: read
    with:
      docker-context: .
      dockerfile: Dockerfile
      image: dependency-scan-image:latest
````

The workflow builds and scans the Docker image, uploads SARIF results to GitHub Code Scanning, and stores JSON reports as workflow artifacts.

`@v1` references the version 1 tag. The consuming repository must have access to the shared workflow repository.

To release a new version:

````bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

git tag -fa v1 -m "Update v1"
git push origin v1 --force
````
For a later release, repeat the process with v1.1.0 or another version tag.
