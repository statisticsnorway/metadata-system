#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG is required}"
RISK_THRESHOLD="${RISK_THRESHOLD:-1.0}"
SEVERITIES="${SEVERITIES:-High,Critical}"

grype "$IMAGE_TAG" -o json > grype-report.json

SEVERITIES_JSON="$(
  printf '%s' "$SEVERITIES" |
    jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; "")) | map(select(length > 0))'
)"

jq \
  --arg threshold "$RISK_THRESHOLD" \
  --argjson severities "$SEVERITIES_JSON" '
  [
    .matches[]
    | select(
        (.vulnerability.severity as $severity
          | ($severities | index($severity)) != null)
        and ((.vulnerability.risk // 0) > ($threshold | tonumber))
      )
    | {
        package: .artifact.name,
        version: .artifact.version,
        vulnerability: .vulnerability.id,
        severity: .vulnerability.severity,
        risk: (.vulnerability.risk // 0),
        fix: (.vulnerability.fix.versions[0] // "none")
      }
  ]
  | sort_by(.risk)
  | reverse
' grype-report.json > filtered-vulns.json