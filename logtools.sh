#!/bin/bash

# .gz ファイルのリストを取得
dir="$HOME/Extract-data/ssl-logtools/build"
files=($dir/*.gz)

# ファイルが存在しない場合の処理
if [ ${#files[@]} -eq 0 ]; then
    echo "No .gz files found in $dir"
    exit 1
fi

# ファイル一覧を表示
echo "再生したいlogのファイルを選択してください:"
for i in "${!files[@]}"; do
    echo "$((i+1))) ${files[i]##*/}"
done

# ユーザーに選択を促す
while true; do
    read -p "番号を入力してください: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && ((choice > 0 && choice <= ${#files[@]})); then
        filename="${files[choice-1]}"
        break
    else
        echo "無効な入力です。正しい番号を入力してください。"
    fi
done

# SSL-logtoolの起動
gnome-terminal --tab -- bash -c "cd $HOME/Extract-data/ssl-logtools/build && bin/logplayer '$filename'; exec bash" &

# AutoRefereeのビルドと実行
gnome-terminal --tab -- bash -c "cd $HOME/Extract-data/AutoReferee && ./build.sh && ./run.sh; exec bash" &

# # 新しいターミナルでSSL Game Controllerを実行
# gnome-terminal --tab -- bash -c "$HOME/Extract-data/ssl-game-controller_v3.12.8_linux_amd64; exec bash" &

# # SSL-visionの起動
# gnome-terminal --tab -- bash -c "cd $HOME/Extract-data/ssl-vision && bin/graphicalClient; exec bash" &