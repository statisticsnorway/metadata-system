# ADR format and conventions

The Metadata System uses **MADR (Markdown Architectural Decision Records)** as
the canonical format for architecture decision records. This guide in
**statisticsnorway/metadata-system** defines the shared format for this repository
and its child repositories. It is the source of truth for the format, not for
the decisions owned by each repository.

The template below is a lightweight use of [MADR](https://adr.github.io/madr/),
with status and date written as Markdown list items to match the existing ADR
metadata and publication tooling.

## Authoring conventions

- Write one decision per Markdown file with a descriptive title.
- In this repository, use `docs/adr/NNNN-short-kebab-case-title.md`, continuing
  the existing four-digit sequence. Child repositories retain their own ADR
  locations and numbering.
- Record the status (`proposed`, `accepted`, `rejected`, `deprecated`, or
  `superseded`) and date (`YYYY-MM-DD`). A proposed decision is not yet accepted.
- Explain the problem, considered options, chosen option and rationale, and
  consequences. Include both benefits and costs; record genuine alternatives
  rather than inventing options to fill the template.
- Use relative links to related ADRs in the same repository. When replacing a
  decision, link the new and superseded records to each other and update the
  old record's status to `superseded`.

Use the template for new ADRs. Existing records keep their history and need not
be reformatted merely to adopt this guide. Snapshots under `docs/adr/<repo>/`
are generated copies: edit the originating repository's ADR and refresh with
`make collect-adrs` instead of editing the snapshot.

## Template

Copy the following into a new ADR and replace the placeholders. Keep the core
sections shown here. Add MADR's optional sections, such as **Decision Drivers**,
**Pros and Cons of the Options**, **Confirmation**, or **More Information**, when
they help explain or verify the decision.

```markdown
# NNNN - Short title describing the decision

- **Status:** proposed
- **Date:** YYYY-MM-DD

## Context and Problem Statement

Describe the situation and the problem or question this decision addresses.

## Considered Options

- First option
- Second option

## Decision Outcome

Chosen option: "First option", because explain why it best addresses the problem.

### Consequences

- Good, because describe a benefit.
- Bad, because describe a cost, risk, or limitation.
```

Add a `Supersedes` or `Related` metadata item with links when applicable.
Detailed option comparisons can live under **Pros and Cons of the Options**
rather than obscuring the decision outcome.

## Child-repository agents

Agents authoring or reviewing ADRs in a child repository must consult this guide
in metadata-system. Keep the format here; link to it from the child repository's
agent instructions instead of maintaining a separate template.

For example, add this instruction to the child repository's `AGENTS.md` (or its
existing equivalent):

```markdown
When creating or editing ADRs, follow the canonical
[MADR format and conventions defined in metadata-system](https://github.com/statisticsnorway/metadata-system/blob/main/docs/adr-format.md).
```

This repository's root `AGENTS.md` provides the pointer for agents working here.
A standalone child-repository checkout does not inherit that file, so it needs
the explicit reference in its own agent instructions. This shared format does
not prescribe where a child repository stores its ADRs.
