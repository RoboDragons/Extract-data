#!/bin/bash
set -e

# XQuartz 経由での GUI 出力設定
export DISPLAY=host.docker.internal:0

# ssl-logtools-qt5 のビルド＆実行ディレクトリへ移動
cd ./ssl-logtools-qt5

# クリーンビルド用ディレクトリ作成
mkdir -p build
cd build

# Qt5 モードで CMake→Make
cmake -DUSE_QT5=ON ..
make

# ログプレイヤーを起動（最後にログファイル名を適宜変更）
./bin/logplayer ../log/2024-07-21_11-00_ELIMINATION_PHASE_ZJUNlict-vs-TIGERs_Mannheim.log.gz

# （必要ならここで AutoReferee 実行などを続ける）
# cd ../../../AutoReferee
# ./build.sh && ./run.sh