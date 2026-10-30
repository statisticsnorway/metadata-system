# ADR0001 - MongoDB Atlas is the datastore for variable definitions

* Status: accepted
* Authority: @statisticsnorway/dapla-metadata-developers
* Date: 2026-08-31

## Context and problem statement

vardef persists variable definitions and their version history. The datastore was chosen in the spring of 2024, at the start of the project, before the domain model had stabilised; MongoDB was in place by 2024-05-07, eleven days after the repository's first commit. The reasoning was recorded at the time in a Confluence page, "Valg av datalager", which compared MongoDB against CloudSQL (PostgreSQL) accessed through JPA.

This ADR is a retroactive record. The decision it documents is real and in force, but it was never captured in this repository, and its consequences have only become visible over the two years since. The `Date` above is the date this record was written, not the date the decision was made.

Two things have changed since. First, vardef's domain model has settled, so it is now possible to say what shape the data actually is rather than what shape it might become. Second, PostgreSQL has become the de facto datastore across the rest of the organisation, including the sibling service `datadoc-service` owned by this same team, which makes vardef's choice an outlier. That second point is taken up separately in [ADR-0002 — Migrate the datastore from MongoDB Atlas to PostgreSQL](0002-migrate-to-postgresql.md); this ADR records the original decision and what living with it has cost.

## Decision drivers

The drivers as they stood in 2024:

* The domain model was still changing shape frequently, and a datastore that did not require schema changes to be declared up front was attractive.
* Kotlin `data class`es should map to stored records with as little ceremony as possible.
* Queries should be expressible as repository methods rather than hand-written query strings.
* The datastore had to be startable in tests on a developer machine and in CI without manual setup.
* Infrastructure had to be obtainable, one way or another, on the NAIS platform.

## Considered options

* MongoDB Atlas, accessed through Micronaut Data MongoDB
* PostgreSQL on NAIS CloudSQL, accessed through JPA/Hibernate
* PostgreSQL on NAIS CloudSQL, accessed through Micronaut Data JDBC

The third option was not evaluated at the time. It is included here because the recorded comparison treats the costs of JPA as though they were costs of PostgreSQL, and those are not the same thing. See "Open points" for the standing of this claim.

## Decision

Chosen option: "MongoDB Atlas, accessed through Micronaut Data MongoDB", because at the time the domain model was still churning and a document store removed schema migration from the cost of every model change, while `data class`es mapped to documents without annotations, identity plumbing or default values, and Micronaut Test Resources could start a MongoDB container for tests with no configuration.

The known cost was that MongoDB is not available on the NAIS platform, so the cluster would have to be provisioned and maintained by the team. This was accepted as a one-off setup cost.

### Positive consequences

* `SavedVariableDefinition` is an ordinary Kotlin `data class` with no persistence annotations beyond `@MappedEntity`, no no-args constructor, and no defaults introduced to satisfy the persistence layer.
* Nested value types — `LanguageStringType`, `Owner`, `Contact` — are stored in place, without a table, a join or an identifier of their own.
* Queries are derived finders on `CrudRepository`: `findByDefinitionIdOrderByPatchId`, `findDistinctDefinitionIdByVariableStatusInList`, `existsByShortName`. No query strings are written by hand.
* Micronaut Test Resources starts MongoDB for tests with no configuration beyond `mongodb.package-names`; no developer has to install or run a database.
* Adding a nullable field to the model requires no migration.

### Negative consequences

Two years of use have shown that vardef does not use MongoDB as a document store, and pays the costs of one anyway.

The data is not document-shaped:

* There are two entities in total — `SavedVariableDefinition` and `VardokVardefIdPair` — held in two separate databases, `vardef` and `vardok-id-mapping`.
* `SavedVariableDefinition` has 24 fields with a maximum nesting depth of two, reached only by `Contact.title`. There are no variable-length nested subdocument arrays and no polymorphic embedded content. `LanguageStringType` is three nullable strings.
* `unitTypes`, `subjectFields`, `classificationReference` and `relatedVariableDefinitionUris` are references to KLASS entries or to other variable definitions, held as strings. They are foreign keys without referential integrity, and nothing in the datastore prevents them dangling.
* Version history is implemented by writing a full copy of the document with an incremented `patchId`. This is versioning by row duplication, a relational pattern.

The access pattern is not document-shaped either. There is no `@Aggregation` anywhere in the codebase, and no use of `MongoCollection` or `MongoDatabase` outside the migration classes. Every read and write in application code is a derived finder or inherited CRUD, which is exactly what the same repository interfaces would look like against a relational store.

The schema is enforced strictly, so the flexibility is not being used:

* `application.yml` sets `serde.deserialization.ignore-unknown: false` and `strict-nullable: true`, so an unexpected field in a stored document is a hard failure rather than something tolerated.
* `SavedVariableDefinition` carries a class-level warning that changes to field names or data types are likely to break the application and will in most cases require a database migration.

Because the schema is enforced but undeclared, schema changes are hand-written data manipulation rather than DDL:

* Migrations are Mongock `@ChangeUnit` classes issuing `updateMany` calls directly against the driver.
* `MongockRunner` sets `setTransactional(false)`, with the comment "Mongock crashes when transactional is true". No migration runs in a transaction, so a partial failure leaves the collection half-migrated. `ContactIsMandatory` is three sequential un-transacted `updateMany` calls, and exists in that shape only because the nested subdocuments may or may not be present; the equivalent relational change is one statement.
* `MeasurementTypeUseLevelOne` cannot be rolled back. Its `@RollbackExecution` method is an empty stub with the comment "Not possible to rollback but method is necessary".
* Migrations run in-process on `StartupEvent`, not as a distinct deployment step, and are excluded from the test environment, so their code paths are exercised only by the two tests that invoke them by hand.

Transactions are not available in practice, which has a visible cost in tests. `BaseVardefTest` is annotated `@MicronautTest(transactional = false)` and achieves isolation by calling `deleteAll` on both repositories and then re-saving the full fixture set, one `save()` per document, before every single test method. Each fixture is saved with `.copy(id = null)` because `ObjectId` identity leaks into the test data. A transactional-rollback strategy would remove all of this.

The infrastructure cost was larger than "må opprettes av teamet" conveys:

* Atlas is off-platform, so egress must be enumerated by hand: three shard hostnames on two ports each, per environment, in `.nais/test/nais.yaml` and `.nais/prod/nais.yaml`. Test and prod already sit on different opaque Atlas subdomains, and the list must be updated by hand if a cluster is re-sharded or recreated.
* The connection string is supplied through manually managed secrets, `metadata-vardef-test` and `metadata-vardef-prod`.
* The cluster is defined in a separate repository, `dapla-metadata-iac`, in `infra/projects/dapla-metadata-{test,prod}/mongodb.tf`. Both files duplicate the `required_providers` block, the provider configuration and three GCP Secret Manager lookups rather than sharing a module, and the Atlas organisation API keys they read must be created and stored manually before Terraform can run at all.
* The result is a third-party managed three-node M10 replica set in `europe-north1`, reached over the public internet, serving a GCP project in the same region — where a NAIS-native PostgreSQL instance is a declarative `spec.gcp.sqlInstance` block with credentials injected by the platform.

Reviewing the original comparison against this evidence, two of the four recorded advantages do not distinguish the options. Expressing queries as repository methods is a property of Micronaut Data, not of MongoDB, and is identical with Micronaut Data JDBC. Micronaut Test Resources starts PostgreSQL containers as readily as MongoDB ones. The two that do distinguish — mapping `data class`es without ceremony, and not declaring structures up front — are real, but both are answers to JPA specifically rather than to relational storage, and the second has turned out not to be used.

## Pros and cons of the options not chosen

### PostgreSQL on NAIS CloudSQL, accessed through JPA/Hibernate

This is the option the original comparison evaluated, and the objections recorded against it are accurate for JPA.

* Positive, because the instance is provisioned declaratively by NAIS, with host, port, credentials and the Cloud SQL proxy handled by the platform and no egress rules or secrets to maintain by hand.
* Positive, because the schema is declared, so constraints, types and referential integrity are enforced by the datastore rather than by the application alone.
* Positive, because transactional test isolation removes the delete-and-reseed step from every test method.
* Positive, because it is what the rest of the organisation runs, including `datadoc-service` in this team.
* Negative, because every non-primitive type becomes its own table, so `LanguageStringType`, `Owner` and `Contact` would each need a table, an identifier and a join.
* Negative, because JPA requires a no-args constructor, which forces default values onto every field of a Kotlin `data class`.
* Negative, because relationships must be declared explicitly through annotations, adding volume to the model for no domain benefit.
* Negative, because Hibernate's own schema handling has known limits; `datadoc-service` runs with `hbm2ddl.auto: update` and its ADR0001 documents that this silently declines to drop columns, narrow types or add constraints to existing columns.

### PostgreSQL on NAIS CloudSQL, accessed through Micronaut Data JDBC

Not evaluated in 2024. It is listed here because it appears to remove most of the objections above while keeping their benefits.

* Positive, because Micronaut Data JDBC maps Kotlin `data class`es directly, without a no-args constructor, without default values introduced for the persistence layer, and without an entity graph.
* Positive, because the repository interfaces would be unchanged: the derived finders vardef already uses are Micronaut Data features, not MongoDB features.
* Positive, because PostgreSQL's `jsonb` type stores a nested value in a single column, so `LanguageStringType`, `Owner` and `Contact` need not become tables.
* Positive, because it retains the platform, schema, transaction and organisational-consistency benefits listed for the JPA option.
* Negative, because Micronaut Data JDBC does not manage schema, so a migration tool would be required from the outset — though vardef already pays for migrations by hand today.
* Negative, because a value held in `jsonb` cannot be constrained by the schema in the way an ordinary column can, so that part of the model would keep the enforcement characteristics it has now.
* Negative, because this option is asserted from documentation and has not been tried against vardef's actual model. See "Open points".

## Open points

* The claim that Micronaut Data JDBC combined with PostgreSQL `jsonb` dissolves most of the recorded objections to the relational option is reasoned from Micronaut and PostgreSQL documentation. It has not been verified against `SavedVariableDefinition`. Settling it requires mapping the entity with `data-jdbc` against a PostgreSQL Test Resources container and comparing the result; that work belongs to accepting [ADR-0002](0002-migrate-to-postgresql.md) rather than to this record.
* Whether the `vardok-id-mapping` database needs to remain separate from `vardef` is a distinct decision that has never been written down, and is not settled here.

## Links

* Written in English per [ADR-0003 — Språk i teknisk dokumentasjon og kode](https://github.com/statisticsnorway/adr/blob/main/docs/0003-teknisk-dokumentasjon-spraak.md), following this repository's existing convention for technical documentation.
* Superseded original: [Valg av datalager](https://statistics-norway.atlassian.net/wiki/x/e4A_7) — the comparison recorded at the time of the decision.
* Proposal to revisit this decision: [ADR-0002 — Migrate the datastore from MongoDB Atlas to PostgreSQL](0002-migrate-to-postgresql.md)
* Prior art in a sibling service: [datadoc-service ADR-0001 — Schema changes via Hibernate `hbm2ddl: update`](https://github.com/statisticsnorway/datadoc-service/blob/main/docs/adr/0001-schema-changes-via-hbm2ddl-update.md)
* Entities: `src/main/kotlin/no/ssb/metadata/vardef/models/SavedVariableDefinition.kt`, `src/main/kotlin/no/ssb/metadata/vardef/integrations/vardok/models/VardokVardefIdPair.kt`
* Repositories: `src/main/kotlin/no/ssb/metadata/vardef/repositories/VariableDefinitionRepository.kt`, `src/main/kotlin/no/ssb/metadata/vardef/integrations/vardok/repositories/VardokIdMappingRepository.kt`
* Migrations: `src/main/kotlin/no/ssb/metadata/vardef/migrations/`
* Configuration: `src/main/resources/application.yml`, `src/main/resources/application-naistest.yml`, `src/main/resources/application-naisprod.yml`, `src/main/resources/bootstrap.yml`
* Test setup: `src/test/kotlin/no/ssb/metadata/vardef/utils/BaseVardefTest.kt`, `build.gradle.kts`
* Deployment manifests: `.nais/test/nais.yaml`, `.nais/prod/nais.yaml`
* Cluster provisioning: `dapla-metadata-iac`, `infra/projects/dapla-metadata-test/mongodb.tf`, `infra/projects/dapla-metadata-prod/mongodb.tf`

<!-- markdownlint-disable-file MD013 -->


---

*Copied from [statisticsnorway/vardef@08898c5](https://github.com/statisticsnorway/vardef/blob/08898c5/docs/adr/0001-mongodb-atlas-as-datastore.md) on 2026-10-30 by `make collect-adrs`. The canonical version is maintained in that repository.*
