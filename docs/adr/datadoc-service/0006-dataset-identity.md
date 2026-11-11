# 0006 - A Dataset groups related data files

- **Status:** proposed
- **Date:** 2026-11-11
- **Authority:** @statisticsnorway/dapla-metadata-developers

## Context and Problem Statement

A Dataset needs to describe how data files relate to one another in terms that are meaningful to producers and consumers. Treating each physical data file as its own Dataset reflects where data happens to be stored, but obscures which files belong to the same conceptual group. Conversely, grouping files too broadly can combine data that consumers need to distinguish.

The definition must describe the data independently of a particular storage layout. One Dataset may be available from multiple locations, and each location may expose only part of its files.

## Decision Drivers

- Consumers need to understand which files are related as one Dataset.
- Dataset identity should express the data's ownership and meaning, not a particular storage or access arrangement.
- A Dataset should not combine distinct groups merely because they share a product and state.
- Optional organizational structure should not determine whether files belong to the same Dataset.
- A Dataset's identity should remain useful when file-level characteristics vary.

## Considered Options

- Treat each physical data file as a separate Dataset.
- Give each storage location its own Dataset identity.
- Include optional subfolders in Dataset identity.
- Group related files by producing team, product, data state, and short description, independently of storage location and optional subfolders.

## Decision Outcome

Chosen option: "Group related files by producing team, product, data state, and short description, independently of storage location and optional subfolders", because it gives consumers a coherent conceptual group while retaining meaningful ownership and product distinctions without making physical organization part of the definition.

A Dataset is the logical group of data files produced by one team for one product and data state that share a short description. Files with the same combination of these characteristics belong to the same Dataset.

A storage location describes where some or all of a Dataset's files can be accessed; it does not create a different Dataset. Making files available in another location neither changes the Dataset's identity nor transfers its ownership. A location may expose only a subset of the Dataset's files.

Optional subfolders may organize files, but do not divide a Dataset. Period, version, and file type describe individual files and may vary among files in the same Dataset.

### Consequences

- **Good:** Related files can be understood as one Dataset even when they are stored or accessed in different locations.
- **Good:** File-level variation in period, version, or type does not unnecessarily split a Dataset.
- **Good:** Optional folder arrangements can change without changing Dataset identity.
- **Bad:** The producing team and short description must be clear enough to distinguish groups within a product and state.
- **Bad:** A location may offer only part of a Dataset, so availability at one location does not imply that every file in the Dataset is accessible there.

## Pros and Cons of the Options Not Chosen

### One physical file per Dataset

- **Positive:** Each Dataset corresponds directly to one stored object.
- **Negative:** Related files appear unrelated, making the broader data group harder for consumers to understand.
- **Negative:** Identity is tied to physical storage rather than the meaning and ownership of the data.

### A separate Dataset identity for each storage location

- **Positive:** Each identity corresponds to the files exposed at a particular location.
- **Negative:** The same conceptual group is split when it is available in multiple locations, even when those locations expose different subsets.
- **Negative:** An access arrangement becomes part of what the Dataset is, rather than where it can be accessed.

### Include optional subfolders in identity

- **Positive:** Folder-based groupings can distinguish files.
- **Negative:** Files can be split or regrouped based on an optional storage convention, even when their conceptual identity is unchanged.
- **Negative:** A folder change can appear to change Dataset identity without changing the data's ownership or meaning.


---

*Copied from [statisticsnorway/datadoc-service@dfee8a8](https://github.com/statisticsnorway/datadoc-service/blob/dfee8a8/docs/adr/0006-dataset-identity.md) on 2026-11-11 by `make collect-adrs`. The canonical version is maintained in that repository.*
