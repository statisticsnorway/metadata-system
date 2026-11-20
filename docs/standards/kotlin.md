# Shared Kotlin guidance

For Kotlin work, read the target repository's `AGENTS.md`, contributor guide and
relevant ADRs first. These recommendations extract reusable patterns from
Datadoc Service, MetaMapper and MetaMapper Dispatcher; they do not replace local
architecture or authorize a migration of an existing test suite.

## Implementation preferences

1. Prefer Kotlin-native language features, standard-library APIs and Kotlin
   packages over Java-style APIs or handwritten compatibility layers.
2. Prefer native Micronaut features in this order: configuration-based
   facilities first; then interface- or annotation-based clients, repositories
   and integrations; handwritten boilerplate last.
3. Use handwritten plumbing only when the native options do not fit the local
   domain or requirements. Preserve established local architecture where it is
   intentional.

## Tests and tooling

- Prefer **Kotest** for Kotlin tests, following the repository's existing spec
  style, fixtures, project configuration and Micronaut integration.
- For HTTP integration tests, prefer the **Rest Assured Kotlin DSL**
  (`Given`, `When`, `Then`) where Rest Assured is appropriate. Reuse local HTTP
  fixtures and authentication helpers. Non-HTTP tests need no HTTP dependency.
- Prefer real integrations when feasible. For isolated tests, prefer small test
  double implementations of interfaces and static fixtures/data. For external
  HTTP APIs, prefer a simulated server such as Microcks or another local
  contract-compatible server. **Strongly avoid mocks and framework/dynamic mock
  libraries**; use one only when these alternatives cannot reasonably model the
  required behavior and local rules permit it.
- Use **ktlint** through the target repository's configured tasks and rules.
- Use **Micronaut-managed test resources** for real integration tests where the
  service and datastore support them. Preserve local resource lifecycle and
  isolation; focused unit tests need not start a full application.

Versions, compatible integrations, commands, test tags and coverage enforcement
come from the target's `gradle/libs.versions.toml`, `build.gradle.kts` and CI.
In particular, an integration artifact named `micronaut-test-kotest5` or a runner
named `junit5` is not sufficient evidence of the actual Kotest major version.
Check the configured dependency and the tests themselves.

## Evidence and local distinctions

- Datadoc Service: [build configuration](https://github.com/statisticsnorway/datadoc-service/blob/main/build.gradle.kts),
  [version catalogue](https://github.com/statisticsnorway/datadoc-service/blob/main/gradle/libs.versions.toml),
  [Kotest service tests](https://github.com/statisticsnorway/datadoc-service/blob/main/src/test/kotlin/no/ssb/metadata/datadoc/services/DatasetServiceTest.kt)
  and [HTTP Kotlin DSL](https://github.com/statisticsnorway/datadoc-service/blob/main/src/test/kotlin/no/ssb/metadata/datadoc/controllers/TaskRegistrationControllerTest.kt).
  Dataset identity, migrations and HTTP fixtures remain local.
- MetaMapper: [build configuration](https://github.com/statisticsnorway/metamapper/blob/main/build.gradle.kts)
  and [Kotest/MockK handler tests](https://github.com/statisticsnorway/metamapper/blob/main/src/test/kotlin/no/ssb/metadata/metamapper/services/ListObjectsHandlerTest.kt).
  MockK here is observed existing usage, not the shared recommendation. Its
  grant-model ADR and resource lifecycle remain local.
- Dispatcher: [build configuration](https://github.com/statisticsnorway/metamapper-dispatcher/blob/main/build.gradle.kts)
  and [version catalogue](https://github.com/statisticsnorway/metamapper-dispatcher/blob/main/gradle/libs.versions.toml)
  declare Kotest, MockK, Kotlin HTTP extensions and Micronaut resource support.
  These declarations are observations, not endorsements of mocking.
  Actual HTTP tests still use the Java-style DSL; see [gaps](gaps.md).
  Queue architecture and real-API test gating remain local.

Resolve source paths under the configured `$METADATA_REPOS_ROOT` described in
the [repository catalogue](../repositories.md) before relying on remote links.
Java and Terraform guidance remains local or organizational; neither has shared
tooling recommendations here.
