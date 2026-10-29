# 0001 — Relationships between metadata entities are typed edges

- **Status:** proposed
- **Date:** 2026-10-29
- **Supersedes:** nothing

## Context

The Metadata System is a set of services that each own a part of the metadata model.
Variable definitions live in `vardef`, classifications and codes in `klass`, variable
instances and datasets in `datadoc-service`.

Entities refer to each other, but the references are weak:

- References are carried as strings, URLs, or bare numeric ids. `vardef`'s ADR 0001
  describes them as "foreign keys without referential integrity, and nothing in the
  datastore prevents them dangling".
- The _kind_ of relationship is implied by the field name, and sometimes by nothing at
  all. `relatedVariableDefinitionUris` is a list of links to other variable definitions
  whose meaning is documented nowhere.
- Identifiers are not typed. Klass publishes `Long` ids from three different tables
  with overlapping ranges, disambiguated only by URL path segment. A stored
  `classificationReference` of `"91"` says neither which entity it is nor when it
  applied.
- There are three identifier spaces for one concept: Vardok numeric ids, vardef's
  `definitionId`, and whatever URL ended up in `definition_uri`.
- The single most important link in the system — dataset variable to variable
  definition — is an unvalidated URL that nothing resolves.

Consumers cannot answer "which classification defines this column?", maintainers
cannot answer "who uses this variable definition?", and developers cannot tell an
asserted relationship from a guessed one.

## Decision

Relationships between entities are **typed, directed edges with declared properties**,
specified in [metadata-relationships](../metadata-relationships.md).

1. A reference is a closed, structured node reference — `service`, `entity_type`,
   `key`, optional `as_of` — with a canonical URN encoding for string-only contexts.
2. A relationship is a named predicate with declared domain, range, direction,
   cardinality, requiredness, temporality, resolution rule, inverse, legal provenance,
   and status.
3. Predicates that are cardinally constrained are typed fields on the entity; open-ended
   ones live in an edge list. Only a typed field can be required.
4. Relationships have one canonical direction. Inverses are declared and derived, never
   stored.
5. Every edge carries provenance (`authored`, `inferred`, `imported`). An inferred edge
   is never authoritative.
6. Derived and transitive relationships are declared as named traversal paths, never
   stored.
7. No shadowing: each concept is owned by exactly one entity, and no entity restates a
   concept owned by another.
8. The canonical key of a node is the identifier its owning service already publishes.
   Type information in the reference removes the need to expose internal UUIDs.
9. Version pinning is by date (`as_of`), and the resolved target is never written back.

## Rejected alternatives

- **Canonical URN only, no structure.** A URN cannot express cardinality, requiredness,
  provenance, or a resolution rule, and it is still just a string.
- **A single open edge list for every relationship.** Fully graph-like, but nothing can
  enforce that a variable instance has a definition, or that a definition has a unit
  type. The guarantees are the point.
- **A central link registry as the source of truth.** Gives reverse lookups, but couples
  every service's release to one store. Reverse lookups are served by a derived index
  instead.
- **Edges stored in both directions.** Convenient, and the fastest route to
  contradictory truths.
- **Storing derived edges** (e.g. dataset → classification). Two sources of truth, and
  an invalidation problem whenever an underlying edge changes.
- **Allowing shadowing with a precedence rule** (the instance overrides the definition).
  It is flexible, but it makes "which value wins" a per-field lookup that every consumer
  must implement, and it hides the real question, which is which entity owns the concept.
- **Automatic creation of a definition for every scanned column.** It makes the
  well-formedness constraint easy and near-duplicate definitions permanent. Candidate
  search and human confirmation come first; provisional creation is the last resort.
- **Keeping `relatedVariableDefinitionUris` as a `related-to` catch-all.** It is the
  ambiguity this decision removes, and it would be used.

## Consequences

- `vardef` gains alias support, consolidation predicates, and a provisional marker.
- `datadoc-service` gains `defined-by` and `candidate-definition`, and loses the fields
  whose concepts are owned elsewhere. Which fields those are is not yet settled.
- Every service that writes a reference must resolve it at write time, and a periodic
  audit must report dangling references.
- Consumers get stable names for traversal paths instead of having to know the graph.
- The document model's `definition_uri` and vardef's `relatedVariableDefinitionUris` are
  scheduled for removal, not reinterpreted.
- klass-owned relationships are out of scope for now: the nodes remain valid targets, but
  the edges are specified later.
