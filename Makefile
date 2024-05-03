.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: default
default: | help

.PHONY: install
install: doctor update-git-repos ## Install the dev environment (pre-commmit hooks and git repos)
	@pre-commit install

.PHONY: update-readme
update-readme:  ## Update the README.md file
	@./bin/update_readme.py

.PHONY: doctor
doctor: ## Ensure that local tools and environment settings are configured correctly
	@./bin/doctor.py

.PHONY: update-git-repos
update-git-repos: ## Pull all related git repos
	@./bin/update_git_repos.py

.PHONY: serve-docs
serve-docs: ## Serve docs locally
	mkdocs serve
