# Metadata system

This is the Home Repo for shared Metadata development guidance and repository pointers.
Start work in the target repository by reading its AGENTS.md and linked local guidance.
Repository-specific architecture, commands and domain decisions stay with that repository.

## Shared guidance

- Kotlin work: read [Kotlin standards](docs/standards/kotlin.md).
- Python work: read [Python standards](docs/standards/python.md).
- TypeScript work: read [TypeScript standards](docs/standards/typescript.md).
- ADR authoring or review: read the [canonical MADR format](docs/adr-format.md).
  Child ADRs remain authoritative in their source repositories; Home copies are snapshots.
- Standards planning: read [documented gaps](docs/standards/gaps.md).
  These are observations, not authorization for framework, dependency, CI or threshold migrations.
- Repository selection or lifecycle questions: read the [catalogue](docs/repositories.md).
  Deprecated repositories are historical references only.
- Optional agent capabilities: read the [skills catalogue](docs/skills.md).

Shared tooling recommendations cover Kotlin, Python and TypeScript only.
Retain local legacy Java guidance and existing organizational Terraform rules.
Local repository rules and domain decisions remain in force; resolve conflicts explicitly.

## Other Repos

Paths below identify separate clones, not children of this checkout. Read each
repository's local guidance before changing it. See the catalogue for the
[local-first Home pointer contract](docs/repositories.md#shared-guidance-resolution).

| Repository (role, status) | Local path | Missing clone | Local guidance |
| --- | --- | --- | --- |
| datadoc-editor (Python dataset-documentation application, deprecated) | `/Users/mmw/code/metadata-system/datadoc-editor` | Clone from https://github.com/statisticsnorway/datadoc-editor.git if missing | Historical `CONTRIBUTING.md` workflow; reference only. |
| ssb-datadoc-model (JSON Schema and generated Java/Python models, deprecated) | `/Users/mmw/code/metadata-system/ssb-datadoc-model` | Clone from https://github.com/statisticsnorway/ssb-datadoc-model.git if missing | Historical `README.md`: source versus generated artifacts; reference only. |
| dapla-toolbelt-metadata (Python clients and tools, stable) | `/Users/mmw/code/metadata-system/dapla-toolbelt-metadata` | Clone from https://github.com/statisticsnorway/dapla-toolbelt-metadata.git if missing | `AGENTS.md` and `CONTRIBUTING.md`. |
| klass (legacy Java classifications and code lists, stable) | `/Users/mmw/code/metadata-system/klass` | Clone from https://github.com/statisticsnorway/klass.git if missing | `AGENTS.md`; module-specific JDKs stay local. |
| vardef (Kotlin variable definitions, stable) | `/Users/mmw/code/metadata-system/vardef` | Clone from https://github.com/statisticsnorway/vardef.git if missing | `AGENTS.md`, `CONTRIBUTING.md` and datastore ADRs. |
| metadata-api-gateway (Kotlin API gateway, deprecated) | `/Users/mmw/code/metadata-system/metadata-api-gateway` | Clone from https://github.com/statisticsnorway/metadata-api-gateway.git if missing | Historical local guidance; reference only. |
| dapla-metadata-iac (Terraform infrastructure, stable) | `/Users/mmw/code/metadata-system/dapla-metadata-iac` | Clone from https://github.com/statisticsnorway/dapla-metadata-iac.git if missing | `AGENTS.md` and `README.md`; retain org rules and generated-configuration boundaries. |
| ssb-dataportal (TypeScript metadata portal, active) | `/Users/mmw/code/metadata-system/ssb-dataportal` | Clone from https://github.com/statisticsnorway/ssb-dataportal.git if missing | `AGENTS.md`; preserve localhost-only browser access. |
| datadoc-service (Kotlin dataset metadata, active) | `/Users/mmw/code/metadata-system/datadoc-service` | Clone from https://github.com/statisticsnorway/datadoc-service.git if missing | `AGENTS.md`; migrations and dataset identity stay local. |
| metamapper (Kotlin metadata extraction and access grants, active) | `/Users/mmw/code/metadata-system/metamapper` | Clone from https://github.com/statisticsnorway/metamapper.git if missing | `AGENTS.md` and grant-model ADR. |
| metamapper-dispatcher (Kotlin queue and task coordination, active) | `/Users/mmw/code/metadata-system/metamapper-dispatcher` | Clone from https://github.com/statisticsnorway/metamapper-dispatcher.git if missing | `AGENTS.md`; queue architecture stays local. |
