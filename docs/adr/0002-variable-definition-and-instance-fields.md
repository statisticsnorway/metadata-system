# 0002 — Variable definition and instance fields have separate ownership

- **Status:** proposed
- **Date:** 2026-11-02
- **Supersedes:** nothing
- **Related:** [ADR 0001 — Relationships between metadata entities are typed edges](0001-structured-relationship-model.md)

## Context and Problem Statement

The Metadata System currently spreads related metadata across variable definitions in
`vardef` and variable instances in the
datadoc model. Variable definitions and variable instances contain overlapping fields,
but the overlap does not consistently distinguish semantic meaning from the way a
dataset represents a variable.

Our Variable definitions system currently has four major issues:

1. Maintainers must complete too many fields and make decisions that can be derived
   later.
2. Global uniqueness of `short_name` forces organisation-wide coordination and slows
   definition creation.
3. Variable instances try to describe meaning, physical representation, dataset scope
   and processing concerns at the same time.
4. Users receive too little automated help to find definitions and complete metadata.

The relationship model in ADR 0001 establishes the edges between entities. This ADR
decides which _fields and concepts_ belong on a variable definition, which belong on a
variable instance, which are derived, and which are removed. It does not redefine the
relationship representation itself.

## Considered Options

- Separate semantic definition ownership from instance occurrence and representation
  facts, deriving or removing fields where appropriate.
- Allow instance overrides of definition fields.
- Keep global `short_name` uniqueness.
- Make every observed physical name an accepted alias.
- Require unit types and subject fields at definition creation.
- Keep a generic comment field.
- Keep `custom_type` as an escape hatch.

## Decision Outcome

Chosen option: "Separate semantic definition ownership from instance occurrence and
representation facts", because it reduces up-front coordination and manual entry
while keeping ownership explicit. The trade-off is greater reliance on candidate
matching, validation and later consolidation.

### Ownership test

Centralise a concept in the variable definition unless both conditions hold:

1. Two datasets can legitimately disagree about the value without either dataset being
   wrong; and
2. putting the difference on the definition would create a second definition differing
   only in that field.

When both conditions hold, the value is an instance occurrence or representation fact.
It is not an override of the definition. A mismatch is either evidence for candidate
matching or a data-quality finding.

### Variable-definition fields

The variable definition owns semantic meaning and intrinsic properties:

| concept                          | decision                                                                                                         |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| semantic `name` and `definition` | Definition-owned.                                                                                                |
| canonical `short_name`           | Definition-owned and unique within the owning team. It cannot change after publication.                          |
| aliases                          | Definition-owned structured values with status and evidence. Accepted aliases are unique within the owning team. |
| `measurement_type`               | Definition-owned broad Klass level-1 measurement type.                                                           |
| `temporality_type`               | Definition-owned temporal meaning of the variable.                                                               |
| personal-data status             | Definition-owned intrinsic property.                                                                             |
| special-category status          | Definition-owned intrinsic property. Pseudonymisation is handled elsewhere.                                      |
| classification series            | Definition-owned through `classified-by`; the series is the value domain.                                        |
| unit types and subject fields    | Not authored definition fields. They are derived projections from linked instances, datasets and products.       |
| change note                      | Attached to each validity period and explains the change represented by that period.                             |
| external definition sources      | Structured source references attached to the validity period.                                                    |

Definitions use team namespacing rather than global `short_name` uniqueness. This
reduces coordination during creation. Candidate search and later consolidation handle
the resulting risk of duplicate concepts.

### Variable-instance fields

The variable instance owns facts about one tidy variable occurrence in one dataset:

| concept                                        | decision                                                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| physical `short_name`                          | The actual top-level column, measure or attribute name.                                                      |
| `data_type` and `format`                       | Physical representation in this dataset.                                                                     |
| `measurement_unit`                             | Concrete Klass level-2 unit used by this representation.                                                     |
| `multiplication_factor`                        | Dataset-specific scaling.                                                                                    |
| classification selector                        | Version, variant, level and/or date range within the definition's classification series. Klass validates it. |
| `population_description`                       | Population covered by this occurrence. Dataset population overviews are derived from variables.              |
| `variable_role` and `data_source`              | Role and source in this dataset.                                                                             |
| `contains_data_from` and `contains_data_until` | Temporal coverage of this occurrence.                                                                        |
| `defined-by`                                   | The relationship to the semantic definition; required in the target state.                                   |

An instance must be tidy. It represents one top-level column, measure or attribute.
Data producers must flatten nested or repeated source structures before registering
variables; the target model has no `data_element_path`.

### Classification selector

The definition identifies a classification series. An instance may select any
combination supported by Klass, including:

- a version;
- a variant of a version;
- a level within a version or variant;
- a date range.

The selector must resolve within the definition's series. An unresolved selector is
invalid for publication. The exact wire representation and Klass endpoint mapping are
implementation details, but the series constraint is normative.

### Alias lifecycle

An alias is not a bare string. It records a value, status, provenance, source evidence
and timestamps. The statuses are:

- `proposed`: inferred evidence that requires review;
- `accepted`: an approved candidate signal, unique within the owning team;
- `rejected`: retained evidence that must not be used as an authoritative match.

An accepted `defined-by` link may produce a proposed alias from the instance's physical
short name. An alias match ranks candidates but never establishes `defined-by` on its
own. If alias evidence conflicts with classification, subject or other evidence, the
system returns the competing candidates and records the conflict for human review.

Canonical names are immutable after publication. If two published definitions should be
consolidated, a future merge flow will transfer relevant instance references to the
surviving definition and retain the losing definition as a redirect. The UX and exact
migration procedure are out of scope for this ADR.

### Removed fields

The target model removes these fields rather than carrying ambiguous or low-value
duplicates:

- `data_element_path`;
- special-value and invalid-value fields;
- `custom_type`;
- pseudonymisation fields, which belong to another system;
- generic instance comments;
- generic definition comments.

Definition comments migrate where possible to a validity-period `change_note` or a
structured external source reference. The original data structure is backed up, so
unmapped legacy values may be discarded from the target model.

Special and sentinel values are deferred. Klass variants are a likely future mechanism,
but this ADR does not create a special-value field or relationship before a concrete
requirement exists.

### How this assists the goals

| goal                       | assistance from this decision                                                                                                 | remaining work                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Reduce maintainer load     | Removes fields that can be derived or belong elsewhere; does not require unit types or subject fields up front.               | Make user interfaces distinguish required, suggested, derived and optional values. |
| Increase creation velocity | Team-scoped names remove organisation-wide coordination. Physical representation does not block semantic definition creation. | Candidate search before provisional creation and future merge/consolidation UX.    |
| Make instances effective   | Instances focus on occurrence, representation and dataset scope instead of duplicating semantic definition fields.            | Enforce the ownership partition in schemas and APIs.                               |
| Provide automated help     | Classification selectors, aliases, candidate evidence and derived projections create explicit automation seams.               | Implement matching, selector suggestions, alias review and derived dataset views.  |

The intended trade-off is less up-front coordination and manual entry in exchange for
better candidate matching, validation and later consolidation. This ADR enables those
workflows; it does not implement them.

### Consequences

- `vardef` must support team-scoped canonical names, structured aliases, validity-period
  change notes and structured external sources.
- `datadoc-service` must support classification selectors and remove the fields assigned
  to definitions, Klass or another system.
- Derived unit-type, subject-field and dataset-population views must expose their
  inferred nature and source evidence; they must not become authored shadow fields.
- Candidate matching becomes more important because team namespacing accepts more local
  creation and therefore more possible duplicates.
- Published canonical names remain stable, so merge/consolidation is a required future
  capability even though its UX is not defined here.
- Existing legacy values are migrated only when they have an explicit target; the
  original structure is retained as a backup rather than copied into a new catch-all.

## Pros and Cons of the Options

The chosen option's benefits and costs are described above. The other options were
rejected for the following reasons:

- **Allow instance overrides of definition fields.** Every consumer would need a
  precedence rule, and a mismatch would be hidden instead of treated as a data-quality
  signal.
- **Keep global `short_name` uniqueness.** It prevents some duplicates but makes every
  team coordinate across the organisation before publishing.
- **Make every observed physical name an accepted alias.** A bad link could permanently
  pollute a shared definition. Proposed aliases preserve evidence without making it
  authoritative.
- **Require unit types and subject fields at definition creation.** These can be derived
  from actual linked usage and should not block publication.
- **Keep a generic comment field.** It mixes change descriptions, source references and
  local notes, creating another ambiguous field.
- **Keep `custom_type` as an escape hatch.** It can recreate shadowing under arbitrary
  keys and makes the ownership model impossible to validate.
