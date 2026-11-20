# 0001 — Team-folder PAM entitlements and application-managed grants

- **Status:** accepted
- **Date:** 2026-11-19
- **Authority:** @statisticsnorway/dapla-metadata-developers

## Context and Problem Statement

Metamapper needs to read data files from managed team buckets in order to extract metadata on variables in each data file. There is some risk associated with this as this access is granted in addition to current data access controls which are assigned exclusively through membership in a Dapla team.

To grant this access in as safe a manner as possible, we wish to limit the scope as much as possible, in the following axes:

- In terms of permissions, Metamapper should be assigned only the minimum access required to perform its task.
- In terms of the number of data storage locations it has simultaneous access to.
- In terms of the duration of access, access should last only as long as necessary to perform the task.

## Considered Options

- One PAM entitlement per eligible bucket.
- One entitlement on a stable ancestor folder, covering eligible buckets across teams.
- One entitlement per team, provisioned on that team's folder.

## Decision Outcome

Chosen option: "One entitlement per team, provisioned on that team's folder", because entitlement provisioning is implemented externally with this scope. It avoids per-bucket grant/provisioning churn without giving one grant access across all teams.

Each entitlement grants simultaneous access to all produkt/delt buckets covered by that team's entitlement. Selecting one workload bucket does not narrow the grant's authorization scope. Different teams have different folder parents; there is no configured global entitlement parent.

Infrastructure owns the entitlements, their IAM bindings, custom role `ssb.bucket.read`, and the conditions implementing the produkt/delt scope and intended kilde exclusion. The application neither creates/edits entitlements nor edits IAM, reproduces bucket-name CEL, or treats CEL parsing as proof of scope. Use the existing custom role as-is; a separate permission-inventory review is not a prerequisite.

The grant service is an in-process application service, not a separately deployed broker or a new public endpoint. A trusted caller supplies the externally obtained, fully qualified entitlement resource name, for example `folders/123/locations/global/entitlements/team-a`. No entitlement ID is derived from a bucket name. Entitlement discovery, including any future `dapla-api` integration, is outside this implementation.

Only the MetaMapper runtime service account is an eligible requester, with automatic approval. The service uses Application Default Credentials (ADC); configuration of the expected principal does not impersonate that principal. Before acquisition it checks the returned entitlement identity, AVAILABLE state, automatic approval, requested duration, exact eligible principal, and that its IAM access resource matches the folder in the supplied name. It does not independently verify which team or buckets that folder belongs to. Trusted upstream selection and external provisioning remain responsible for that association and scope.

### Grant lifecycle and coordination

Retain the temporary-access abstraction and durable PostgreSQL coordination approach from the historical grant-service work. Coordinate one non-terminal grant generation per full entitlement name, not per bucket. Jobs for produkt and delt buckets under the same entitlement share it; jobs using different team entitlements do not.

Each acquisition records a borrower lease with a workload bucket and a deadline. The explicitly configured 1–10 distinct-bucket cap is global to the participating application instances and is workload control only. A released bucket frees its workload slot while another live borrower keeps the team grant. If a generation has no live borrowers but PAM termination remains uncertain, its associated buckets retain capacity conservatively. All participating instances must share the same database, expected requester and capacity configuration.

Requests default to one hour and must be whole seconds from one second to one hour, within the entitlement's maximum. A shared lease can expire sooner: its deadline is bounded by the requested duration and the remaining PAM grant lifetime. Expiry is derived from PAM's reported access-grant timestamp and requested duration, not a local assumption about activation time. Callers must stop reads at the returned deadline and reacquire on demand before further reads. There is no background renewal.

Release is idempotent by borrower UUID. Other live borrowers retain access; the last release initiates revocation. Periodic reconciliation also handles abandoned/expired leases. A revoke operation acknowledgement is not proof of termination: observe a terminal grant state before freeing the generation. IAM propagation can outlast PAM state transitions; terminal state alone is not proof of effective Cloud Storage access removal.

Persist create intent before sending the request, use the generation UUID as PAM request ID and justification marker, and never automatically reassign a create sender or resend create after an uncertain result. Reconcile by listing grants on that supplied entitlement and matching the marker, then by GET once its name is known. A paused process can resume much later than PAM's documented request-ID deduplication window. If no result ever becomes visible, retain the generation and require operator investigation rather than risking a duplicate grant.

Pending, unavailable, malformed and unknown PAM responses never authorize reads. Unexpected foreign/duplicate grants, incompatible ownership or externally modified bindings block the generation and require investigation; the application does not revoke foreign access. Unknown states and transient transport failures are retried by subsequent reconciliation, not interpreted as termination. Database failures propagate explicitly. HTTP requests, activation/release polling and grant-list pagination are bounded; polling budgets can be exceeded by in-flight bounded operations. No unbounded automatic retries are used.

### Consequences

- Good, because a team grant covers its produkt/delt workload together while avoiding the former cross-team ancestor entitlement.
- Good, because entitlement/IAM administration stays outside the application, and PostgreSQL sharing survives concurrent jobs, replicas and restarts.
- Bad, because access is broader than a selected workload bucket; a one-bucket workload cap still permits access to every bucket covered by that team's entitlement.
- Bad, because uncertain create outcomes can require operator intervention and reduce capacity. This is preferred to unsafe duplicate creation.
- Bad, because database availability and coordinated configuration are prerequisites, and the coordination lock serializes short state transitions.
- Bad, because provisioning conditions and naming assumptions need real-cloud verification. Other IAM/ACL allow paths can independently grant access; the entitlement cannot guarantee total effective access or absolute kilde exclusion.
- Bad, because bucket retirement/name reuse remain deferred, and the upstream entitlement-to-work association must be trustworthy.

## Pros and Cons of the Options

The chosen option's benefits and costs are described above. The alternatives were not retained for these reasons:

- **One entitlement per eligible bucket.** More provisioning and lifecycle coordination, and it conflicts with the implemented simultaneous team-level scope.
- **One stable ancestor entitlement.** Avoids team-specific inputs but gives a single grant access across teams. This was the previously accepted direction, now replaced by externally provisioned team-folder entitlements.

## Implementation Status and Activation Prerequisites

The application now implements `TemporaryBucketAccess.acquire(entitlementName, bucket, duration)` and `release(leaseId)`, a PAM REST adapter, Micronaut Data repositories, a Flyway schema, and periodic reconciliation. It follows the historical temporary-access design rather than adding a parallel broker; the previous grant implementation was on a closed, unmerged branch, not main. PostgreSQL Test Resources tests exercise sharing, cross-instance coordination, duration/deadline bounds, expiry, revocation and uncertain outcomes; local HTTP tests exercise the PAM wire contract. These are not evidence of real-cloud scope or permission behavior.

The feature remains disabled by default (`app.bucket-access.enabled=false`). Before activation:

- Supply a shared NAIS-provisioned PostgreSQL datasource named `bucket-access`, with dialect `POSTGRES`, credentials and a JDBC URL through deployment configuration. Flyway owns the isolated `bucket_access_schema_history` and application tables. Provisioning/deployment activation is separate; this change makes no cloud or NAIS resource changes.
- Set `app.bucket-access.max-simultaneous-buckets` explicitly in 1–10 and `app.bucket-access.requester-principal` to the runtime `serviceAccount:<email>`. Optional duration and timeout settings live under the same prefix; defaults are one-hour duration, 30-second activation/release budgets, one-second polling and 15-second HTTP requests. Reconciliation defaults to every 30 seconds; it cleans up/reconciles but never renews.
- Supply trusted entitlement names at the internal service boundary. The current dispatcher `Task` schema has no entitlement name, so task handlers and Cloud Storage reads are deliberately not wired to this service. Decide the upstream delivery contract separately; do not infer IDs, invent discovery or expose an endpoint to fill this gap.
- Integrate callers so leases cover listing and the entire lazy/streaming Parquet read, are released on completion/failure/cancellation, and are reacquired on demand after expiry. Add bounded retries for transient Cloud Storage IAM propagation, then fail explicitly. This read-path integration and its propagation behavior are not implemented or claimed here; existing reads remain unchanged.
- Give the runtime ADC identity eligibility to request the supplied entitlements and the necessary `privilegedaccessmanager.entitlements.get`, `privilegedaccessmanager.grants.list`, `privilegedaccessmanager.grants.get`, and `privilegedaccessmanager.grants.revoke` permissions on the appropriate team-folder resources. Eligibility to request grants does not by itself establish revocation permission. The service does not need entitlement list/create/update/delete or folder IAM-editing privileges. Actual bindings must be reviewed and verified externally; this is not a recommendation to grant a broad administrator role.
- Run an isolated Standard-tier GCP verification of the team folder boundary, simultaneous produkt/delt access, representative kilde/external-team exclusions, the existing `ssb.bucket.read` list/read behavior, automatic approval, actual runtime permissions, propagation, expiry and effective revocation.

### Decision History

The original context above is preserved. On 2026-11-10 this ADR accepted one stable ancestor-folder entitlement and recorded per-team provisioning as an undecided "Phase 2" possibility. On 2026-11-19 the per-team direction was chosen following external provisioning implementation. It is the current architecture, not a deferred phase. The grant service is implemented locally; entitlement delivery to jobs, read-path activation and real-cloud verification remain outstanding.

## More Information

- [PAM overview](https://docs.cloud.google.com/iam/docs/pam-overview)
- [Create PAM entitlements](https://docs.cloud.google.com/iam/docs/pam-create-entitlements)
- [Request temporary elevated access](https://docs.cloud.google.com/iam/docs/pam-request-temporary-elevated-access)
- [PAM entitlement deletion](https://docs.cloud.google.com/sdk/gcloud/reference/pam/entitlements/delete)
- [Grant REST resource and lifecycle states](https://docs.cloud.google.com/iam/docs/reference/pam/rest/v1/folders.locations.entitlements.grants)
- [Create grants and request-ID deduplication](https://docs.cloud.google.com/iam/docs/reference/pam/rest/v1/folders.locations.entitlements.grants/create)
- [Revoke grants and required permission](https://docs.cloud.google.com/iam/docs/reference/pam/rest/v1/folders.locations.entitlements.grants/revoke)
- [IAM condition attribute reference](https://docs.cloud.google.com/iam/docs/conditions-attribute-reference)
- [IAM resource name attributes](https://docs.cloud.google.com/iam/docs/conditions-resource-attributes)
- [Cloud Storage bucket naming](https://docs.cloud.google.com/storage/docs/buckets#naming)


---

*Copied from [statisticsnorway/metamapper@31a4900a60c177de14518412898366c2eddba7c7](https://github.com/statisticsnorway/metamapper/blob/31a4900a60c177de14518412898366c2eddba7c7/docs/adr/0001-folder-entitlement-scoped-grants.md) on 2026-11-20 by `make collect-adrs`. The canonical version is maintained in that repository.*
