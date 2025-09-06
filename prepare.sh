#!/bin/bash

set -e

# xtermでコマンドを実行
xterm -e "cd ./ssl-logtools/build && make && bin/logplayer ../2024-07-19_14-29_GROUP_PHASE_RoboDragons-vs-TIGERs_Mannheim.log.gz; bash" &
#xterm -e "cd ./ssl-logtools/build ; bash" &

#xterm -e "cd ./AutoReferee; ./run.sh; bash" &