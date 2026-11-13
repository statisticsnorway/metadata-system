# Metadata relationships

Normative reference for the relationships between metadata entities in the Metadata
System. It defines _what_ an entity is, _how_ it is identified, and _which_ named
relationships connect it to other entities.

It describes the **target state**, not the current state of any repository. Where the
two differ, there is a migration note in [section 9](#9-legacy-and-migration). The
relationship decision is recorded in [ADR 0001](adr/0001-structured-relationship-model.md)
and the field ownership decision in
[ADR 0002](adr/0002-variable-definition-and-instance-fields.md). The naming recommendation
is recorded separately in [ADR 0003](adr/0003-team-scoped-variable-definition-names.md).
These ADRs are Proposed; this reference does not verify live service behaviour.

Audience: consumers of metadata, maintainers of metadata, and developers of the
services.

[Interactive diagram of the model](diagrams/index.md)

---

## Goals

This target model is intended to make metadata production faster and more useful, not
to make every metadata record more detailed. It addresses four current problems:

1. **Maintainer load is too high.** Definitions and variable instances contain more
   fields and decisions than maintainers can consistently complete.
2. **Definition creation is too slow.** Global `short_name` uniqueness forces
   organisation-wide coordination before a team can publish a definition.
3. **Variable instances cover too many concerns.** The instance model mixes meaning,
   physical representation, dataset scope and processing details without serving any of
   them well.
4. **Users receive too little automated help.** The system has insufficient support for
   finding definitions, filling metadata, validating classification choices and showing
   derived information.

The design responds by making definitions the centre of semantic metadata, keeping
instances focused on dataset-specific facts, and making inference explicit and
reviewable. It is expected to **reduce manual work** and **enable automation**; the
relationship model alone does not implement candidate ranking, alias review, metadata
suggestions or merge workflows.

The intended trade-off is to replace up-front coordination with automated discovery and
later consolidation. Team namespacing is expected to increase definition creation
velocity; this is a hypothesis, not a measured result. Candidate evidence, aliases and
future merge support address fragmentation.

| goal                         | model response                                                                                                              | remaining implementation                                                                |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Reduce maintainer load       | Remove fields that can be derived or belong elsewhere; do not require unit types and subject fields at definition creation. | Build forms that distinguish required, suggested, derived and optional values.          |
| Increase definition velocity | Scope canonical names and accepted aliases to the owning team instead of the whole organisation.                            | Add candidate search before provisional definition creation and a future merge flow.    |
| Make instances effective     | Keep instances to physical representation, dataset scope, source and role; keep semantic meaning in definitions.            | Enforce ownership in schemas and reject reintroduced shadow fields.                     |
| Provide automated help       | Give candidate links evidence, scores and provenance; make classification selectors and derived projections explicit.       | Implement matching, alias review, Klass selector suggestions and derived dataset views. |

---

## 1. Vocabulary

One term per concept. Legacy names are listed so they can be recognised and mapped.

| term                        | meaning                                                                                                                                                                           | do not confuse with                                                                       |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **variable definition**     | The meaning of a variable, owned by `vardef`. The single source of truth for semantic name, definition text, measurement type and classification series.                          | A column in a dataset, or `SavedVariableDefinition`'s neighbours (patch, validity period) |
| **variable instance**       | A concrete variable in a dataset, owned by `datadoc-service`. Describes a column: its short name, its presence in files, and the definition it implements.                        | A variable definition; a scanned Parquet node                                             |
| **short name**              | A physical instance name, or a team-namespaced recommended canonical name on a definition.                                                                                        | An alias; a physical name is not necessarily the canonical name                           |
| **alias**                   | A structured, evidence-carrying name by which a definition may be known. Accepted aliases are unique within the owning team; proposed and rejected aliases are not authoritative. | A canonical short name; an automatic link                                                 |
| **classification**          | A classification or code list, owned by `klass`. Identified by its _series_.                                                                                                      | A classification **version**, variant, level, or a single code                            |
| **classification selector** | The instance-owned specification of the classification representation in use: version, variant, level and/or date range, constrained to the definition's series.                  | The classification series itself                                                          |
| **classification code**     | One code within a classification, scoped to the classification and to a date.                                                                                                     | The classification itself                                                                 |
| **dataset**                 | A collection of data files and the variables they contain, owned by `datadoc-service`.                                                                                            | A data file; a data product                                                               |
| **data file**               | A single physical file belonging to a dataset.                                                                                                                                    | A dataset                                                                                 |
| **provisional definition**  | A variable definition created from a scan, not authored by a human. Carries a marker so it is never mistaken for a curated definition.                                            | A draft: a draft may also be human-authored                                               |
| **candidate**               | A variable definition that _may_ describe a variable instance, suggested by inference and not yet confirmed.                                                                      | `defined-by`, which is an assertion                                                       |
| **node reference**          | A typed pointer to an entity: `service`, `entity_type`, `key`, optional `as_of`.                                                                                                  | A URL; a bare identifier                                                                  |
| **relationship (edge)**     | A named, directed connection from one node to another, with declared properties.                                                                                                  | A field holding a string that happens to be an identifier                                 |
| **predicate**               | The name of a relationship, read as a sentence from source to target.                                                                                                             | A field name                                                                              |
| **resolution**              | Fetching the target of a relationship from its owning service.                                                                                                                    | Cacheing the target's content                                                             |
| **derived projection**      | A rebuildable query result inferred from relationships and source metadata, such as a definition's observed subject fields.                                                       | An authored definition attribute                                                          |
| `as_of`                     | The date at which a versioned relationship is evaluated.                                                                                                                          | The validity period of either endpoint                                                    |

`LanguageStringType` means two different serialisations today
(`[{languageCode, languageText}]` in the document model, `{nb, nn, en}` in the Kotlin
services). See [remaining implementation questions](#10-remaining-implementation-questions).

---

## 2. The model

### 2.1 Nodes

A **node** is an entity that owns an identity and can be the target of a relationship.
Its canonical key is the identifier its owning service already publishes. The
reference's `entity_type` disambiguates numerically overlapping ids, so no service is
required to expose an internal UUID.

| entity type              | service         | key                           | notes                                                             |
| ------------------------ | --------------- | ----------------------------- | ----------------------------------------------------------------- |
| `variable-definition`    | vardef          | `definitionId` (8 characters) | A patch is a resolution result, not a node                        |
| `classification`         | klass           | series id                     | What `classificationReference` means today                        |
| `classification-code`    | klass           | `<seriesId>/<code>`           | Codes are unique within a version; `as_of` completes the identity |
| `correspondence-table`   | klass           | id                            | Out of scope for now, listed for completeness                     |
| `classification-version` | klass           | version id                    | Out of scope for now, listed for completeness                     |
| `dataset`                | datadoc-service | UUID                          |                                                                   |
| `data-product`           | datadoc-service | `productShortName`            | The container above datasets                                      |
| `variable-instance`      | datadoc-service | UUID                          |                                                                   |
| `data-file`              | datadoc-service | file path                     |                                                                   |
| `team`                   | Dapla           | team slug                     | External service                                                  |
| `group`                  | Dapla           | group name                    | External service                                                  |

**Value objects are not nodes.** `time-period`, `contact`, and `language-string` are
stored inline and have no identity of their own.

### 2.2 Node references

A reference to a node is a structured, closed object:

```
{ service, entity_type, key, as_of? }
```

It is **closed**: there are no free-form extension fields. Extension happens by adding
an `entity_type`, never by adding fields to a reference — an open reference can always
evade validation.

For contexts that accept only a string (CSV, data-platform columns, legacy fields),
the canonical encoding is:

```
urn:ssb:<service>:<entity-type>:<key>[@<as-of>]
```

### 2.3 Relationships

A relationship is `(source node, predicate, target node)` plus edge properties. Every
predicate declares:

| property        | purpose                                                                 |
| --------------- | ----------------------------------------------------------------------- |
| domain          | entity type of the source                                               |
| range           | entity type of the target                                               |
| direction       | the one canonical reading, source → target                              |
| cardinality     | `1..1`, `0..1`, `1..*`, `0..*`                                          |
| required        | whether the relationship must be present at all                         |
| `as_of`         | `required`, `recorded`, or not applicable                               |
| resolution rule | how a consumer resolves the target at `as_of`                           |
| inverse         | the name of the reverse reading — declared, never stored                |
| provenance      | which assertion kinds are legal: `authored`, `inferred`, `imported`     |
| status          | `enforced`, `unvalidated`, `new · committed`, `new · proposed`, `trial` |

### 2.4 Rules

1. **Typed field where cardinality is constrained; open edge list where it is not.**
   A required relationship must be a typed field on the entity, because only the schema
   can require it. Open-ended relationships live in an edge list.
2. **One canonical direction.** Inverses are declared in the specification and derived
   on traversal. Both directions are never stored.
3. **No shadowing.** Each concept has exactly one owning entity, and an entity never
   restates a concept owned by another. Centralise a concept in the definition unless
   two datasets can legitimately disagree about it and putting that difference on the
   definition would create a second definition differing only in that field. Such a
   difference belongs on the instance as an occurrence or representation fact. A
   mismatch is not an override: it is either evidence for candidate matching or a
   data-quality finding.
4. **Derived relationships are declared, not stored.** Transitive and composed
   relationships exist as named traversal paths (§7). Storing them would create a
   second source of truth that any underlying change invalidates.
5. **Every edge carries provenance.** An `inferred` edge is never authoritative and
   never equivalent to an `authored` one.
6. **Resolution is reproducible from the reference alone.** The resolved target (a patch
   id, a version id) is not written back. To reproduce what a published dataset said,
   snapshot the published document.
7. **Cross-service resolution happens over HTTP against the owning service.** No
   service reads another service's database.
8. **New writes are resolved at write time; existing data is audited.** A target that
   cannot be resolved is a dangling relationship and is reported, never silently kept.
9. **Legacy fields are added alongside, deprecated, and removed on a stated date.**
   They are never silently reinterpreted.

---

## 2.5 Ownership decisions

The following table is normative. “Derived” means that a service may expose or cache a
projection, but the value is not authored on the entity and is never a second source of
truth.

Naming follows the Proposed recommendation in [ADR 0003](adr/0003-team-scoped-variable-definition-names.md):
canonical names use lowercase with underscores and compare exactly; accepted aliases
compare by exact stored value. Both share one namespace per definition-owning Dapla
team. Identical names across teams produce no collision warning or publication gate.
Semantic duplicates introduce no new publication gate and remain future work.

| concept or field                                                                         | owner               | rule                                                                                                      |
| ---------------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------- |
| meaning, `definition`, semantic `name`                                                   | variable definition | One definition owns the meaning.                                                                          |
| canonical `short_name`                                                                   | variable definition | Unique within the owning team; immutable after publication.                                               |
| aliases                                                                                  | variable definition | Structured and status-bearing; accepted aliases are unique within the owning team.                        |
| `unit_types[]`, `subject_fields[]`                                                       | derived             | Inferred from linked instances, datasets and products; not mandatory authored fields.                     |
| `measurement_type`                                                                       | variable definition | Broad Klass level-1 measurement type.                                                                     |
| `temporality_type`                                                                       | variable definition | Describes the variable's temporal meaning, not this dataset's coverage.                                   |
| personal-data and special-category status                                                | variable definition | Intrinsic semantic properties. Pseudonymisation is handled elsewhere.                                     |
| classification series                                                                    | variable definition | Optional (`0..1`); `classified-by` identifies a value-domain series, not a subject-area taxonomy.           |
| classification selector                                                                  | variable instance   | Selects version, variant, level and/or date range within that series.                                     |
| physical `short_name`                                                                    | variable instance   | The actual tidy column name; mismatch with the canonical name is accepted and can produce alias evidence. |
| `data_type`, `format`                                                                    | variable instance   | Physical representation in this dataset.                                                                  |
| `measurement_unit`                                                                       | variable instance   | Concrete Klass level-2 unit used by this representation.                                                  |
| `multiplication_factor`                                                                  | variable instance   | Dataset-specific scaling.                                                                                 |
| `population_description`                                                                 | variable instance   | The population covered by this occurrence. Dataset overviews are derived from instances.                  |
| `variable_role`, `data_source`                                                           | variable instance   | Role and source in this dataset.                                                                          |
| `contains_data_from`, `contains_data_until`                                              | variable instance   | Temporal coverage of this occurrence.                                                                     |
| change note                                                                              | validity period     | One structured explanation of the change represented by the period.                                       |
| external definition sources                                                              | validity period     | A structured list of sources supporting that period.                                                      |
| `data_element_path`, special values, invalid-value descriptions, `custom_type`, comments | removed             | Not part of the target model; special-value support may be added later through Klass-driven requirements. |

This partition is intentionally not a field-by-field copy of either current service
schema. It is the target ownership model that new APIs and migration work must converge
towards.

---

## 2.6 Structured value objects

These are inline value objects, not independently identified nodes.

### Classification selector

The instance selector inherits its series from the definition's `classified-by` edge.
It may contain any combination supported by Klass:

```json
{
  "version": "2024",
  "variant": "default",
  "level": 2,
  "valid_from": "2024-01-01",
  "valid_until": "2024-12-31"
}
```

The selector must resolve within the definition's series. A selector that Klass cannot
resolve is invalid for publication. The exact wire names and endpoint mapping are an
implementation contract; the ownership and validation rule are normative.

### Alias

An alias records both a possible name and why it was proposed:

```json
{
  "value": "old_income_name",
  "status": "proposed",
  "provenance": "inferred",
  "source": {
    "service": "datadoc-service",
    "entity_type": "variable-instance",
    "key": "2f1c9a3e-4b7d-4e2a-9c11-8d0f5b6a7c31"
  },
  "created_at": "2026-11-02T10:00:00Z"
}
```

`accepted` aliases are usable candidate signals and are unique within the owning team.
`proposed` aliases may be duplicated. `rejected` aliases remain evidence and are not
used as authoritative matching signals. No alias, regardless of status, automatically
creates `defined-by`.

### Validity-period change note and sources

A validity period may carry one structured change note and a list of external sources:

```json
{
  "change_note": {
    "text": "Clarified the population definition.",
    "author": "team-slug",
    "recorded_at": "2026-11-02T10:00:00Z"
  },
  "sources": [
    {
      "uri": "https://example.test/definition",
      "title": "External definition",
      "publisher": "Example publisher",
      "retrieved_at": "2026-11-02T10:00:00Z"
    }
  ]
}
```

The change note explains the change represented by that validity period. External
definition sources are structured separately rather than placed in a generic comment.

---

## 3. vardef relationships

Domain: `variable-definition`.

| predicate       | domain → range                      | card | req | `as_of`  | status          |
| --------------- | ----------------------------------- | ---- | --- | -------- | --------------- |
| `classified-by` | definition → `classification`       | 0..1 | no  | recorded | enforced        |
| `owned-by`      | definition → `team`                 | 1..1 | yes | —        | enforced        |
| `accessible-by` | definition → `group`                | 1..* | yes | —        | enforced        |
| `same-as`       | definition → `variable-definition`  | 0..* | no  | —        | new · committed |
| `supersedes`    | definition → `variable-definition`  | 0..* | no  | —        | new · committed |
| `merged-into`   | definition → `variable-definition`  | 0..1 | no  | —        | new · committed |
| `derived-from`  | definition → `variable-definition`  | 0..* | no  | —        | new · proposed  |
| `valid-during`  | definition → `time-period` (inline) | 1..* | yes | —        | trial           |

Value-bearing fields that are **not** relationships, but which the reuse story
depends on:

- `has-alias` — structured values by which this definition may be known. Each alias has
  a value, status (`proposed`, `accepted`, or `rejected`), provenance, source evidence
  and timestamps. Accepted aliases are unique within the owning team; proposed and
  rejected aliases are not authoritative. An alias is a candidate signal, never an
  automatic `defined-by` assertion.
- `provisional` — a marker distinguishing a definition created from a scan from one
  authored by a human.

`classified-by` points at the classification _series_. Which representation is used by a
particular dataset is selected by the instance-owned classification selector. Which
codes are valid depends on that selector and is resolved through Klass.

---

## 4. datadoc-service relationships

Domains: `dataset`, `variable-instance`.

| predicate                   | domain → range                    | card     | req         | `as_of`  | status          |
| --------------------------- | --------------------------------- | -------- | ----------- | -------- | --------------- |
| `contains`                  | `dataset` → `variable-instance`   | 1..*     | yes         | —        | trial           |
| `part-of-product`           | `dataset` → `data-product`        | 1..1     | yes         | —        | trial           |
| `present-in`                | `variable-instance` → `data-file` | 0..*     | yes         | —        | trial           |
| `defined-by`                | instance → `variable-definition`  | 0..1 → 1 | target: yes | required | unvalidated     |
| `has-candidate-definitions` | instance → `variable-definition`  | 0..*     | no          | required | new · committed |

In addition to these edges, an instance may carry a structured classification selector
whose series must equal the target of its definition's `classified-by` relationship.
The selector may identify a version, variant, level and/or date range. Klass validates
the combination; an unresolved selector makes the instance invalid for publication.

`defined-by` is the headline relationship of the model: it is what makes a dataset
interpretable, and today it is an unvalidated URL spanning three unrelated identifier
spaces (Vardok numeric id, vardef `definitionId`, and whatever URL was written).

`present-in` is **reified**: the edge carries per-file attributes (physical type,
logical type, format), because a variable's physical shape is a property of its
presence in a file, not of its meaning. Data must be tidy before it enters this model:
one variable instance represents one top-level column, measure or attribute. Nested
paths and repeated structures are the data producer's responsibility to flatten.

`has-candidate-definitions` is an **inferred** edge. It carries its evidence and score, and
it is never a substitute for `defined-by`.

---

## 5. Reuse and consolidation

The default path from a scanned column to a documented variable is:

```
scanned column
  → has-candidate-definitions (0..*, inferred, ranked, with evidence)
  → defined-by          (0..1 now, 1 in the target)
```

A variable definition is only created from a scan when candidate search finds nothing
acceptable and a human chooses to create one. That definition is `provisional` until
enriched. This ordering exists to prevent a proliferation of near-duplicate
definitions; automatic creation is the last resort, not the default.

Reuse signals, in the order they are worth trying (the specification fixes the signal
set and requires evidence and score on each candidate edge; it does not fix the
ranking):

1. A confirmed `defined-by` for the same short name elsewhere in the same data product.
2. Exact canonical short-name match with explicit definition-owner team context.
3. Accepted-alias match (`has-alias`) by exact stored value within that context,
   requiring human confirmation before storing the definition ID.
4. Vardok id mapping, for migrated data only.
5. Attribute agreement — measurement type/unit, classification, subject and source.
6. Text similarity on name and definition. Always `inferred`, never auto-confirming.

Under [ADR 0003](adr/0003-team-scoped-variable-definition-names.md), canonical-name
lookup requires `(definition owner team, canonical short_name)`. Do not infer this
context from the instance's team: cross-team references are allowed. The resulting
stable `definitionId`, not the lookup pair or alias, is stored as the actual
`defined-by` reference key.

Duplicates are reversible by design. `same-as` asserts that two definitions describe
the same variable; `supersedes` records that one replaced another; `merged-into` marks
a definition that survives only as a redirect. Merging rewrites all edges that point at
the loser to point at the winner. `same-as` is the only symmetric, transitive predicate
in the model.

---

## 6. Resolution rules

| owning service  | resolution                                                   |
| --------------- | ------------------------------------------------------------ |
| vardef          | `GET /variable-definitions/{definitionId}?date_of_validity=` |
| klass           | `GET /classifications/{seriesId}/codesAt?date=` for codes    |
| datadoc-service | lookup by UUID, or by the relationship's own foreign key     |

A resolved target is never persisted on the edge (§2.4 rule 6). Where a published
document must be reproducible, the document is snapshotted at publication.

---

## 7. Derived traversal paths

Declared so consumers have a stable name to ask for; composed at read time; never
stored.

| path                                    | definition                                           | answers                                                 |
| --------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------- |
| `effective-classification-of(instance)` | `defined-by → classified-by`                         | Which classification defines this column's values?      |
| `effective-unit-type-of(instance)`      | derived from linked instances, datasets and products | What unit types have been observed for this definition? |
| `dataset-classifications(dataset)`      | `contains → defined-by → classified-by`              | What does each variable in this dataset mean?           |
| `definitions-in-use(data-product)`      | `part-of-product → contains → defined-by`            | Which definitions does this product depend on?          |
| `code-at(classification, code, date)`   | resolution at `as_of`                                | Was this code valid then?                               |
| `duplicate-cluster(definition)`         | transitive `same-as`                                 | Which definitions are one variable?                     |
| `documentation-coverage(dataset)`       | share of instances with an `authored` `defined-by`   | How much of this dataset is documented?                 |

---

## 8. Out of scope

The following are deliberately excluded from this version of the model. The model may
be expanded to cover them later if needed.

- **Relationships internal to klass.** The model makes sense for classifications and
  their codes, and the nodes remain valid targets, but the changes cannot be
  implemented now. This covers the family/series/version/item hierarchy, parent codes,
  correspondence tables, and version succession.
- **Special values and sentinel values.** Variants in Klass should be used to specify these, not in-lining on a variable instance.
- **Legacy ssb-datadoc-model extension fields.** `custom_type`, pseudonymisation,
  special-value fields, invalid-value descriptions, and instance comments are removed
  from the target model. The original data structure is backed up for migration review;
  unmapped values are not copied into a new legacy namespace.

Also out of scope: pseudonymization keys as nodes, and all free-URL fields such as
vardef's `externalReferenceUri`.

---

## 9. Legacy and migration

### 9.1 Identifier reconciliation

Three identifier spaces describe the same concept today. Only `definitionId` survives
as identity; the other two become aliases.

| legacy                                | target                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| Vardok numeric id (`vardok/26`)       | alias of a `variable-definition`; mapping lives in vardef's `vardok-id-mapping` |
| vardef `definitionId`                 | the canonical key                                                               |
| `definition_uri` (often a Vardok URL) | `defined-by` with `entity_type: variable-definition`                            |

Vardok is **not** a first-class entity type in the target model. Giving it one would
allow new metadata to be authored against a system being retired.

### 9.2 Field migration

| field                                               | service        | becomes                                                      | removal                                  |
| --------------------------------------------------- | -------------- | ------------------------------------------------------------ | ---------------------------------------- |
| `definition_uri`                                    | document model | `defined-by`                                                 | on migration of all documents            |
| `classification_uri`                                | document model | definition series plus instance classification selector      | target migration                         |
| `unit_type`                                         | document model | instance `measurement_unit` or derived measurement metadata  | target migration                         |
| `data_element_path`                                 | document model | removed; data must be tidy before registration               | target migration                         |
| `special_value`, invalid-value fields               | document model | removed; future Klass-driven support is deferred             | target migration                         |
| `custom_type`, pseudonymisation, instance `comment` | document model | removed; handled elsewhere or discarded                      | target migration                         |
| `comment`                                           | vardef         | validity-period `change_note` or structured source reference | target migration                         |
| `relatedVariableDefinitionUris`                     | vardef         | retired; authors choose `derived-from` or `same-as`          | on release of the replacement predicates |

`relatedVariableDefinitionUris` is removed rather than kept as a catch-all. A vague
predicate is the problem this model exists to remove, and a hole shaped like the old
ambiguity will be used exactly as the old ambiguity was.

---

## 10. Remaining implementation questions

Recorded so they are not silently assumed:

1. **Which date means what.** `as_of` is a date, but whether a relationship should be
   pinned to the period the data is applicable for, or to the dataset's
   publication/change date, is not decided. The model is unaffected; the resolution
   rule per edge is.
2. **`defined-by` requirement.** Modelled as `0..1` now and `1` in the target. The
   target cannot be reached until the scan pipeline produces definitions or an
   acceptable alternative exists.
3. **`same-as` clusters with conflicting attributes.** One rule must be chosen:
   attributes must agree before a cluster forms, a cluster has a designated
   canonical definition, or attributes are unioned.
4. **Merge UX.** Canonical names cannot change after publication. A future merge flow
   must transfer relevant instance references to a surviving definition and preserve
   the losing definition as a redirect. The exact user experience is intentionally out
   of scope here. Definition ownership transfer and team slug changes are separate,
   unresolved namespace-lifecycle follow-up in [ADR 0003](adr/0003-team-scoped-variable-definition-names.md).
5. **Classification selector wire shape.** The semantic shape is settled, but the
   service contract must choose exact names and validation errors for version, variant,
   level and date-range selectors.
6. **`LanguageStringType`.** Two incompatible serialisations coexist. The relationship
   model does not depend on which wins, but a cross-service reference model cannot
   avoid hitting it.

---

## 11. Implementation examples

An example payload for each predicate. These are illustrations of shape, not a wire
format: field names, envelope and transport are decided by each service. Every payload
follows the same structure — the predicate, a closed node reference, provenance, and
only the properties that predicate declares.

`part-of-product`:

```json
{
  "predicate": "part-of-product",
  "target": {
    "service": "datadoc-service",
    "entity_type": "data-product",
    "key": "folkemengde"
  },
  "provenance": "authored"
}
```

`contains`:

```json
{
  "predicate": "contains",
  "target": {
    "service": "datadoc-service",
    "entity_type": "variable-instance",
    "key": "2f1c9a3e-4b7d-4e2a-9c11-8d0f5b6a7c31"
  },
  "provenance": "authored"
}
```

`present-in` — reified, so it carries the per-file attributes:

```json
{
  "predicate": "present-in",
  "target": {
    "service": "datadoc-service",
    "entity_type": "data-file",
    "key": "gs://bucket/path/fagfelt.parquet"
  },
  "attributes": { "physical_type_name": "INT64", "logical_type_name": "int64" },
  "provenance": "inferred"
}
```

`defined-by`:

```json
{
  "predicate": "defined-by",
  "target": {
    "service": "vardef",
    "entity_type": "variable-definition",
    "key": "a1b2c3d4",
    "as_of": "2026-10-29"
  },
  "provenance": "authored"
}
```

`has-candidate-definitions` — inferred, with its evidence:

```json
{
  "predicate": "has-candidate-definitions",
  "target": {
    "service": "vardef",
    "entity_type": "variable-definition",
    "key": "a1b2c3d4",
    "as_of": "2026-10-29"
  },
  "provenance": "inferred",
  "evidence": { "signal": "short-name-exact", "score": 0.94 }
}
```

`owned-by` and `accessible-by`:

```json
{ "predicate": "owned-by", "target": { "service": "dapla", "entity_type": "team", "key": "fagteam-befolkning" }, "provenance": "authored" }
{ "predicate": "accessible-by", "target": { "service": "dapla", "entity_type": "group", "key": "fagteam-befolkning-developers" }, "provenance": "authored" }
```

`classified-by` — the series, with the date at which codes are resolved:

```json
{
  "predicate": "classified-by",
  "target": {
    "service": "klass",
    "entity_type": "classification",
    "key": "91",
    "as_of": "2026-10-29"
  },
  "provenance": "authored"
}
```

An instance classification selector is constrained to that series:

```json
{
  "classification_selector": {
    "series": "91",
    "version": "2024",
    "variant": "default",
    "level": 2,
    "valid_from": "2024-01-01",
    "valid_until": "2024-12-31"
  },
  "provenance": "authored"
}
```

An alias is structured evidence, not an automatic definition link:

```json
{
  "value": "old_income_name",
  "status": "proposed",
  "provenance": "inferred",
  "source": {
    "service": "datadoc-service",
    "entity_type": "variable-instance",
    "key": "2f1c9a3e-4b7d-4e2a-9c11-8d0f5b6a7c31"
  }
}
```

---

## 12. Regenerating the diagram

`diagrams/metadata-relationships.html` is generated from
`diagrams/metadata-relationships.archify.json` with Archify 3.2.0:

```bash
node <archify>/bin/archify.mjs finalize architecture \
  docs/diagrams/metadata-relationships.archify.json \
  docs/diagrams/metadata-relationships.html \
  --quality showcase
```

The built HTML is committed so that publishing does not depend on the CLI, which is a
local tool rather than a project dependency. MkDocs copies it verbatim during
`mkdocs build`, so it is served at `diagrams/metadata-relationships.html`. Change
the JSON, not the HTML.
