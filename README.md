# Poppler CI

This repository contains the static infrastructure definition for the Poppler CI service. The infrastructure uses [Docker Compose]() and [Buildbot](https://buildbot.net).

## Overview

The Poppler CI service consists of two main components:

1. A Buildbot instance that is configured to run the various tasks needed to
   provide the service.
2. A set of _workers_ that provide the environment where all tasks can run.

### Buildbot

Buildbot is a reliable and flexible continuous integration (CI) project. It
provides a web interface to its activities and coordinates monitoring a git
repository and starting various tasks based on git activity and possibly other
events.

### Workers

#### Build & Test

This worker provides an environment that can build the Poppler sources and
run its test suite. It captures build output and compares it to a stable set
of expected “references” (or refs) and provide a report containing a visual
diff of the unexpected results.

TBD: there will be a way to accept new refs from the process as expected for
future CI runs.

#### Fetch Sources & Create Refs

This worker downloads all files listed in a `sources.txt` (TBD where this is maintained) file. From these sources, the worker creates a set of references
in the form of `.ps`, `.text`. `.md5` and `.png` files and makes the those available in a shared directory on the build server so that the Build & Test worker can use it to compare its output to.

The Fetch Sources task is smart enough to not download a file twice.

TODO: make sure that the accept-new-refs task does not get its results clobbered
by the Create Refs task

## Getting Started

### Prerequisistes

- Docker
- Docker Compose

### Building the Workers

To be able to run the workers, you first have to build them. In order to do
that, check out the `poppler-buildbot` repository.

```shell
cd poppler-buildbot
cd worker
docker built -t poppler-ci-test1 .
```
### Running the Service (locally)

For testing this setup locally or on a server, you can follow these steps.
 If you want to set this up permanently on a server, there are more
 instructions below.

```shell
cd service
# edit docker-compose.yaml in the `worker` section to point to `poppler-ci-test1`
docker-compose up
```

This launches all components and makes the Buildbot Web UI available at http://127.0.0.1:8180.

Use `ctrl-c` once to stop all services.

You can use `docker-compose up -d` to start all services in the background and
later use `docker compose down` to stop them again.

## Running the Service (in production)

TODO:
- letsencrypt?
- auth?
