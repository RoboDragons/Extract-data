#!/bin/bash

# Qt4とBoostをインストール
sudo apt update -y
sudo apt upgrade -y
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
cd ~

# Python環境の構築
sudo apt install python3 python3-pip -y
sudo apt install python3-venv -y
python3 -m venv ~/myenv
source ~/myenv/bin/activate
pip install numpy pandas matplotlib seaborn
pip install protobuf==3.20.0
sudo apt install python3-tk python3-dev -y

# Java環境の構築
sudo apt install openjdk-21-jdk -y

# ~/.bashrc のパスを指定
BASHRC_FILE="$HOME/.bashrc"

# ~/.bashrc に指定の内容がすでに存在するか確認
if ! grep -q "cd" "$BASHRC_FILE"; then
    cat << 'EOF' >> "$BASHRC_FILE"

function cd() {
    builtin cd "$@" || return
    if [[ "$PWD" == *"/Extract-data" ]]; then
        source ~/myenv/bin/activate
    fi
}
EOF
    echo "内容を~/.bashrc に追加しました。"
    bash
else
    echo "~/.bashrc に既に指定の内容があります。"
fi
