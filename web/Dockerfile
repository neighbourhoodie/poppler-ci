FROM docker.io/library/debian:testing

# Last build date - this can be updated whenever there are security updates so
# that everything is rebuilt
ENV security_updates_as_of 2023-09-01

# This will make apt-get install without question
ARG DEBIAN_FRONTEND=noninteractive

# Install security updates and required packages
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install -q python3-flask rsync \
    && mkdir /buildbot \
    && useradd -ms /bin/bash buildbot

USER buildbot
WORKDIR /buildbot/web

CMD ["flask", "run", "--debug", "--host=0.0.0.0"]
