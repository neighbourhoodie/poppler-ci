# Poppler CI

This repository contains the static infrastructure definition for the Poppler CI service. The infrastructure uses [Docker Compose]() and [Buildbot](https://buildbot.net).

  - [Overview](#overview)
    - [Buildbot](#buildbot)
    - [Workers](#workers)
      - [Build \& Test](#build--test)
      - [Fetch Sources \& Create Refs](#fetch-sources--create-refs)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Worker set up](#worker-set-up)
    - [Building the Workers](#building-the-workers)
    - [Running the Service (locally)](#running-the-service-locally)
  - [Running the Service (in production)](#running-the-service-in-production)
    - [Prerequisites for the initial set up](#prerequisites-for-the-initial-set-up)
    - [TLS](#tls)
    - [Authorization](#authorization)

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

### Prerequisites for the initial set up

- A server, and ssh with root access to it
- A domain name set up to point to the server's IP address
- The ability to git clone this repo onto the server, or get it there some other way
- Be able to install on the server:
  - Docker
  - Docker Compose (`apt install -y docker-compose`)
  - htpasswd (`apt install -y apache2-utils`)

### TLS

To enable HTTPS in buildbot's website, Certbot is used. To set it up and allow Let's encrypt to issue the TLS certificate, follow these steps:

1. Locate yourself at the root of the project folder `poppler-ci`
2. Create an `.env` file with your variables:

```sh
cp ./service/.env.default ./service/.env
```

and with the editor of your choice (we're demoing with `nano`), fill the variables:
```sh
nano ./service/.env
```

2. Run the installation script

Go to the `service` folder, give execution permissions to the `certbot-install.sh` script, and run it:
```sh
cd ./service
chmod +x certbot-install.sh
./certbot-install.sh
```

This script will create the necessary directories and use Certbot to request the certificate to Let's encrypt.

The TLS certificate expires every 90 days. For automatic renewal, a cron job has been set up by the script at `/etc/cron.d/renew_certificate_job`, which will run on the first of each month. This job will call the `/renew-certificate.sh` script. Logs from that script go to `/var/log/syslog` and have the renew-cert prefix.

> [!NOTE]  
> The certificate renewal cronjob assumes that the path to the repository is `/root/poppler-ci`. If this is not the case, please modify `/etc/cron.d/renew_certificate_job` accordingly.

### Authorization

`nginx` with [basic auth](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) is used to restrict access to certain parts of the CI. To create and manage user credentials, you can use a tool like `htpasswd`. At the root of the project, run the following command, replacing `USERNAME` with your chosen username:

```sh
htpasswd -c ./service/etc/nginx/.htpasswd <USERNAME>
```

You'll be prompted to enter and confirm a password. This command creates a `.htpasswd` file containing the username and a hashed password.

To manage access:
- Add a new user to an existing file
```sh
htpasswd ./service/etc/nginx/.htpasswd <USERNAME>
```
- To delete a user
```sh
htpasswd -D ./service/etc/nginx/.htpasswd <USERNAME>
```
Or manually delete the line with that username from the file.


TODO:
- auth?
- remove all instances of `poppler-ci-test1` (rename it for something better)
