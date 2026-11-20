# Repository catalogue

The Home Repo holds shared development guidance and pointers to separately cloned
repositories. Repository-specific architecture, commands and domain decisions
remain in each source repository. `git-repos.txt` is the unchanged machine list;
the catalogue below follows its order.

**Lifecycle is user-confirmed**, not inferred from GitHub archive flags, release
dates or dependency versions. Active repositories receive ongoing development;
stable repositories remain maintained. Deprecated repositories are historical
references and are not consolidation or tooling-migration targets.

| Repository | Languages and role | Lifecycle | Clone identifier | Remote |
| --- | --- | --- | --- | --- |
| datadoc-editor | Python dataset-documentation application | deprecated | `$METADATA_REPOS_ROOT/datadoc-editor` | [GitHub](https://github.com/statisticsnorway/datadoc-editor) |
| ssb-datadoc-model | JSON Schema with generated Java/Python models | deprecated | `$METADATA_REPOS_ROOT/ssb-datadoc-model` | [GitHub](https://github.com/statisticsnorway/ssb-datadoc-model) |
| dapla-toolbelt-metadata | Python metadata clients and tools | stable | `$METADATA_REPOS_ROOT/dapla-toolbelt-metadata` | [GitHub](https://github.com/statisticsnorway/dapla-toolbelt-metadata) |
| klass | Legacy Java classifications and code lists | stable | `$METADATA_REPOS_ROOT/klass` | [GitHub](https://github.com/statisticsnorway/klass) |
| vardef | Kotlin variable definitions | stable | `$METADATA_REPOS_ROOT/vardef` | [GitHub](https://github.com/statisticsnorway/vardef) |
| metadata-api-gateway | Kotlin API gateway | deprecated | `$METADATA_REPOS_ROOT/metadata-api-gateway` | [GitHub](https://github.com/statisticsnorway/metadata-api-gateway) |
| dapla-metadata-iac | Terraform infrastructure | stable | `$METADATA_REPOS_ROOT/dapla-metadata-iac` | [GitHub](https://github.com/statisticsnorway/dapla-metadata-iac) |
| ssb-dataportal | TypeScript metadata portal | active | `$METADATA_REPOS_ROOT/ssb-dataportal` | [GitHub](https://github.com/statisticsnorway/ssb-dataportal) |
| datadoc-service | Kotlin dataset metadata | active | `$METADATA_REPOS_ROOT/datadoc-service` | [GitHub](https://github.com/statisticsnorway/datadoc-service) |
| metamapper | Kotlin metadata extraction and access grants | active | `$METADATA_REPOS_ROOT/metamapper` | [GitHub](https://github.com/statisticsnorway/metamapper) |
| metamapper-dispatcher | Kotlin queue and task coordination | active | `$METADATA_REPOS_ROOT/metamapper-dispatcher` | [GitHub](https://github.com/statisticsnorway/metamapper-dispatcher) |

Set `METADATA_REPOS_ROOT` to the directory containing the child clones. Resolve
each clone as `$METADATA_REPOS_ROOT/<name>`; for a missing clone, select and
configure that root before cloning `https://github.com/statisticsnorway/<name>.git`
there. Read its `AGENTS.md` when present, followed by its linked local guidance.
Historical repositories retain their original contributor and README guidance.
Existing alternate clone layouts are not moved or rewritten by this catalogue.

## Shared guidance resolution

Standalone child checkouts do not inherit Home's `AGENTS.md`. Their agent
instructions should retain local rules and include a self-contained local-first
pointer:

> For shared Metadata guidance, resolve Home from `METADATA_SYSTEM_HOME` when
> explicitly set. If unset, use an existing Home checkout explicitly selected
> by the harness; do not guess a parent directory.
> Read `AGENTS.md` there, then the document triggered by this task:
> `docs/standards/kotlin.md`, `docs/standards/python.md` or
> `docs/standards/typescript.md` for that language;
> `docs/adr-format.md` for ADR work; `docs/standards/gaps.md` for standards
> planning; `docs/repositories.md` for lifecycle; `docs/skills.md` for optional skills.
> If Home is absent, select a location, clone
> `https://github.com/statisticsnorway/metadata-system.git` there, and set
> `METADATA_SYSTEM_HOME` to that checkout.
> If a required document is absent, report the missing guidance and activate the
> Home revision containing it before proceeding with work that depends on it.
> Local domain, security and organizational rules remain authoritative.

Set `METADATA_SYSTEM_HOME` to the Home checkout and
`METADATA_REPOS_ROOT` to the directory containing child clones. A child must
resolve document paths against Home, not its own directory or a guessed parent.
For ADRs, also retain the portable
[canonical guide URL](https://github.com/statisticsnorway/metadata-system/blob/main/docs/adr-format.md)
required by the [ADR conventions](adr-format.md#child-repository-agents).

**Local activation:** committing guidance on a Home feature branch does not
activate it in another checkout. Before push/merge, GitHub `main` and a fresh
clone may lack these documents. Set `METADATA_SYSTEM_HOME` to the checkout or
worktree containing the committed revision, or activate that revision in your
own Home checkout. A clone fallback alone cannot retrieve an unpushed branch.
This contract leaves clone layout flexible and does not authorize changes to
another checkout.
