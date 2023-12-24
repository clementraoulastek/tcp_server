# Kamas Dashboard

This repository is a TCP server for messenger application.

# Conda env

A virtual environment is used to run the project. It is managed by conda.

## Create the environment

```bash
conda env create -f environment.yml
```

## Activate the environment

```bash
conda activate server-tcp
```

# Run the app 

## In dev mode
```bash
make run
```

## In prod mode

```bash
make run
```

# Run the tests

```bash
make test
```

# Deploy the app

## Build the docker image

```bash
make docker-build
```

## Push the docker image

```bash
make docker-push
```
