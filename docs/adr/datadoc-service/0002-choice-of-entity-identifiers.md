# ADR0002 - Public identifier and primary key are chosen separately for each entity

* Status: accepted
* Authority: @statisticsnorway/dapla-metadata-developers
* Date: 2026-08-28

## Context and problem statement

The three persisted entities in datadoc-service identify themselves in three different ways. `Dataset` has a
Hibernate-generated `UUID`. `DataProduct` uses `productShortName`, a natural key parsed from the file path.
`DaplaDataFile` has a database-generated `Long` that is never exposed, and is addressed over HTTP by `filePath` instead.

Both natural keys come from the same place: the paths that producers post to `/data-files`. `DaplaFilePathParser`
extracts the product short name from a path segment, and data files sharing that segment belong to the same Data Product
by definition. The SSB Statistics Register is contacted only to enrich a product with a title and subject code where a
match exists; a miss returns null and nothing fails. The register is not a source of identity for this system.

## Decision drivers

* Two of the three entities have a natural identifier that is already carried in the data producers send us, is
  meaningful to users, and appears in the API today.
* `DaplaDataFile` has the potential to grow to hundreds of millions of rows, where the width of the primary key is a
  real cost in every index.
* `Dataset.id` appears in URLs, where a sequential key leaks row counts and invites enumeration.
* `DatasetIdentity` is a new concept still under active design and is expected to change shape.
* ADR-0001 commits us to `hbm2ddl.auto: update`, which adds constraints but never drops them, so any schema-level
  commitment is expensive to reverse.
* We want a rule that the next person can apply to a new entity without re-deriving the reasoning.

## Considered options

* Choose the public identifier and the primary key separately per entity, against a stated rule
* Standardise on `UUID` for every entity
* Standardise on natural keys for every entity

## Decision

Chosen option: "Choose the public identifier and the primary key separately per entity, against a stated rule", because
the three entities differ on constraints that are real — external ownership of the identifier, expected table size, and
whether the identifier is published — rather than incidental. A single type cannot satisfy all three.

The rule is:

1. **Public identifier.** Use the entity's natural token when one exists and is a single, stable value carried in the
   data we are given. This gives `DataProduct.productShortName` and `DaplaDataFile.filePath`, both parsed from the file
   path by `DaplaFilePathParser`. Otherwise generate one, as for `Dataset.id`.
2. **Primary key.** Use the public identifier as the primary key, unless it is too wide for the table's expected row
   count. In that case keep a hidden surrogate and enforce the public identifier with a unique constraint.
   `DaplaDataFile` is the only current instance of the exception.
3. **Surrogate type.** Published surrogates are `UUID`, so that they do not leak row counts or invite enumeration.
   Internal surrogates are `Long` identity, which is 8 bytes and appends monotonically, giving better index locality at
   scale.
4. **Enforcement.** A natural token that is not the primary key gets a database unique constraint, except while its
   definition is still under active design. See the open point on `DatasetIdentity` below.
5. **No wrappers.** Identifiers are raw `UUID`, `Long` and `String`. There are no value-class or typealias wrappers.

Applied to the current entities:

| Entity          | Public identifier          | Primary key             |
|-----------------|----------------------------|-------------------------|
| `DataProduct`   | `productShortName: String` | same                    |
| `Dataset`       | `id: UUID`                 | same                    |
| `DaplaDataFile` | `filePath: String`         | `id: Long`, not exposed |

No code changes follow from this ADR. Every current identifier already complies; the rule was derived from the existing
design rather than written to justify replacing it.

### Positive consequences

* A new entity can be given an identifier by answering two questions in order, without rediscovering the reasoning.
* The apparent inconsistency between the three entities is now explained rather than merely tolerated, and the
  explanation names the constraint responsible in each case.
* `DaplaDataFile` keeps an 8-byte primary key at hundreds of millions of rows while still being addressed by a
  meaningful path in the API.
* `Dataset` identifiers stay opaque in URLs.

### Negative consequences

* Rule 2's exception is a judgement call. It names no row-count threshold, because any number would be invented rather
  than measured, so applying it to a new entity requires estimating the table's eventual size.
* Both natural keys are derived from paths chosen by data producers rather than by this service. See the open point
  below.
* `productShortName` and `filePath` are both bare `String`, are both public identifiers, and are structurally
  interchangeable. `DaplaFilePathParser` derives the former from the latter, so both are in scope in the same functions
  and nothing prevents passing one where the other is expected.

## Pros and cons of the options not chosen

### Standardise on `UUID` for every entity

* Positive, because every identifier would have the same type, and the question that prompted this ADR would not recur.
* Positive, because primary keys would be uniformly narrow and uniformly opaque.
* Negative, because `productShortName` and `filePath` are how producers already name these things in the paths they send
  us, and how users refer to them. Assigning a UUID alongside them creates a second namespace for a thing that already
  has a name, and every client would need to resolve between them.
* Negative, because a random UUID primary key on a table heading for hundreds of millions of rows has poor B-tree insert
  locality and costs 16 bytes in every index that carries it, against 8 for a `Long`.

### Standardise on natural keys for every entity

* Positive, because a natural key is simpler to reason about across layers: the same token identifies the resource in
  the API, in logs and in the database.
* Positive, because it matches the two entities that already have one.
* Negative, because `Dataset`'s natural key is `DatasetIdentity`, a four-component tuple one of whose components is free
  text. As a primary key it would be four columns wide, would make every foreign key four columns wide, and would not
  fit cleanly in a URL.
* Negative, because `DatasetIdentity` is expected to change shape, and changing a primary key is the most expensive
  schema change available to us under ADR-0001.
* Negative for `DaplaDataFile` at scale, for the index-width reason above.

## Open points

* **`DatasetIdentity` has no unique constraint.** `DatasetsRepository.find` looks datasets up by the four identity
  components and `Dataset.equals` falls back to them, but nothing in the schema prevents two rows sharing an identity.
  Uniqueness is enforced in `DatasetsService` only. This is deliberate: the identity is still under design, and under
  ADR-0001 `update` would add a new unique constraint while leaving the superseded one in place, silently rejecting rows
  the new identity considers distinct. Undoing that needs hand-written DDL against each environment. Add the constraint
  once the identity stabilises.
* **We depend on producers not changing the product segment of a path.** `DataProduct.productShortName` is parsed from
  the file path, so its stability is the stability of the convention producers follow, not a guarantee any register
  offers us. There is no rename operation: if a producer moves files under a different product segment, we create a new
  `DataProduct` and the old row survives with whatever still references it. This assumption is recorded here so that it
  is met rather than rediscovered.
* **Rule 5 may not hold indefinitely.** Value-class wrappers such as `ProductShortName` would make the `String`
  confusion described above a compile error, but would require custom Micronaut Data type converters, Serde support and
  OpenAPI schema annotations, and there are currently no value classes or typealiases anywhere in `src/`. The return is
  poor for two identifiers in one service. Revisit if a third `String` identifier appears.

## Links

* Written in English
  per [ADR-0003 — Språk i teknisk dokumentasjon og kode](https://github.com/statisticsnorway/adr/blob/main/docs/0003-teknisk-dokumentasjon-spraak.md),
  following this repository's existing convention for technical documentation.
* Constrained by [ADR-0001 — Schema changes via Hibernate `hbm2ddl: update`](0001-schema-changes-via-hbm2ddl-update.md)
* Entities: `src/main/kotlin/no/ssb/metadata/datadoc/models/Dataset.kt`, `DataProduct.kt`, `DaplaDataFile.kt`,
  `DatasetIdentity.kt`
* Repositories: `src/main/kotlin/no/ssb/metadata/datadoc/repositories/`
* Natural key source: `src/main/kotlin/no/ssb/metadata/datadoc/parser/DaplaFilePathParser.kt`

<!-- markdownlint-disable-file MD013 -->


---

*Copied from [statisticsnorway/datadoc-service@ab0fc6d](https://github.com/statisticsnorway/datadoc-service/blob/ab0fc6d/docs/adr/0002-choice-of-entity-identifiers.md) on 2026-10-30 by `make collect-adrs`. The canonical version is maintained in that repository.*
