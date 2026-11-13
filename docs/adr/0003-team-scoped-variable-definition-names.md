# 0003 - Variable definition names are unique within the owning team

- **Status:** proposed
- **Date:** 2026-11-13
- **Authority:** @statisticsnorway/dapla-metadata-developers
- **Related:** [ADR 0001 - Typed relationships](0001-structured-relationship-model.md), [ADR 0002 - Definition and instance field ownership](0002-variable-definition-and-instance-fields.md)

## Context and Problem Statement

Statisticians at Statistics Norway manually produce variable definitions. Production is slow, and the reported organisation-wide uniqueness requirement for `short_name` makes authors hesitant to publish: choosing a name may take a name already used elsewhere. This creates a coordination burden even when teams describe different concepts.

Global uniqueness has a real benefit: a short name alone can identify one definition, making the connection from a variable instance to a definition appear simple. However, a unique name does not prove that the definition describes the instance's meaning, and different names can still describe the same concept.

This ADR separates a human-facing lookup name from the stable identity used in a relationship. It recommends a naming policy for the target model; it does not claim that the live services implement it or that their current behaviour has been verified.

## Decision Drivers

- Reduce the fear of taking another team's name and the coordination needed to publish.
- Preserve unambiguous exact-name lookup when the definition's namespace is explicit.
- Support reuse across teams without confusing a name match with semantic agreement.
- Avoid replacing global name coordination with another mandatory review process.

## Considered Options

- Global uniqueness.
- Team-scoped uniqueness.
- Domain- or value-domain-scoped uniqueness.
- No hard uniqueness.
- Advisory or warning models instead of hard uniqueness.

## Decision Outcome

Recommended option: "Team-scoped uniqueness", because the definition's owning Dapla team provides an existing responsibility boundary and a namespace that authors can choose without negotiating with the whole organisation. This recommendation remains **Proposed**. Improved production velocity is a hypothesis, not a measured result.

### Namespace and exact comparison

The namespace is the **definition's owning Dapla team**, as expressed by its `owned-by` relationship. It is not the team of an instance, dataset, data product or consumer.

- A canonical `short_name` uses lowercase with underscores and is compared exactly.
- Accepted aliases are compared by their exact stored value. There is no case folding, whitespace trimming or other normalisation for uniqueness or exact-name lookup.
- Canonical names and accepted aliases share one namespace within each owning team. An exact value cannot name two different definitions in that team, whether the collision is canonical-to-canonical, canonical-to-alias or alias-to-alias.
- Proposed and rejected aliases do not reserve names. Accepting an alias must satisfy the same per-team constraint as a canonical name.
- Identical names in different teams are allowed without collision warnings or a publication gate. Semantic duplicate definitions introduce no new publication gate; detecting and consolidating them remains future work.

For example, `team-a` and `team-b` may each publish `income`. Within `team-a`, another definition cannot use `income` as either its canonical name or an accepted alias. An accepted alias stored as `Income` is distinct from `income`; that does not make `Income` a valid canonical `short_name`.

### Lookup and reference identity

A canonical name can resolve to a definition only with explicit `(definition owner team, canonical short_name)` context. The caller must supply or select the definition owner's team, not infer it from the instance's own team. Without that context, a bare name is insufficient for unambiguous resolution.

After resolution, store and use the stable `definitionId` as the actual reference key in the typed `defined-by` relationship from ADR 0001. The team/name pair is a lookup context, not a replacement identity or stored relationship key. An instance owned by one team may refer to a definition owned by another.

An exact accepted-alias match in an explicitly selected definition-owner namespace may surface a candidate. It requires human confirmation of the definition before storing its `definitionId`; it never creates an automatic `defined-by` link. The alias lifecycle and evidence requirements remain in ADR 0002.

For example, an instance from `team-c` may select `(team-a, income)`, resolve that canonical name and store the resulting `definitionId`. Selecting `team-b` instead identifies that team's definition. Neither selection is implied by `team-c`'s ownership, and a matching alias still requires confirmation.

### Consequences

- Good, because authors can publish without reserving names across the organisation.
- Good, because exact lookup remains unambiguous within an explicit owner namespace, including canonical/accepted-alias collisions.
- Good, because stable IDs support cross-team reuse independently of physical names.
- Bad, because a bare short name no longer identifies a definition organisation-wide; discovery and consumers must show or obtain the definition-owner context.
- Bad, because the same name can describe different concepts across teams and semantic duplicates can proliferate. The uniqueness constraint does not solve semantic governance, even within a team.
- Bad, because accepting an alias can conflict with another definition's local name, and organisational changes affect the namespace lifecycle.

## Pros and Cons of the Options

### Global uniqueness

- Advantage: one exact short name identifies at most one definition across the organisation; consumers need no team context for name lookup.
- Disadvantage: authors compete for names and must coordinate outside their team, discouraging publication and encouraging artificial names.
- Disadvantage: globally different names do not prevent semantic duplicates, and a matching name alone does not establish semantic compatibility.

### Team-scoped uniqueness

- Advantage: aligns naming authority with the definition owner and bounds coordination while retaining an exact lookup guarantee.
- Disadvantage: requires explicit namespace context and leaves cross-team duplication possible. Team ownership changes need a separate lifecycle policy.
- Preferred over the alternatives because it removes the reported cross-team reservation pressure without making local name lookup ambiguous.

### Domain- or value-domain-scoped uniqueness

Two distinct candidates are involved: using the existing classification series as a value-domain namespace, or adding a new subject-area taxonomy as a domain namespace. The existing classification series is optional (`classified-by` has cardinality `0..1`) and describes a value domain, not a subject-area taxonomy.

- Advantage of value-domain scope: reuses an existing relationship and groups definitions using the same classification series without regard to team boundaries.
- Disadvantage of value-domain scope: it may group unrelated concepts sharing a value domain and split related concepts using different value domains. Unclassified definitions have no namespace under this rule; covering them would need another policy or a new classification requirement.
- Advantage of a new subject-area taxonomy: could align naming with semantic stewardship across organisational teams rather than with allowed values.
- Disadvantage of a new subject-area taxonomy: adds a model and governance burden. Authors must agree on subject-area boundaries and assignment before publishing; overlapping or changing areas complicate namespace selection and can recreate the coordination bottleneck. The existing classification series does not supply this subject-area scope.

### No hard uniqueness

- Advantage: eliminates name reservation conflicts entirely, even within a team; stable IDs still make explicit references unambiguous.
- Disadvantage: even an owner-qualified canonical name can return multiple definitions, requiring extra selection and increasing the risk of mistaken links.
- Not preferred because local exact lookup is useful and can be preserved without imposing organisation-wide coordination.

### Advisory or warning models

- Advantage: global or local collision warnings can encourage discovery and reuse without technically blocking publication.
- Disadvantage: warnings still ask authors to judge whether they are taking another team's name and may become a de facto approval gate.
- Disadvantage: without a hard local constraint, exact owner-qualified lookup remains ambiguous; with one, cross-team warnings add friction without improving that guarantee.
- Not preferred as the naming policy. Ordinary discovery is compatible with the recommendation, but identical cross-team names must not trigger collision warnings.

## Unresolved Follow-up

- Definition ownership transfer: how to handle collisions and preserve lookup expectations when a definition moves between teams.
- Team slug changes: how a renamed team's namespace is identified and how prior lookup contexts behave. Stable `definitionId` references remain the identity, but this ADR does not prescribe namespace redirects or rename behaviour.
- Semantic duplicate detection and consolidation, including any future governance.
- Rollout and measurement of the velocity hypothesis belong to a later decision. This ADR sets no migration procedure, rollout commitment or measurement programme.
