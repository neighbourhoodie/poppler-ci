# Poppler CI

This repository contains the static infrastructure definition for the Poppler CI
service. The infrastructure uses [Docker Compose]() and
[Buildbot](https://buildbot.net).

  - [Overview](#overview)
    - [Buildbot](#buildbot)
    - [Workers](#workers)
    - [Flask admin app](#flask-admin-app)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Worker set up](#worker-set-up)
    - [Building the Workers](#building-the-workers)
    - [Running the Service (locally)](#running-the-service-locally)
  - [Running the Service (in production)](#running-the-service-in-production)
    - [Prerequisites for the initial set up](#prerequisites-for-the-initial-set-up)
    - [Setting hostnames](#setting-hostnames)
    - [TLS](#tls)
    - [Authorization](#authorization)
    - [Final step](#final-step)

## Overview

The Poppler CI service consists of several components:

1. A Buildbot instance that is configured to run the various tasks needed to
   provide the service.
2. A set of _workers_ that provide the environment where all tasks can run.
3. A Flask application that provides admin functions not available directly via
   Buildbot.
4. A "backend" nginx server that provides access to Buildbot, the Flask admin
   app, and static files such as HTML build reports, and also implements HTTP
   Basic Auth.
5. A "frontend" nginx server designed for production, which implements HTTPS and
   endpoints needed to support Certbot, and proxies to the "backend" nginx.

### Buildbot

Buildbot is a reliable and flexible continuous integration (CI) project. It
provides a web interface to its activities and coordinates monitoring a git
repository and starting various tasks based on git activity and possibly other
events.

### Workers

This worker provides an environment that can build the Poppler sources and run
its test suite. It captures build output and compares it to a stable set of
expected “references” (or refs) and provide a report containing a visual diff of
the unexpected results.

The reference sources and outputs are kept in the `refs` directory. At the start
of each test run, these refs are updated from two sources:

- A list of filenames and URLs stored in `refs/manifest.txt`
- The `unittestcases` and `tests` suites in the repository
  `https://gitlab.freedesktop.org/poppler/test`

Only files that do not already exist are added to the reference sets; all
existing files remain as they are from previous test runs. Each "suite" of
references reside in their own directory, e.g. `refs/unittestcases` for the unit
tests, and `refs/corpus` for the sources listed in `refs/manifest.txt`. Under
each of these directories is a `sources` directory containing the original PDFs,
and an `outputs` directory containing the results of converting those PDFs to
various other formats using Poppler.

When a build is run, the outputs are regenerated and compared to those in
`refs/*/outputs`. The results of each build are kept in
`outputs/poppler-builder/build-N` where `N` is the build number indicated by
Buildbot. An HTML report including diffs is generated and placed in this
directory, and its URL is printed at the end of the test run. Only the outputs
of failing tests are retained, and these can be used to update the refs if a
maintainer decides that these failing tests actually represent desired changes.

### Flask admin app

This application provides admin functions that cannot be expressed directly in
Buildbot. The application can be accessed via the url `/cmd` on the build
server.

The tasks available are:

- **Update the refs from a build**: if a maintainer determines that a failed
  build's outputs actually represent desired changes, they can "promote" those
  outputs to become new references. By entering the build number into a form,
  the `refs/update` script is invoked to copy files from the build's output
  directory into `refs`.

- **Clean up build outputs**: to free up disk space, a maintainer can delete the
  `outputs` directory content for all but the most recent N builds.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Worker set up

Poppler builbot-worker's configuration is based on the default one provided by
[Builbot](https://github.com/buildbot/buildbot), but needs to be based on
`debian:testing` and requires some additional packages. These changes are
applied in our fork of the Buildbot repository. To build the worker, run these
commands:

```sh
# TODO: replace this with a repo on Poppler's GitLab
$ git clone https://github.com/neighbourhoodie/poppler-buildbot.git
$ cd poppler-buildbot/worker
$ docker build -t poppler-ci-test1 .
```

### Running the Service (locally)

For testing this setup locally or on a server, you can follow these steps. If
you want to set this up permanently on a server, there are more instructions
below.

```shell
docker compose up
```

This launches all components and makes the Buildbot Web UI available at
`http://127.0.0.1:8180`.

Use `ctrl-c` once to stop all services.

You can use `docker-compose up -d` to start all services in the background and
later use `docker compose down` to stop them again.

## Running the Service (in production)

### Prerequisites for the initial set up

- A server, and ssh with root access to it
- A domain name set up to point to the server's IP address
- An email address where Certbot can send emails to
- The ability to git clone this repo onto the server, or get it there some other
  way
- Be able to install on the server:
  - Docker
  - Docker Compose (`apt install -y docker-compose`)
  - htpasswd (`apt install -y apache2-utils`)

### Setting hostnames

The Buildbot service needs to know the domain name that is used to access it in
the browser. In development, this is `http://127.0.0.1:8010`. In production,
this needs to be set to your own domain.

In `docker-compose.yml`, edit `BUILDBOT_WEB_URL` to reflect the server's public
URL, e.g. `https://ci.example.com`.

### TLS

To enable HTTPS in buildbot's website, Certbot is used. To set it up and allow
Let's encrypt to issue the TLS certificate, follow these steps:

1. Locate yourself at the root of the project folder `poppler-ci`
2. Create an `.env` file with your variables:

```sh
cp services/nginx-https/.env.default services/nginx-https/.env
```

and with the editor of your choice (we're demoing with `nano`), fill the
variables:

```sh
nano services/nginx-https/.env
```

3. Run the installation script

Go to the `services/nginx-https` folder and run `certbot-install.sh`:

```sh
cd services/nginx-https
./certbot-install.sh
```

This script will create the necessary directories and use Certbot to request the
certificate to Let's encrypt.

The TLS certificate expires every 90 days. For automatic renewal, a cron job has
been set up by the script at `/etc/cron.d/renew_certificate_job`, which will run
on the first of each month. This job will call the `/renew-certificate.sh`
script. Logs from that script go to `/var/log/syslog` and have the renew-cert
prefix.

> [!NOTE]
> The certificate renewal cronjob assumes that the path to the repository is
> `/root/poppler-ci`. If this is not the case, please modify
> `/etc/cron.d/renew_certificate_job` accordingly.

### Authorization

`nginx` with [basic
auth](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/)
is used to restrict access to certain parts of the CI. To create and manage user
credentials, you can use a tool like `htpasswd`. At the root of the project, run
the following command, replacing `USERNAME` with your chosen username:

```sh
htpasswd -c services/nginx-app/etc/nginx/.htpasswd <USERNAME>
```

You'll be prompted to enter and confirm a password. This command creates a
`.htpasswd` file containing the username and a hashed password.

To manage access:

- Add a new user to an existing file

```sh
htpasswd services/nginx-app/etc/nginx/.htpasswd <USERNAME>
```

- To delete a user

```sh
htpasswd -D services/nginx-app/etc/nginx/.htpasswd <USERNAME>
```

Or manually delete the line with that username from the file.

### Final step

Once you've finished all the previous steps successfully, run:

```shell
docker compose up
```

This launches all components and makes the Buildbot Web UI available at
the domain you have specified in your `.env` file.
