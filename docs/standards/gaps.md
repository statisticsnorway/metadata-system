# Standards gaps and historical differences

These are evidence-labelled observations for planning, **not authorization** to
change frameworks, dependencies, CI, versions or coverage thresholds. Local
configuration remains authoritative. Lifecycle labels are the
[user-confirmed decisions](../repositories.md), not deductions from tooling age.
Resolve source paths under `$METADATA_REPOS_ROOT` as described in the catalogue.

## Maintained repositories

| Repository | Observed evidence | Difference from shared guidance |
| --- | --- | --- |
| vardef (stable) | [Build](https://github.com/statisticsnorway/vardef/blob/main/build.gradle.kts) configures JUnit; [model tests](https://github.com/statisticsnorway/vardef/blob/main/src/test/kotlin/no/ssb/metadata/vardef/models/VariableDefinitionTest.kt) import JUnit. HTTP tests under `src/test/kotlin` use `io.restassured.RestAssured` rather than Kotlin extension imports. | Existing JUnit and Java-style HTTP DSL differ from the recommended Kotest and Kotlin HTTP DSL. Preserve the suite; any adoption is separate work. |
| metamapper-dispatcher (active) | [Build](https://github.com/statisticsnorway/metamapper-dispatcher/blob/main/build.gradle.kts) declares Kotlin HTTP extensions. [ManualBucketLoadControllerTest](https://github.com/statisticsnorway/metamapper-dispatcher/blob/main/src/test/kotlin/no/ssb/metadata/metamapper/dispatcher/controllers/ManualBucketLoadControllerTest.kt) and [TaskQueueControllerTest](https://github.com/statisticsnorway/metamapper-dispatcher/blob/main/src/test/kotlin/no/ssb/metadata/metamapper/dispatcher/controllers/TaskQueueControllerTest.kt) import `io.restassured.RestAssured`. | Declared Kotlin DSL support is not actual Kotlin DSL adoption. |
| metamapper-dispatcher (active) | [Test workflow](https://github.com/statisticsnorway/metamapper-dispatcher/blob/main/.github/workflows/run-tests.yml) runs `./gradlew test ktlintCheck`; the build applies JaCoCo but does not finalize tests with `jacocoTestReport`. | Unlike Datadoc Service and MetaMapper CI, this workflow does not invoke the JaCoCo report. No new report requirement or CI change is made here. |
| metamapper (active) | [AGENTS.md](https://github.com/statisticsnorway/metamapper/blob/main/AGENTS.md) describes tests as "Kotest 5 + MockK"; the [version catalogue](https://github.com/statisticsnorway/metamapper/blob/main/gradle/libs.versions.toml) resolves a newer Kotest major. | Instruction text is stale; configuration is authoritative. Integration artifact names containing `kotest5` do not establish the dependency major. |
| dapla-toolbelt-metadata (stable) | [CONTRIBUTING.md](https://github.com/statisticsnorway/dapla-toolbelt-metadata/blob/main/CONTRIBUTING.md) says 100% coverage; [pyproject.toml](https://github.com/statisticsnorway/dapla-toolbelt-metadata/blob/main/pyproject.toml) has `tool.coverage.report.fail_under = 80`. | Policy and enforcement disagree. Record both; keep current enforcement until a separately approved policy decision. |

## Historical references only

| Repository | Observed evidence | Interpretation |
| --- | --- | --- |
| metadata-api-gateway (deprecated) | [Build](https://github.com/statisticsnorway/metadata-api-gateway/blob/main/build.gradle.kts) uses JUnit and Micronaut Rest Assured; existing tests under `src/test/kotlin` use JUnit and Java-style Rest Assured rather than the Kotlin DSL. | Historical parallel to Vardef, not a migration target. |
| ssb-datadoc-model (deprecated) | [Generated Python manifest](https://github.com/statisticsnorway/ssb-datadoc-model/blob/main/generated/python/datadoc_model/pyproject.toml) declares uv, pytest, pytest-cov and Ruff. [Python CI](https://github.com/statisticsnorway/ssb-datadoc-model/blob/main/.github/workflows/test-python.yml) invokes pytest only; the inspected manifest/workflow provide neither Nox sessions nor mypy checks. | Some Python tooling exists; the maintained Toolbelt's fuller automation is not present in these inspected sources. Preserve source/generated boundaries and historical tooling. |

Shared recommendations cover Kotlin, Python and TypeScript only. Legacy Java
and organizational Terraform standards are deliberately retained in their
existing scope; neither is a gap to fill through this consolidation.
