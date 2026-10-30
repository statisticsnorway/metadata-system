# ADR0005 - Dataset variables are identified by short name and data type within a dataset

* Status: accepted
* Authority: @statisticsnorway/dapla-metadata-developers
* Date: 2026-10-21

## Context and problem statement

A `DatasetVariable` is read from the schema of the data files in a `Dataset` and is shared by every data file of that
dataset that contains it, through the join table `data_file_dataset_variable`. Producers report the schema of each
file, and nothing in it says that a column in one scan is the same column as one with another name in the next.

We need to decide what identifies a variable, what a rename or a changed data type in a data file means, and what
happens to a variable that no data file refers to anymore.

## Decision drivers

* Duplicates within a dataset must be impossible: the same name and data type must never exist twice.
* A later scan must not overwrite the data type of a DatasetVariable, since that could misrepresent its true meaning.
* The only information we receive about a variable is its schema node.
* Variables are shared between files, so changing one affects every file linked to it.
* We do not yet know which details of a schema node (such as precision and scale) Datadoc needs, so we store only what
  identifies a variable.
* The decision should be enforceable in the schema, since changes are expensive to undo (ADR0003 has no undo migrations).

## Considered options

* Identify a variable by `(dataset, shortName, physicalTypeName, logicalTypeName)`; a rename or a changed data type is a
  new variable; unlinked variables are deleted
* Identify a variable by `(dataset, shortName)`; a rename is a new variable; unlinked variables are deleted. A later scan
  may then overwrite the data type.
* Identify a variable by `(dataset, shortName)`, but allow renaming it in place
* Keep a separate stable identity for a variable, independent of its name

## Decision

Chosen option: "Identify a variable by `(dataset, shortName, physicalTypeName, logicalTypeName)`; a rename or a changed
data type is a new variable; unlinked variables are deleted", because the file schema is the only source for variables,
and it cannot tell a rename or a type change from a removal plus an addition.

The data type is part of the identity because overwriting it with a later scan could misrepresent the true meaning of the
variable. We have no single value that represents both the physical and the logical type, and the logical type carries
details (such as precision and scale) that we do not yet know whether it should distinguish DatasetVariables. We therefore store
the name of each type as a string, `physicalTypeName` and `logicalTypeName`, and use both.

1. **Identity.** A DatasetVariable is identified within a dataset by `shortName`, `physicalTypeName` and `logicalTypeName`,
   which are taken from the schema node the variable was created from. The combination is unique, enforced by the
   constraint `uk_dataset_variable_identity`. The `id` (UUID) is only the row key that the links refer to.
2. **Missing types count as a value.** `physicalTypeName` is null for structs and lists, and `logicalTypeName` is null
   for columns without a logical type annotation, for example `BOOLEAN`. The constraint is `UNIQUE NULLS NOT DISTINCT`
   (PostgreSQL 15 or newer; production and test run 17), so that two variables with the same name and the same missing
   types are duplicates. A plain `UNIQUE` constraint would allow them.
3. **Only names and type names are stored.** We store the DatasetVariable's name and the names of its types, not the whole
   schema node. Details that are not part of the identity, such as precision, scale and `children`, are not kept. 
4. **A rename or a changed type in a data file is a new DatasetVariable.** The file is linked to the DatasetVariable with the new name
   or type, and the link to the old one is removed. An existing DatasetVariable is never changed in place because it is shared:
   changing it would also change it for other files which still contain the old column.
5. **A DatasetVariable with no links is deleted.** Nothing in the database does this, because a foreign key cascade fires on
   deleting a parent and cannot express "delete when no longer referenced" (see ADR0004). It is the application's
   responsibility to delete unlinked DatasetVariables whenever links change, that is when a file's DatasetVariables are replaced and
   when task completion deletes files. This is not implemented yet.

### Positive consequences

* No duplicate DatasetVariables (same name and datatype) are possible within a dataset, whatever code path writes them.
* A later scan cannot overwrite the datatype of a DatasetVariable.
* Links are never silently moved to a different column by a rename or a changed type.
* The schema needs no extra tables or identity columns for DatasetVariables.

### Negative consequences

* A dataset can hold several DatasetVariables with the same name but different datatypes, for example after a column
  changed type between scans.
* History is lost across a rename or a type change: the new DatasetVariable is unrelated to the old one. This becomes a
  problem once users enrich DatasetVariables, see the open points.
* Details of the schema node that are not part of the identity are not stored. Adding one later needs a new column and
  a migration, and a rescan to fill it for existing DatasetVariables. See ADR0006.
* Until the cleanup in rule 4 is implemented, DatasetVariables which lose their last link remain, reserve their name in the
  unique constraint, and show up as DatasetVariables of the dataset.
* Cleanup lives in the application, so a code path that changes links without it leaves orphans behind.
* Nothing stops a data file from being linked to a DatasetVariable of another dataset than its own. This is not enforced in
  the schema, because `dapla_data_file.dataset_id` is nullable and a composite foreign key would not apply to files
  without a dataset. It must be upheld by the code that creates links.

## Pros and cons of the options not chosen

### Rename in place

* Positive, because the links and any future metadata follow the DatasetVariable.
* Negative, because it is wrong for a shared DatasetVariable when the rename comes from one file.
* Negative, because the rename can collide with an existing DatasetVariable of the same name and then needs a merge operation.
* Negative, because scanning continues to be the only source of which DatasetVariables exist. Users will enrich what a scan
  found, not define DatasetVariables, so a rename always arrives through a scan and not as a user action.

### Identify by `(dataset, shortName)` only

* Positive, because a column whose type changes stays one DatasetVariable and keeps its links.
* Negative, because a later scan would then overwrite the data type, or keep an outdated one, and either misrepresents
  the DatasetVariable for files that still have the other type.

### A separate stable identity

* Positive, because a rename could keep its identity.
* Negative, because we have no input that tells us two names are the same DatasetVariable, so we would have to ask users or
  guess.

## Open points

* **User enrichment of scanned DatasetVariables.** Files and DatasetVariables will keep being scanned, and users will later enrich the
  metadata found by the scan. That enrichment is stored with the DatasetVariable, so a rename in a data file, being a new
  DatasetVariable, leaves the enrichment on the old one. Rule 4 would then delete that DatasetVariable, and the enrichment with it,
  once no file is linked to it. Decide before enrichment exists whether such a DatasetVariable should be deleted, kept for
  user review, or have its enrichment carried over to a DatasetVariable the user points out as its replacement.
* **Distinguishing by logical type details.** The logical type is stored by name only. Two `DECIMAL` columns with the
  same name but different precision or scale are the same DatasetVariable. Decide whether that is acceptable, or whether such
  details should become part of the identity.
* **Types of nested columns.** Only the top-level node is stored. Whether the nested `children` of a struct or list need
  to be stored as DatasetVariables of their own is not decided.
* **Cleanup trigger.** Decide whether to clean up eagerly in the same transaction as the link change, as assumed in rule
  4, or in a periodic job. The first avoids a window where orphans are visible.

## Links

* Related to [ADR0004 — Dataset variables are removed by database cascade](0004-cascade-deletes-for-dataset-variables.md)
* Related to [ADR0003 — Adopt Flyway for schema migrations](0003-adopt-flyway-for-schema-migrations.md)
* Migration: `src/main/resources/db/migration/V3__add_dataset_variable.sql`
* Entities: `src/main/kotlin/no/ssb/metadata/datadoc/models/DatasetVariable.kt`, `DaplaDataFile.kt`

<!-- markdownlint-disable-file MD013 -->


---

*Copied from [statisticsnorway/datadoc-service@ab0fc6d](https://github.com/statisticsnorway/datadoc-service/blob/ab0fc6d/docs/adr/0005-dataset-variables-are-identified-by-short-name.md) on 2026-10-30 by `make collect-adrs`. The canonical version is maintained in that repository.*
