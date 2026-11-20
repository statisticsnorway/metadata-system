# Shared TypeScript guidance

For TypeScript work, read the target's local agent guidance first. These
recommendations come from SSB Dataportal; its Next.js architecture, generated
clients, authentication, static fixtures and package-manager constraints stay
with that application.

- Use **strict TypeScript** and handle indexed access safely, following the
  target's `tsconfig.json` and type-generation prerequisites.
- Use **Biome** for linting and formatting with the target's configured rules.
  Preserve generated-code exclusions rather than manually fixing generated clients.
- Use **Vitest** for focused unit/component tests, reusing local Testing Library
  fixtures and test placement.
- Use **Playwright** for browser integration and end-to-end tests, retaining
  local authenticated/unauthenticated server isolation and static-data fixtures.
- Use **axe** for accessibility checks through existing Playwright helpers.
  Dataportal requires accessibility filenames and explicit `.withRules([...])`
  selection; follow its local README rather than inventing a shared ruleset.

**Browser boundary:** Dataportal's `playwright-cli` skill may access only its
local running development server on `http://localhost`, never other web resources.
This shared document does not broaden that skill, user instructions or any
repository-specific security boundary.

Evidence: Dataportal's
[agent guidance](https://github.com/statisticsnorway/ssb-dataportal/blob/main/AGENTS.md),
[package scripts](https://github.com/statisticsnorway/ssb-dataportal/blob/main/package.json),
[TypeScript configuration](https://github.com/statisticsnorway/ssb-dataportal/blob/main/tsconfig.json)
and [Biome configuration](https://github.com/statisticsnorway/ssb-dataportal/blob/main/biome.json).
Use the same paths in the [local clone](../repositories.md) for authoritative
commands, versions, coverage and CI; these recommendations authorize no
dependency, framework, threshold or application-architecture migration.
