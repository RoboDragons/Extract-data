import threading
import socket
import struct
import os
import numpy as np
import pandas as pd
import time
import messages_robocup_ssl_wrapper_pb2
import ssl_gc_referee_message_pb2
import math
import sys

debug = False
stop_event = threading.Event()

game_state = None  # グローバル変数としてゲームの状態を管理
Game_on = [2, 3, 4, 5, 8, 9]

sock = None

def setup_socket():
    global sock
    multicast_group = '224.5.23.1'
    server_address = ('', 10003)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)

    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def receive_game_controller_signal():
    """ ゲームコントローラの信号を受信し、状態をグローバル変数に格納する """
    global game_state
    buffer_size = 4096

    while not stop_event.is_set():
        try:
            data, _ = sock.recvfrom(buffer_size)
            referee_message = ssl_gc_referee_message_pb2.Referee()
            referee_message.ParseFromString(data)
            game_state = referee_message.command  # 最新のゲーム状態を更新
        except Exception as e:
            print("RefereeMessage デコードエラー:", e)

def track_ball_position(log_dir):
    """ ボールの位置を記録する """
    local = "127.0.0.1"
    multicast = "224.5.23.2"
    port = 10006
    buffer = 65536

    path = os.path.join("out", log_dir)
    os.makedirs(path, exist_ok=True)
    ballpojiPath = os.path.join(path, "ballpoji.csv")

    addr = ('', port)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(addr)
    udp.setsockopt(socket.IPPROTO_IP,
                   socket.IP_ADD_MEMBERSHIP,
                   socket.inet_aton(multicast) + socket.inet_aton(local))

    ball_position = []

    while not stop_event.is_set():
        try:
            packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data, _ = udp.recvfrom(buffer)
            packet.ParseFromString(data)

            frame = packet.detection
            if frame and game_state in Game_on:  # ゲームが進行中かチェック
                balls = frame.balls
                if balls:
                    ball = balls[0]
                    if frame.frame_number % 10 == 0:
                        balls_position = [int(ball.x), int(ball.y), game_state]
                        ball_position.append(balls_position)

                        # CSVに書き込み
                        df = pd.DataFrame(ball_position, columns=["x", "y", "state"])
                        df.to_csv(ballpojiPath, header=True, index=False)

                        if debug:
                            print("ball_position: ", balls_position)
        except Exception as e:
            print("ボール位置デコードエラー:", e)

    udp.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    log_dir = os.path.splitext(os.path.basename(sys.argv[1]))[0]  # 拡張子を除いたファイル名
    setup_socket()

    thread1 = threading.Thread(target=receive_game_controller_signal)
    thread2 = threading.Thread(target=track_ball_position, args=(log_dir,))

    thread1.start()
    thread2.start()

    try:
        thread1.join()
        thread2.join()
    except KeyboardInterrupt:
        stop_event.set()
        thread1.join()
        thread2.join()

    sock.close()
    print("ソケットを閉じました")