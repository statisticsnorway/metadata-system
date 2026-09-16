# Metadata System

Create, publish and use metadata for datasets, instance variables, concept variables and classifications.

See [docs](https://statisticsnorway.github.io/metadata-system) for more information.

The Metadata System is composed of a collection of libraries and services:

<!-- linked-repos-start -->

- [datadoc-editor](https://github.com/statisticsnorway/datadoc-editor)
- [ssb-datadoc-model](https://github.com/statisticsnorway/ssb-datadoc-model)
- [dapla-toolbelt-metadata](https://github.com/statisticsnorway/dapla-toolbelt-metadata)
- [klass](https://github.com/statisticsnorway/klass)
- [vardef](https://github.com/statisticsnorway/vardef)
- [metadata-api-gateway](https://github.com/statisticsnorway/metadata-api-gateway)
- [dapla-metadata-iac](https://github.com/statisticsnorway/dapla-metadata-iac)
- [ssb-dataportal](https://github.com/statisticsnorway/ssb-dataportal)
- [datadoc-service](https://github.com/statisticsnorway/datadoc-service)
- [metamapper](https://github.com/statisticsnorway/metamapper)
- [metamapper-dispatcher](https://github.com/statisticsnorway/metamapper-dispatcher)

<!-- linked-repos-end -->

## Development

Run `make install` to configure your local development environment.

All available make targets:

<!-- make-help-start -->

```
install                        Install the dev environment (pre-commmit hooks and git repos)
update-readme                  Update the README.md file
doctor                         Ensure that local tools and environment settings are configured correctly
update-git-repos               Pull all related git repos
serve-docs                     Serve docs locally
```

<!-- make-help-end -->
