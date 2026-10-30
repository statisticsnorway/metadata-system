# ADR0003 - Adopt Flyway for schema migrations

* Status: accepted
* Authority: @statisticsnorway/dapla-metadata-developers
* Date: 2026-10-12

## Context and problem statement

Datadoc needs versioning and controlled rollout of database schema changes. Previously, Hibernate `hbm2ddl` updated the schema; this ADR supersedes the decision in ADR0001.

## Considered options

Both tools are open source, with some features available only in paid editions. They support versioned migrations, multiple databases, and recording executed migrations in their own tables. Both can be used with Micronaut.

### Flyway

* Simple to adopt, with migrations defined directly in SQL.
* File names indicate migration type, for example, versioned (`V`) and repeatable (`R`) migrations.
* Linear versioning provides a clear migration order.
* The open-source edition does not support undo migrations.

### Liquibase

* Supports multiple formats, including XML, YAML, JSON, and SQL.
* Uses a changelog to control migrations.
* Supports labels, contexts, snapshots, and rollback functionality.
* Rollback must be defined or supported by the changelog for the change in question.

## Decision

Datadoc will use Flyway to version and roll out database schema changes. Migrations will be defined as SQL files in version order. Flyway is the source of truth for schema changes; Hibernate will validate entity mappings but will not modify the schema.

Existing databases will be adopted by baselining their current schema. New databases will be created from the migration files.

## Consequences

The team already has experience with Flyway from Klass, reducing adoption cost and risk. Its simple, SQL-based model meets Datadoc’s needs without Liquibase’s additional complexity.

Since Flyway’s open-source edition does not support undo migrations, errors will be corrected with new migrations. Destructive changes must have an explicit rollback plan.

---

*Copied from [statisticsnorway/datadoc-service@ab0fc6d](https://github.com/statisticsnorway/datadoc-service/blob/ab0fc6d/docs/adr/0003-adopt-flyway-for-schema-migrations.md) on 2026-10-30 by `make collect-adrs`. The canonical version is maintained in that repository.*
