#!/bin/bash

# エラーハンドリング
set -e

# ログプレイヤーを実行
gnome-terminal -- bash -c "cd ./ssl-logtools/build && make && bin/logplayer ../log/2024-07-21_11-00_ELIMINATION_PHASE_ZJUNlict-vs-TIGERs_Mannheim.log.gz; exec bash"
#gnome-terminal -- bash -c "cd ./ssl-logtools/build ; exec bash"

# AutoRefereeを別のターミナルで実行
#gnome-terminal -- bash -c "cd ./AutoReferee; ./run.sh; exec bash"
