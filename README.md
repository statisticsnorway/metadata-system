# Metadata System

Create, publish and use metadata for datasets, instance variables, concept variables and classifications.

See [docs](https://statisticsnorway.github.io/metadata-system) for more information.

The Metadata System is composed of a collection of libraries and services:

<!-- linked-repos-start -->
* [datadoc](https://github.com/statisticsnorway/datadoc)
* [ssb-datadoc-model](https://github.com/statisticsnorway/ssb-datadoc-model)
* [klass](https://github.com/statisticsnorway/klass)
* [vardef](https://github.com/statisticsnorway/vardef)
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
