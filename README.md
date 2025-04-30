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

### Prerequisites

- Docker
- Docker Compose

### Worker set up

Poppler builbot-worker's configuration is based on the default one provided by [Builbot](https://github.com/buildbot/buildbot). However, Poppler currently requires Debian testing to execute its test with. For that purpose, we need to modify the default [Dockerfile](https://github.com/buildbot/buildbot/blob/7d203fc581d7f4a320f0091f983b55f8afa55bf2/worker/Dockerfile) with a few tweaks:

1. Use `debian:testing` as the image to pull from instead of `debian:12`:
```yaml
FROM docker.io/library/debian:testing
```

2. Prepare the build environment with the required dependencies, adding the following command:
```yaml
RUN echo 'deb-src http://deb.debian.org/debian unstable main' >> /etc/apt/sources.list \
     && apt-get update \
     && apt-get build-dep --yes --no-install-recommends poppler \
     && apt-get install --yes --no-install-recommends ninja-build libcurl4-openssl-dev git ca-certificates locales libgtk-3-dev libbrotli-dev libboost-container-dev qt6-base-dev
```

This means that whenever a new version of the default Dockerfile is released, these modifications must be reapplied on top of it.

### Building the Workers

To be able to run the workers, you first have to build them. In order to do
that, check out the `poppler-buildbot` repository.

```shell
cd poppler-buildbot
cd worker
docker build -t poppler-ci-test1 .
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

### Authorization

`nginx` with [basic auth](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) is used to restrict access to certain parts of the CI. To grant access to certain users:

1. Create a file `.htpasswd` in the `/etc` directory.
2. Generate a user + hashed password pair and include it into the `.htpasswd` file

TODO:
- letsencrypt?
- auth?
