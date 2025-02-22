#!/bin/bash

# Qt4とBoostをインストール
sudo apt update
sudo apt install qt4-default
sudo apt install libboost-all-dev

# Extract-dataをclone
git clone git@github.com:RoboDragons/Extract-data.git
cd ~/Extract-data
git submodule update --init --recursive

# ssl-logtoolsの準備
cd ~/Extract-data/ssl-logtools
mkdir build
cd build
cmake ..
make

# ssl-visionの準備
cd ~/Extract-data/ssl-vision
./InstallPackagesUbuntu.sh
make

# Python環境の構築
sudo apt install python3 python3-pip -y
sudo apt install python3-venv -y
python3 -m venv ~/myenv
source ~/myenv/bin/activate
pip install numpy pandas
pip install protobuf==3.20.0

# Java環境の構築
sudo apt install openjdk-21-jdk -y