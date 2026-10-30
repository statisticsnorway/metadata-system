# ADR0002 - Migrate the datastore from MongoDB Atlas to PostgreSQL

* Status: proposed
* Authority: @statisticsnorway/dapla-metadata-developers
* Date: 2026-08-31

## Context and problem statement

vardef stores variable definitions in MongoDB Atlas. That decision, and the evidence accumulated since, is recorded in [ADR-0001 — MongoDB Atlas is the datastore for variable definitions](0001-mongodb-atlas-as-datastore.md).

The short version: vardef does not use MongoDB as a document store. It stores two fixed-schema entities with a maximum nesting depth of two, reads them exclusively through derived finders with no aggregation pipelines anywhere, models relationships as strings without referential integrity, and versions records by writing full duplicates. It enforces its schema strictly in the application layer while declaring none in the datastore, and consequently hand-writes migrations as `updateMany` calls — non-transactional, because Mongock crashes otherwise, and in one case irreversible. It has no transactions, so tests achieve isolation by deleting and reseeding the database before every test method. Its cluster sits off the NAIS platform, requiring hand-maintained egress rules, manually managed secrets, and a separate Terraform stack whose Atlas API keys must be seeded by hand.

Separately, PostgreSQL has become the de facto datastore across the organisation. vardef is an outlier, including within its own team: `datadoc-service`, same owners, runs PostgreSQL. This has not been made explicit as an organisational standard, and no mandate exists.

Should vardef migrate?

## Decision drivers

Listed strongest first. The organisational driver is the one that prompted this ADR, but it is the weakest of the set and is deliberately not the headline.

* **Schema management is being paid for twice.** The application enforces a schema it cannot declare, so every change to `SavedVariableDefinition` requires a hand-written data migration where a declared schema would require DDL. `SavedVariableDefinition` carries a warning to this effect in its own KDoc.
* **Migrations are not safe.** `MongockRunner` runs with `setTransactional(false)`, so any migration that fails partway leaves the collection in a mixed state. One existing migration cannot be rolled back at all.
* **Test isolation is expensive and structurally so.** Without transactions, `BaseVardefTest` deletes and re-saves the entire fixture set before every test method. This is not a test-code problem that can be fixed in test code.
* **Infrastructure is hand-maintained where it could be declarative.** Six egress entries across two environments, manually managed secrets, and a duplicated Terraform stack with pre-seeded Atlas API keys — versus a `spec.gcp.sqlInstance` block with platform-injected credentials.
* **Referential integrity is unenforceable.** References to KLASS entries and to other variable definitions are strings; nothing prevents them dangling.
* **Being the only team on MongoDB is a standing risk.** There is no organisational mandate, and this has not yet caused a concrete problem. It is a risk rather than a driver: it affects platform support, on-call familiarity, review depth and the ease of moving people between services, and it is the kind of divergence that is cheapest to correct before it is forced.

## Considered options

* Migrate to PostgreSQL
* Remain on MongoDB Atlas
* Remain on MongoDB, but start using it as a document store

## Decision

Chosen option: "Migrate to PostgreSQL", because every property vardef relies on from its datastore is one PostgreSQL provides, and every property MongoDB provides in exchange — schemaless storage, nested document trees, aggregation pipelines — is one vardef demonstrably does not use, while the costs of that exchange are being paid in full and are enumerable today.

This ADR settles only *whether*, not *how*. The access layer, the schema management tool and the cutover approach are each further decisions with real alternatives; they are recorded under "Open points" and should be settled in their own ADRs.

This ADR is `proposed`. No conditions are attached under which it should be accepted, because none are known: no organisational standard is pending, no Atlas contract or cost event is anticipated, and nothing currently forces the question. It should be accepted or rejected by discussion within the team. If accepted, it supersedes [ADR-0001](0001-mongodb-atlas-as-datastore.md).

### Positive consequences

* Schema changes become declared DDL, reviewable in pull requests and applied by a migration tool, rather than hand-written `updateMany` calls.
* Migrations become transactional, so a failed migration leaves no partial state.
* Test isolation can use transactional rollback, removing the delete-and-reseed cycle from every test method.
* The database becomes a declarative block in the NAIS manifest, deleting six egress rules, two manually managed secrets and two Terraform files with their hand-seeded Atlas API keys.
* Foreign keys to other variable definitions become enforceable by the datastore.
* vardef stops being the only service in the organisation on MongoDB, and shares a datastore with `datadoc-service` in the same team.

### Negative consequences

* This is a live service with production data. Migration requires a data transfer, a verification step and a cutover, none of which are free, and all of which carry risk that the current arrangement does not.
* The effort is unbudgeted and nothing is currently forcing it, so it competes directly with feature work.
* Nested value types — `LanguageStringType`, `Owner`, `Contact` — must be re-homed, either as columns, as tables, or as `jsonb`. Whichever is chosen, the mapping code changes.
* If the access layer chosen is JPA/Hibernate, the objections recorded in ADR-0001 apply in full: entity annotations, explicit relationships, and default values forced onto `data class` fields by the no-args constructor requirement.
* A schema management tool must be adopted, adding a dependency and per-change authoring cost that MongoDB did not require in the same form.
* `SavedVariableDefinition`'s version-by-duplication model produces one row per patch. This is unremarkable relationally, but the volume and index strategy have not been examined.
* Two separate databases, `vardef` and `vardok-id-mapping`, must either be preserved as two instances or consolidated. Consolidation is probably right but has not been decided.

## Pros and cons of the options not chosen

### Remain on MongoDB Atlas

* Positive, because it costs nothing and risks nothing today. The service works.
* Positive, because the team knows the current setup, and the infrastructure, however hand-maintained, is already built and running.
* Positive, because no organisational standard requires the change, so there is no deadline and no external pressure.
* Negative, because every cost enumerated in the drivers above is recurring, not one-off: each new field is another hand-written migration, each test run pays the reseed, each Atlas re-shard means editing egress rules by hand.
* Negative, because the costs of migrating grow with the data and with the number of services depending on the API.
* Negative, because the divergence risk compounds quietly, and the moment it becomes acute is the worst moment to start a migration.

### Remain on MongoDB, but start using it as a document store

Considered because the honest reading of ADR-0001 is not that MongoDB is a bad datastore, but that vardef uses it as a relational one. Using it as intended is the other way to resolve that mismatch.

* Positive, because it would make the current choice coherent, and would avoid a migration entirely.
* Negative, because there is nothing in the domain to model as a document. The data is two flat entities with a maximum nesting depth of two; there is no tree, no polymorphism and no variable-length nested collection to exploit.
* Negative, because it would mean deliberately loosening `serde.deserialization.ignore-unknown: false` and `strict-nullable: true`, giving up schema enforcement that the API contract currently depends on.
* Negative, because it would not address the transaction, test isolation, infrastructure or organisational-consistency drivers at all. Those are properties of the deployment and the engine, not of how the data is modelled.

## Open points

Each of the following is a further decision that this ADR deliberately does not settle, and each should get its own ADR if this one is accepted.

* **Access layer: Micronaut Data JDBC or JPA/Hibernate.** This matters more than it appears. Every objection to PostgreSQL recorded in the original 2024 comparison — tables for non-primitive types, no-args constructors, default values, annotation weight — is an objection to JPA specifically, and Micronaut Data JDBC appears to avoid all of them while leaving vardef's existing repository interfaces unchanged. That claim is reasoned from documentation and has not been verified; settling it means mapping `SavedVariableDefinition` with `data-jdbc` against a PostgreSQL Test Resources container and comparing the result. `datadoc-service` uses JPA, so consistency pulls the other way, and that tension needs resolving rather than assuming.
* **Nested value types: columns, tables or `jsonb`.** Follows from the access layer decision but is separable from it.
* **Schema management: Flyway, Liquibase, or Hibernate's `hbm2ddl`.** Note that `datadoc-service` ADR-0001 documents `hbm2ddl.auto: update` silently declining to drop columns, narrow types or add constraints to existing columns — which is precisely the class of change a migration from an unconstrained document model would require. That precedent argues against reusing it here.
* **Whether `vardok-id-mapping` is consolidated into the main database.** ADR-0001 notes that the separation has never been justified in writing.
* **Cutover approach.** Dual-write, read-only window, or replay from source. vardok-derived records are reconstructible from the source system; user-authored variable definitions are not, and the two may warrant different treatment.

## Links

* Written in English per [ADR-0003 — Språk i teknisk dokumentasjon og kode](https://github.com/statisticsnorway/adr/blob/main/docs/0003-teknisk-dokumentasjon-spraak.md), following this repository's existing convention for technical documentation.
* Decision this would supersede: [ADR-0001 — MongoDB Atlas is the datastore for variable definitions](0001-mongodb-atlas-as-datastore.md)
* Original comparison: [Valg av datalager](https://statistics-norway.atlassian.net/wiki/x/e4A_7)
* Prior art in a sibling service: [datadoc-service ADR-0001 — Schema changes via Hibernate `hbm2ddl: update`](https://github.com/statisticsnorway/datadoc-service/blob/main/docs/adr/0001-schema-changes-via-hbm2ddl-update.md), [datadoc-service ADR-0002 — Choice of entity identifiers](https://github.com/statisticsnorway/datadoc-service/blob/main/docs/adr/0002-choice-of-entity-identifiers.md)
* Entities: `src/main/kotlin/no/ssb/metadata/vardef/models/SavedVariableDefinition.kt`, `src/main/kotlin/no/ssb/metadata/vardef/integrations/vardok/models/VardokVardefIdPair.kt`
* Repositories: `src/main/kotlin/no/ssb/metadata/vardef/repositories/VariableDefinitionRepository.kt`, `src/main/kotlin/no/ssb/metadata/vardef/integrations/vardok/repositories/VardokIdMappingRepository.kt`
* Migrations: `src/main/kotlin/no/ssb/metadata/vardef/migrations/`
* Test setup: `src/test/kotlin/no/ssb/metadata/vardef/utils/BaseVardefTest.kt`, `build.gradle.kts`
* Deployment manifests: `.nais/test/nais.yaml`, `.nais/prod/nais.yaml`
* Cluster provisioning: `dapla-metadata-iac`, `infra/projects/dapla-metadata-test/mongodb.tf`, `infra/projects/dapla-metadata-prod/mongodb.tf`

<!-- markdownlint-disable-file MD013 -->


---

*Copied from [statisticsnorway/vardef@08898c5](https://github.com/statisticsnorway/vardef/blob/08898c5/docs/adr/0002-migrate-to-postgresql.md) on 2026-10-30 by `make collect-adrs`. The canonical version is maintained in that repository.*
