FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-tk \
        gcc \
        g++ \
        cmake \
        make \
        git \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        openjdk-21-jdk \
        libboost-all-dev \
        gnome-terminal \
        dbus-x11 \
        locales \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen ja_JP.UTF-8

ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

WORKDIR /workspace


RUN python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt

CMD ["/bin/bash"]