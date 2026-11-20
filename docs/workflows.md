# Shared workflows

This repo stores GitHub Actions workflows which may be reused in child repos. They're located in .github/workflows

## Grype security scan

Add this workflow to a consuming repository:

```yaml
name: Dependency scan

on:
  workflow_dispatch:
  schedule:
    - cron: "0 0 * * *"

jobs:
  grype-scan:
    uses: statisticsnorway/metadata-system/.github/workflows/dependency-scan.yaml@v1
    permissions:
      contents: read
      security-events: write
      packages: read
      actions: read
    with:
      docker-context: .
      dockerfile: Dockerfile
      image: dependency-scan-image:latest
```

The workflow builds and scans the Docker image, uploads SARIF results to GitHub Code Scanning, and stores JSON reports as workflow artifacts.

`@v1` references the version 1 tag. The consuming repository must have access to the shared workflow repository.

To release a new version:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

git tag -fa v1 -m "Update v1"
git push origin v1 --force
```

For a later release, repeat the process with v1.1.0 or another version tag.
