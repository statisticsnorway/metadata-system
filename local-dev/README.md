# Local development

This directory contains the setup for running the services locally. The repositories are expected to be located in the same parent directory.

## Configure the local environment

Create your local environment file from the provided example:

```bash
cp .env.local.example .env.local
```
Open `.env.local` and provide values for all required variables.

Next, in each service's repo, copy the file `application-local.yml.example` to `application-local.yml`.

## Start the infrastructure

```
docker compose --env-file .env.local up -d
```

## Start the services

Start each service in a separate terminal window:

### Datadoc-service

If not set, open ```application-local.yml``` and provide a password for the database connection.

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

### Using process-compose

Install [process-compose](https://f1bonacc1.github.io/process-compose/installation/)

```
process-compose --no-server -f process-compose.yml -e .env.local up
```