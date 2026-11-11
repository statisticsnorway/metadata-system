# 0001 — Folder-level PAM entitlement for eligible buckets

- **Status:** accepted
- **Date:** 2026-11-10
- **Authority:** @statisticsnorway/dapla-metadata-developers

## Context and Problem Statement

Metamapper needs to read data files from managed team buckets in order to extract metadata on variables in each data file. There is some risk associated with this as this access is granted in addition to current data access controls which are assigned exclusively through membership in a Dapla team.

To grant this access in as safe a manner as possible, we wish to limit the scope as much as possible, in the following axes:

- In terms of permissions, Metamapper should be assigned only the minimum access required to perform its task.
- In terms of the number of data storage locations it has simultaneous access to.
- In terms of the duration of access, access should last only as long as necessary to perform the task.

## Considered Options

- One PAM entitlement per eligible bucket, provisioned at the stable parent folder.
- One stable folder-level PAM entitlement covering matching descendant buckets.
- One PAM entitlement per team, provisioned on that team's child folder below the stable parent (possible Phase 2 direction).

## Decision Outcome

Chosen option: "One stable folder-level PAM entitlement covering matching descendant buckets", because it avoids per-bucket entitlement provisioning and covers newly matching descendant buckets during an active grant.

IaC provisions and maintains one stable PAM entitlement at a stable parent folder. It grants simultaneously to matching descendant buckets across descendant projects and folders. The entitlement's resource-name filter is intended to include only these approved bucket-name templates:

- `ssb-<team>-data-produkt-prod`
- `ssb-<team>-data-delt-<kortnavn>-prod`
- `ssb-<team>-data-delt-delomat-<kortnavn>-prod`

The intended exact exclusion is the `-kilde-` token; for example, the kilde bucket format is `ssb-<team>-data-kilde-prod`. Google IAM Conditions document limits for resource-name string matching. Naming rules will be documented but are not centrally enforced, so this filter must not be represented as a hard guarantee that kilde buckets are excluded. This entitlement's filter also does not guarantee MetaMapper's total effective access: other IAM or ACL allow paths are accepted.

Use custom role `ssb.bucket.read` as-is; a separate permission-inventory review is not a prerequisite. Only the MetaMapper runtime service account is an eligible requester, with automatic approval.

IaC owns provisioning the stable entitlement. Application configuration explicitly supplies both the entitlement ID and expected parent-folder ID. The application checks the entitlement's identity and state against that configuration, but does not parse arbitrary CEL as semantic proof of its resource scope. The application manages grants only. A missing, disabled, or inconsistent entitlement fails closed with an explicit error; the caller may retry after the configuration is corrected.

Keep the existing temporary-access service and PostgreSQL coordination. Concurrent jobs share one coordinated grant. Retain the configured 1–10 distinct-bucket cap only as workload/concurrency control, not as an authorization boundary. Limit a grant to one hour, with no background auto-renewal. After expiry, reacquire on demand at the next read. Retry transient IAM propagation within a bounded policy, then fail explicitly. Revoke the grant when no active work remains.

Reconcile uncertain PAM request or revoke outcomes before retrying. Pending and unknown states remain conservative until reconciled. Accept and defer bucket retirement and name-reuse handling.

Keep the feature disabled until an isolated Standard-tier GCP test verifies the folder boundary, the name patterns and representative exclusions, `ssb.bucket.read` list/read behavior, expiry, and revocation.

### Consequences

- Good, because one entitlement covers newly matching descendant buckets without per-bucket provisioning.
- Good, because IaC provisions the entitlement while the application identity remains limited to grant management.
- Bad, because the entitlement's scope is broader than any one job's selected buckets. The application cap limits workload/concurrency only; it does not narrow the entitlement.
- Bad, because the intended name filter is subject to documented IAM Conditions resource-name matching limits, and naming rules are not centrally enforced. The accepted scope gap must remain explicit.
- Bad, because other IAM or ACL allow paths can independently provide access, so this entitlement alone cannot describe or guarantee MetaMapper's total effective access.
- Bad, because configuration errors or unavailable entitlement state produce explicit acquisition failures, and bucket retirement/name reuse are not handled by this decision.

## Pros and Cons of the Options

The chosen option's benefits and costs are described above. The other options were not chosen for the following reasons:

- **One entitlement per eligible bucket.** It requires provisioning a new entitlement for each eligible bucket and does not provide the confirmed stable folder-level grant model.
- **One entitlement per team on a child folder.** It is a possible future direction, but is deferred; its provisioning, scope, ownership, and runtime details remain undecided.

## Appendix: Phase 2 direction (undecided)

The only stated future direction is to have one PAM entitlement per team, provisioned dynamically by infrastructure on that team's child folder below the stable parent. Its intended scope would cover that team's produkt/delt buckets while excluding kilde. `dapla-api` would supply entitlement details rather than relying on IDs generated by convention.

Phase 2 is deferred. Its scope, provisioning contract, ownership, runtime behavior, and other implementation details remain undecided; this appendix records a direction only and creates no further commitments.

## More Information

- [PAM overview](https://docs.cloud.google.com/iam/docs/pam-overview)
- [Create PAM entitlements](https://docs.cloud.google.com/iam/docs/pam-create-entitlements)
- [Request temporary elevated access](https://docs.cloud.google.com/iam/docs/pam-request-temporary-elevated-access)
- [PAM entitlement deletion](https://docs.cloud.google.com/sdk/gcloud/reference/pam/entitlements/delete)
- [IAM condition attribute reference](https://docs.cloud.google.com/iam/docs/conditions-attribute-reference)
- [IAM resource name attributes](https://docs.cloud.google.com/iam/docs/conditions-resource-attributes)
- [Cloud Storage bucket naming](https://docs.cloud.google.com/storage/docs/buckets#naming)


---

*Copied from [statisticsnorway/metamapper@9b490f5](https://github.com/statisticsnorway/metamapper/blob/9b490f5/docs/adr/0001-folder-entitlement-scoped-grants.md) on 2026-11-11 by `make collect-adrs`. The canonical version is maintained in that repository.*
