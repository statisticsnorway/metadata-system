# Diagrams

## Relationship model diagram

Interactive view of the entities and the named relationships between them. The
normative specification is [Metadata relationships](../metadata-relationships.md).

<iframe src="metadata-relationships.html" title="Metadata relationship model diagram" style="width: 100%; height: 85vh; min-height: 640px; border: 0;" loading="lazy"></iframe>

[Open the diagram full screen](metadata-relationships.html)

## Working with diagrams

Diagrams are generated with Archify and committed as standalone HTML, so building and
publishing the docs needs no diagram toolchain.

> Archify is an **agent skill, not a project tool**. Nothing pins its version in the repo
> — there is no `make` target or CI step for it, and diagram work is normally done
> conversationally with a coding agent that has the skill installed: you describe the model
> or the change, the agent edits the JSON and rebuilds. The committed HTML is what keeps
> that arrangement safe — the docs build never needs the CLI, and a reviewer sees the
> rendered result.

- Edit `docs/diagrams/<name>.archify.json`, never the generated HTML.
- Commit `docs/diagrams/<name>.html` alongside it; MkDocs copies it verbatim to
  `diagrams/<name>.html`.
- The page that embeds it (`docs/diagrams/index.md`) uses an iframe so the site navigation
  stays visible. A new diagram needs that page plus an entry in `mkdocs.yml`.
- `.archify/` holds scratch output and receipts and is gitignored.

Regenerate after changing the JSON:

```bash
node <archify>/bin/archify.mjs finalize architecture \
  docs/diagrams/metadata-relationships.archify.json \
  docs/diagrams/metadata-relationships.html \
  --quality showcase
```

The build is deterministic: unchanged source produces a byte-identical file, so the commit
diff only reflects real edits. Preview with `make serve-docs`;
`docs/metadata-relationships.md` §12 has the same instructions in context.
