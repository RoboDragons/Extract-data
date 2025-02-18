#!/bin/bash

# visionとlogtoolsをclone
git clone git@github.com:RoboCup-SSL/ssl-vision.git
git clone git@github.com:RoboCup-SSL/ssl-logtools.git

# Qt4とBoostをインストール
sudo apt update
sudo apt install qt4-default
sudo apt install libboost-all-dev

# ssl-logtoolsの準備
cd ssl-logtools
mkdir build
cd build
cmake ..
make

# ssl-visionの準備
cd ~/ssl-vision
./InstallPackagesUbuntu.sh
make