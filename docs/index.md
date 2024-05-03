# Dapla Pseudo System

The following shows a C4 container diagram for the Dapla Pseudo System. Users (either statisticians or
automated processes, such as Kildomaten) interacts with the Pseudo Service REST API using the Dapla Toolbelt Pseudo python
client library. Pseudo Service interacts with external systems such as KMS or the stable-id-lookup-service.

```plantuml id="containerDiagram" format="svg_inline" title="Dapla Pseudo System Container Diagram"
    !include <C4/C4_Component>

    title Dapla Pseudo - System Container Diagram
    Boundary(pseudoSystem, "Dapla Pseudo", "gcp, ") {
    
        Container_Boundary(pseudoServiceContainer, "Pseudo Service") {
            Container(pseudoService, " [[https://vg.no dapla-dlp-pseudo-service]]", "java micronaut app", "Provides a REST API for (de/re/)pseudonymization")
            Component(pseudoFunc, "dapla-dlp-pseudo-func", "java library", "Pseudonymization algorithms and functions")
            Component(pseudoCore, "dapla-dlp-pseudo-core", "java library", "Processing, streaming, configuration handling and pseudo rule management")
            Component(tinkFpe, "tink-fpe-java", "java library", "Algorithms for Format Preserving Encryption")
    
            Rel(pseudoService, tinkFpe, "links", "library")
            Rel(pseudoService, pseudoFunc, "links", "library")
            Rel(pseudoService, pseudoCore, "links", "library")
        }

        ContainerDb(kms, "KMS", "GCP, ", "Manages Key Encryption Keys (KEKs) for working with Data Encyption Keys")
        Rel(pseudoService, kms, "(en/de)crypts Data Encryption Keys", "HTTPS")
    }

    Boundary(teamProject, "Team Project", "gcp, team-foeniks") {
        Person(kildomatenUser, "Kildomaten", "Automated processing (GCP Cloud Run)", "job", $sprite="robot")
        Person(statUser, "Statistician", "During development, e.g with Jupyter")
        ContainerDb(sourceDataBucket, "Source data", "GCP bucket", "Source data (not pseudonymized)")
        ContainerDb(productDataBucket, "Product data", "GCP bucket", "Pseudonymized data")
        Component(toolbeltPseudo, "dapla-tooolbelt-pseudo", "python library", "Toolkit for interacting with the Pseudo Service")

        Rel_L(kildomatenUser, sourceDataBucket, "Reads from", "HTTPS")
        Rel_L(kildomatenUser, productDataBucket, "Writes to", "HTTPS")
        Rel_U(kildomatenUser, toolbeltPseudo, "Uses", "library")
        Rel_R(statUser, toolbeltPseudo, "Uses", "library")
        Rel_R(toolbeltPseudo, pseudoService, "Makes API calls to", "JSON/HTTPS")
    }

    Boundary(freg, "FREG", "gcp, freg") {
        Container(sidLookupService, "stable-id-lookup-service", "python fastapi", "REST API for lookup of person-identifier stable IDs")
        Rel_R(pseudoService, sidLookupService, "Makes API calls to", "JSON/HTTPS")
   }
```
