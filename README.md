# Dapla Pseudo System

Functionality that provides pseudonymization, de-pseudonymization and re-pseudonymization for Dapla.

See [docs](https://statisticsnorway.github.io/-system) for more information.

The Dapla Pseudo System is composed of a collection of libraries and services:

<!-- linked-repos-start -->
* [dapla-dlp-pseudo-service](https://github.com/statisticsnorway/dapla-dlp-pseudo-service)
* [dapla-dlp-pseudo-func](https://github.com/statisticsnorway/dapla-dlp-pseudo-func)
* [dapla-dlp-pseudo-core](https://github.com/statisticsnorway/dapla-dlp-pseudo-core)
* [tink-fpe](https://github.com/statisticsnorway/tink-fpe)
* [dapla-toolbelt-pseudo](https://github.com/statisticsnorway/dapla-toolbelt-pseudo)
* [-iac](https://github.com/statisticsnorway/-iac)
<!-- linked-repos-end -->


## Development

Run `make install` to configure your local development environment.

All available make targets: 

<!-- make-help-start -->
```
install                        Install the dev environment (pre-commmit hooks and git repos)
doctor                         Ensure that local tools and environment settings are configured correctly
update-git-repos               Pull all related git repos
serve-docs                     Serve docs locally
```
<!-- make-help-end -->
