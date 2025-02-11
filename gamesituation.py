import threading
import socket
import struct
import os
import numpy as np
import pandas as pd
import time
import messages_robocup_ssl_wrapper_pb2
import ssl_gc_state_pb2
import ssl_gc_engine_pb2
import ssl_gc_referee_message_pb2
import math

debug = False
STATE_LIST = []
State_num = 0
count = 0
sock = None
Game_on = [2, 3, 4, 5, 8, 9]
stop_event = threading.Event()
game_time=0.0
blue_possession_time=0.0
yellow_possession_time=0.0

def setup_socket():
    global sock
    buffer_size = 4096  # バッファサイズ データの受け取るお皿の大きさ
    multicast_group = '224.5.23.1'
    server_address = ('', 10003)  # GCのアドレス データが送られてくる元の

    # ソケットの作成 SOCK_DGRAMはUDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ソケットにオプションを設定し、マルチキャストグループに参加
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)

    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def receive_game_controller_signal():
    global sock
    buffer_size = 4096  # バッファサイズ データの受け取るお皿の大きさ

    try:
        while not stop_event.is_set():
            data, address = sock.recvfrom(buffer_size)  # データ受信
            if debug:
                print("データを受信しました from", address)
                print("受信データ (バイナリ):", data)  # 受信データをバイナリ形式で表示

            try:
                # RefereeMessageのデコード
                referee_message = ssl_gc_referee_message_pb2.Referee()
                referee_message.ParseFromString(data)
                if debug:
                    print("Referee Message (人間が読みやすい形式):")

                #print(referee_message.Command.Name(referee_message.command))
                return referee_message.command
            except Exception as e:
                print("RefereeMessage デコードエラー:", e)
                print("----------------------")

    except KeyboardInterrupt:
        print("終了処理を開始します...")

def track_ball_position():
    local = "127.0.0.1"
    multicast = "224.5.23.2"
    port = 10006
    buffer = 65536

    path = "out/"
    ballpojiPath = path + "ballpoji.csv"

    addr = ('', port)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(addr)
    udp.setsockopt(socket.IPPROTO_IP,
                   socket.IP_ADD_MEMBERSHIP,
                   socket.inet_aton(multicast) + socket.inet_aton(local))

    ball_position = []

    if not os.path.isdir(path):
        os.mkdir(path)

    while not stop_event.is_set():
        try:
            packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data, _ = udp.recvfrom(buffer)
            packet.ParseFromString(data)

            frame = packet.detection
            if debug:
                print("frame: ", frame)
            if frame:
                balls = frame.balls
                if balls:
                    ball = balls[0]
                    
                    if receive_game_controller_signal() in Game_on:
                        #print("here")
                        if frame.frame_number % 10 == 0:
                            balls_position = [int(ball.x) / 10, int(ball.y) / 10, receive_game_controller_signal()]
                            ball_position.append(balls_position)
                            df = pd.DataFrame(ball_position, columns=["x", "y", "state"])
                            df = df.sort_values("x")
                            df.to_csv(ballpojiPath, header=True, index=False)

                        if debug:
                            print("ball_position: ", ball_position)
                            print("\n")
        except KeyboardInterrupt:
            break

    udp.close()

def possession():
    global game_time, blue_possession_time, yellow_possession_time  # グローバル変数として宣言
    local = "127.0.0.1"
    multicast = "224.5.23.2"
    port = 10006
    buffer = 65536

    path = "out/"
    possessionPath = path + "possession.csv"

    addr = ('', port)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(addr)
    udp.setsockopt(socket.IPPROTO_IP,
                   socket.IP_ADD_MEMBERSHIP,
                   socket.inet_aton(multicast) + socket.inet_aton(local))

    if not os.path.isdir(path):
        os.mkdir(path)


    ball_to_bluerobots_distance=[]
    ball_to_yellowrobots_distance=[]    
    ball_to_bluerobots_id=[]
    ball_to_yellowrobots_id=[]
    min_dist_blue_robot_index=0
    min_dist_yellow_robot_index=0
    ball_holding_robot=[]
    
    robots_radius=80
    holding_distance=50
    
    
    
    while not stop_event.is_set():
        try:
            packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data, _ = udp.recvfrom(buffer)
            packet.ParseFromString(data)

            frame = packet.detection
            if receive_game_controller_signal() in Game_on:
                game_time+=0.1
                if frame:
                    #print("frame: ", frame)
                    robots_blue = frame.robots_blue
                    robots_yellow = frame.robots_yellow
                    balls = frame.balls
                    #print(robots_blue)
                    if balls:
                        ball=balls[0]
                        if debug:
                            print("ball: ", int(ball.x))
                        if robots_blue:
                            for i in range(len(robots_blue)):
                                ball_to_bluerobots_distance.append((robots_blue[i].x-ball.x)**2+(robots_blue[i].y-ball.y)**2)
                                ball_to_bluerobots_id.append(robots_blue[i].robot_id)
                            if ball_to_bluerobots_distance:
                                min_dist_blue_robot_index=ball_to_bluerobots_distance.index(min(ball_to_bluerobots_distance))
                                
                            if 0 <= min_dist_blue_robot_index < len(robots_blue):
                                if math.atan(robots_blue[min_dist_blue_robot_index].orientation)*(ball.x-robots_blue[min_dist_blue_robot_index].x)+robots_blue[min_dist_blue_robot_index].y+robots_radius > ball.y and math.atan(robots_blue[min_dist_blue_robot_index].orientation)*(ball.x-robots_blue[min_dist_blue_robot_index].x)+robots_blue[min_dist_blue_robot_index].y-robots_radius < ball.y:
                                    if min(ball_to_bluerobots_distance) < holding_distance:
                                        blue_possession_time+=0.1
                                        print("blue",min_dist_blue_robot_index)
                                        ball_holding_robot.append([robots_blue[min_dist_blue_robot_index].robot_id,blue_possession_time,yellow_possession_time,game_time])
                            min_dist_blue_robot_index=0
                            ball_to_bluerobots_distance=[0]*len(robots_blue)
                            ball_to_bluerobots_id=[0]*len(robots_blue)
                        if robots_yellow:
                            for i in range(len(robots_yellow)):
                                ball_to_yellowrobots_distance.append((robots_yellow[i].x-ball.x)**2+(robots_yellow[i].y-ball.y)**2)
                                ball_to_yellowrobots_id.append(robots_yellow[i].robot_id)
                            if ball_to_yellowrobots_distance:
                                min_dist_yellow_robot_index=ball_to_yellowrobots_distance.index(min(ball_to_yellowrobots_distance))
                                
                            if 0 <= min_dist_yellow_robot_index < len(robots_yellow):
                                if math.atan(robots_yellow[min_dist_yellow_robot_index].orientation)*(ball.x-robots_yellow[min_dist_yellow_robot_index].x)+robots_yellow[min_dist_yellow_robot_index].y+robots_radius > ball.y and math.atan(robots_yellow[min_dist_yellow_robot_index].orientation)*(ball.x-robots_yellow[min_dist_yellow_robot_index].x)+robots_yellow[min_dist_yellow_robot_index].y-robots_radius < ball.y:
                                    if min(ball_to_yellowrobots_distance) < holding_distance:
                                        yellow_possession_time+=0.1
                                        print("yellow",min_dist_yellow_robot_index)
                                        ball_holding_robot.append([robots_yellow[min_dist_yellow_robot_index].robot_id,blue_possession_time,yellow_possession_time,game_time])
                            min_dist_yellow_robot_index=0
                            ball_to_yellowrobots_distance=[1000]*len(robots_yellow)
                            ball_to_yellowrobots_id=[0]*len(robots_yellow)
                    
                                            
                df = pd.DataFrame(ball_holding_robot, columns=["robot_id", "blue_possession_time", "yellow_possession_time", "game_time"])
                df = df.sort_values("game_time")
                df.to_csv(possessionPath, header=True, index=False)
        except KeyboardInterrupt:
            break
        except Exception as e:
                print("RefereeMessage デコードエラー:", e)
                print("b=",min_dist_blue_robot_index)
                print("y=",min_dist_yellow_robot_index)

    udp.close()

if __name__ == "__main__":
    setup_socket()
    # スレッドを作成して、両方の関数を並行して実行
    thread1 = threading.Thread(target=receive_game_controller_signal)
    thread2 = threading.Thread(target=track_ball_position)
    thread3 = threading.Thread(target=possession)

    thread1.start()
    thread2.start()
    thread3.start()

    try:
        thread1.join()
        thread2.join()
        thread3.join()
    except KeyboardInterrupt:
        stop_event.set()
        thread1.join()
        thread2.join()
        thread3.join()

    sock.close()
    print("ソケットを閉じました")