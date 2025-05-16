FROM ubuntu:latest

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \

RUN     python3 \
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
    && rm -rf /var/lib/apt/lists/*

# Javaの環境変数を設定（=で記述）
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

WORKDIR ~

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

CMD ["/bin/bash"]