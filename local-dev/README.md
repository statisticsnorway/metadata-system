# Local development

This directory contains the setup for running the services metamapper, metamapper-dispatcher and datadoc-service locally. 
The repositories are expected to be located in the same parent directory as metadata-system.

## Configure the local environment

Create your local environment file from the provided example:

```bash
cp metadata-system/local-dev/.env.example metadata-system/local-dev/.env
```
Open `.env` and provide values for all variables.

Next, in each service's repo, create the file `/src/main/resources/application-local.yml`. Remember to provide the datasource password for the datadoc-service file:

#### metamapper

```
micronaut:
  server:
    host: 127.0.0.1
    port: 8081
  http:
    services:
      datadoc-service:
        url: http://localhost:8080
        connect-timeout: 5s
        read-timeout: 30s
      metamapper-dispatcher:
        url: http://localhost:8085
  security:
    enabled: false
    oauth2:
      clients:
        metamapper-m2m-token:
          enabled: false

gcs:
  emulator:
    host: localhost
    port: 4443

app:
  config-verifier:
    enabled: false
  poller:
    fixed-delay: 2s
  bucket:
    shared:
      allowed-suffixes: .parquet
      excluded-suffixes: ""
      include-paths: ""
      exclude-paths: ""
    product:
      allowed-suffixes: .parquet
      excluded-suffixes: ""
      include-paths: ""
      exclude-paths: ""
```

#### metamapper-dispatcher

```
micronaut:
  server:
    host: 127.0.0.1
    port: 8085
  http:
    services:
      dapla-api:
        url: http://127.0.0.1:9
        connect-timeout: 1s
        read-timeout: 1s

endpoints:
  all:
    port: 8095

dapla:
  api:
    token: local-unused

dispatcher:
  load-environment: test
  dapla:
    buckets:
      types-to-include: []
  manual-task:
    bucket-name: local-bucket
    environment: test
```

#### datadoc-service

```
micronaut:
  server:
    host: 127.0.0.1
    port: 8080
  security:
    enabled: false

endpoints:
  all:
    port: 8090

datasources:
  default:
    url: jdbc:postgresql://localhost:5432/datadoc
    username: datadoc
    password: 
    driver-class-name: org.postgresql.Driver
```


## Start the infrastructure

```
docker compose up -d
```

## Start the services

Start each service in a separate terminal window. Startup order:
 - datadoc-service
 - metamapper-dispatcher
 - metamapper

### Datadoc-service

Run the following command to start the service:
```
./start.sh datadoc
```

### Metamapper

```
./start.sh metamapper
```

### Metamapper dispatcher

```
./start.sh dispatcher
```

### Using process managers 

#### process-compose

Install [process-compose](https://f1bonacc1.github.io/process-compose/installation/)

Run:
```
process-compose --no-server
```

#### dekit

Install with [Homebrew](https://formulae.brew.sh/formula/dekit) or [docs for dekit](https://dekit.run/docs/start/getting-started):

Run:
```
dekit
```
