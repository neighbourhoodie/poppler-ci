FROM docker.io/library/debian:testing

# This will make apt-get install without question
ARG DEBIAN_FRONTEND=noninteractive

# Install security updates and required packages
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install -q python3-flask rsync \
    && mkdir /buildbot \
    && useradd -ms /bin/bash buildbot

USER buildbot
WORKDIR /buildbot/flask

CMD ["flask", "run", "--debug", "--host=0.0.0.0"]
