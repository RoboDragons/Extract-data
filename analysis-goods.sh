#!/bin/bash

# Clone the SSL-Vision repository

git clone git@github.com:RoboCup-SSL/ssl-logtools.git
cd ssl-logtools

# Create and move to the build directory
mkdir build
cd build

# Run CMake and Make
cmake ..
make

# Install cmake if it's missing
sudo apt-get install cmake

# Remove potential lock files
sudo rm /var/lib/apt/lists/lock
sudo rm /var/lib/dpkg/lock
sudo rm /var/lib/dpkg/lock-frontend

# Install cmake again just to be sure
sudo apt-get install cmake

# Run make again
make

# Add the PPA and install QT4 packages
sudo add-apt-repository ppa:/ubuntuhandbook1/ppa
sudo apt update
sudo apt install qt4-*

# Run make again
make

# Clone the SSL-Logtools repository

#cd ../../
#git clone git@github.com:RoboCup-SSL/ssl-vision.git
#cd ./ssl-vision

# Run the Install Packages script
#sudo ./InstallPackagesUbuntu.sh
