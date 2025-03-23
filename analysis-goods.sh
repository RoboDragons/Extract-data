#!/bin/bash

# Qt4とBoostをインストール
sudo apt update -y                # パッケージリストを最新に更新
sudo apt upgrade -y               # システムのパッケージを最新に更新
sudo apt install qt4-default      # Qt4（GUIアプリケーションフレームワーク）のインストール
sudo apt install libboost-all-dev # C++ライブラリのBoostをインストール

# Extract-dataをclone
git clone git@github.com:RoboDragons/Extract-data.git  # Extract-dataリポジトリをGitHubからクローン
cd ~/Extract-data                                      # プロジェクトフォルダに移動
git submodule update --init --recursive                # サブモジュールも含めて最新化

# ssl-logtoolsの準備
cd ~/Extract-data/ssl-logtools    # ssl-logtoolsディレクトリに移動
mkdir build                       # buildフォルダを作成
cd build                          # buildフォルダに移動
cmake ..                          # cmake でビルド環境を構築
make                              # make でコンパイル

# ssl-visionの準備
cd ~/Extract-data/ssl-vision             # ssl-visionディレクトリへ移動
./InstallPackagesUbuntu.sh               # 依存パッケージのインストール
make                                     # ビルド
cd ~                                     # ホームディレクトリに戻る

# Python環境の構築
sudo apt install python3 python3-pip -y  # Python3 と Pip（パッケージ管理ツール）をインストール
sudo apt install python3-venv -y         # python3-venv をインストール（仮想環境の作成に必要）
python3 -m venv ~/myenv                  # 仮想環境を作成
#pythonの仮想環境を無効化するコマンド
#deactivate
source ~/myenv/bin/activate              # 仮想環境を有効化
pip install numpy pandas matplotlib seaborn  # データ解析に必要なライブラリをインストール
pip install protobuf==3.20.0                 # プロトコルバッファーのバージョン指定
sudo apt install python3-tk python3-dev -y   # GUIツールキットと開発用ライブラリをインストール

# Java環境の構築
sudo apt install openjdk-21-jdk -y       # Java 21のJDKをインストール

# ~/.bashrc のパスを指定
BASHRC_FILE="$HOME/.bashrc"

# ~/.bashrc に指定の内容がすでに存在するか確認
if ! grep -q "cd" "$BASHRC_FILE"; then
    cat << 'EOF' >> "$BASHRC_FILE"

function cd() {
    builtin cd "$@" || return
    if [[ "$PWD" == *"/Extract-data" ]]; then
        source ~/myenv/bin/activate    # Extract-dataディレクトリに移動すると、自動的に仮想環境が有効化
    fi
}
EOF
    echo "内容を~/.bashrc に追加しました。"
    bash
else
    echo "~/.bashrc に既に指定の内容があります。"  # 重複を避けるためのチェック
fi