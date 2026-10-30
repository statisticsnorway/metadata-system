# ADR0001 - Schema changes via Hibernate `hbm2ddl: update` until a case requires a migration framework

* Status: accepted
* Authority: @statisticsnorway/dapla-metadata-developers
* Date: 2026-08-27

## Context and problem statement

The database schema for datadoc-service is currently derived from the JPA entities and applied by Hibernate with `hbm2ddl.auto: update`; no migration framework (Flyway, Liquibase) is present. The service is `lifecycle: experimental` and pre-1.0, so entities still change often. How should we manage schema changes, and at what point should we adopt a dedicated migration framework?

## Decision drivers

* The schema is still changing frequently, and the service is marked experimental.
* Stored state is derived, not authored: every Dataset and Data Product is reconstructed from the file paths that producers post to `/data-files`, so the database can in principle be repopulated rather than migrated.
* We do not want a schema strategy that is destructive on process start, because deployed environments restart for reasons unrelated to schema changes.
* We want to avoid adding a framework and its per-change authoring overhead before there is a concrete case that requires it.

## Considered options

* Keep `hbm2ddl.auto: update`, and adopt a migration framework when a concrete case requires it
* Switch to `hbm2ddl.auto: create` in deployed environments
* Adopt Flyway or Liquibase now

## Decision

Chosen option: "Keep `hbm2ddl.auto: update`, and adopt a migration framework when a concrete case requires it", because the schema changes we make today are additive, which `update` handles, and the stored state is derived rather than authoritative, which keeps the cost of getting it wrong low. Adopting a migration framework now would be speculative.

This ADR should be revisited the first time any of the following is needed, since `update` handles none of them:

* dropping or renaming a column or table
* changing or narrowing a column type
* adding a database-level constraint to an existing column
* rolling back a schema change
* when stored state stops being reproducible from `/data-files` and becomes authoritative

### Positive consequences

* No additional dependency, toolchain or per-change authoring overhead while entities are still churning.
* Additive changes (new tables, new columns) are applied automatically on deploy.
* Existing data survives deploys, restarts and reschedules.

### Negative consequences

* `update` is silently incomplete: it never drops columns or tables, never narrows types, and never adds constraints to existing columns. It reports no error when it declines to act, so divergence between the entities and the schema accumulates unnoticed.
* A concrete instance of that divergence already exists: `Dataset.storageLocationName`, `Dataset.datasetState` and `Dataset.shortDescription` are non-null in Kotlin, but their columns remain nullable in PostgreSQL. The invariant is enforced by the application only, and anything else writing to the database can violate it.
* Tightening nullability on an existing column requires a manual check for pre-existing nulls in each environment before deploying, because Kotlin will throw on read where the schema still permits null.
* The schema is not versioned or reviewable in git; its state can only be observed by inspecting a running database.
* Rolling back a schema change requires hand-written DDL.

## Pros and cons of the options not chosen

### Switch to `hbm2ddl.auto: create` in deployed environments

Considered because it would guarantee the schema always matches the entities, removing the null-audit step described above.

* Positive, because the schema would never diverge from the entities.
* Positive, because nullability and other constraints would be applied for real, not just in Kotlin.
* Negative, because `create` recreates on every process start, not when the schema changes. These are different triggers, and only the latter is what we want.
* Negative, because `jpa.default.properties.hibernate.hbm2ddl.auto` is set in `application.yml`, which is the base configuration for every environment. `MICRONAUT_ENVIRONMENTS` layers `application-naistest.yml` or `application-naisprod.yml` on top, and neither overrides this property, so the setting would reach naisprod.
* Negative, because both NAIS deployments run `replicas: min 1, max 1`, so every deploy, restart and node reschedule would drop and recreate all tables in that environment.

### Adopt Flyway or Liquibase now

* Positive, because schema changes become versioned, reviewable in pull requests and reversible.
* Positive, because database-level constraints can be expressed and enforced.
* Positive, because we will need this eventually; the question is when, not whether.
* Negative, because no current case requires it, and each additive change would cost a hand-written migration while entities are still changing shape frequently.
* Negative, because it adds a dependency and a piece of deployment machinery to a service that does not yet need either.

## Open points

* `datasources.default.schema-generate: CREATE_DROP` is also set in `application.yml`. This is Micronaut Data's own schema generation setting and is believed not to govern schema handling when Hibernate JPA is in use, but the interaction between the two settings has not been verified. Worth clarifying so that only one mechanism is visibly in charge.

## Links

* Written in English per [ADR-0003 — Språk i teknisk dokumentasjon og kode](https://github.com/statisticsnorway/adr/blob/main/docs/0003-teknisk-dokumentasjon-spraak.md), following this repository's existing convention for technical documentation.
* Configuration: `src/main/resources/application.yml`, `src/main/resources/application-naistest.yml`, `src/main/resources/application-naisprod.yml`
* Deployment manifests: `.nais/test/nais.yaml`, `.nais/prod/nais.yaml`

<!-- markdownlint-disable-file MD013 -->


---

*Copied from [statisticsnorway/datadoc-service@ab0fc6d](https://github.com/statisticsnorway/datadoc-service/blob/ab0fc6d/docs/adr/0001-schema-changes-via-hbm2ddl-update.md) on 2026-10-30 by `make collect-adrs`. The canonical version is maintained in that repository.*
