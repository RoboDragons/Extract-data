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
robots_radius=800
holding_distance=15000
    

local = "127.0.0.1"
multicast = "224.5.23.2"
port = 10006
buffer = 65536
path = "out/"
addr = ('', port)
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp.bind(addr)
udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast) + socket.inet_aton(local))

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
    global udp
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
                            return balls_position
    
        except KeyboardInterrupt:
            break

def store_ball_position():
    while not stop_event.is_set():
        try:
            ball_position=track_ball_position()
            ballpojiPath = path + "ball_position.csv"
            if not os.path.isdir(path):
                os.mkdir(path)
            
            if ball_position:
                df = pd.DataFrame(ball_position, columns=["x", "y", "state"])
                df = df.sort_values("x")
                df.to_csv(ballpojiPath, header=True, index=False)

            if debug:
                print("ball_position: ", ball_position)
                print("\n")
        except KeyboardInterrupt:
            break

def count_game_time(name):
    global game_time, blue_possession_time, yellow_possession_time, count
    if receive_game_controller_signal() in Game_on:
        if name == "blue":
            blue_possession_time+=1.0
        elif name == "yellow":
            yellow_possession_time+=1.0 
        game_time+=1.0
        return [game_time, blue_possession_time, yellow_possession_time]

def possession(team_name):
    global game_time, blue_possession_time, yellow_possession_time, udp, path, possessionPath,robots_radius,holding_distance
    possessionPath = path + "possession.csv"
    if not os.path.isdir(path):
        os.mkdir(path)

    ball_to_robots_distance=[]    
    ball_to_robots_id=[]
    min_dist_robot_index=0
    holding_num=[]
    ball_holding_robot=[]
    
    while not stop_event.is_set():
        try:
            packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data, _ = udp.recvfrom(buffer)
            packet.ParseFromString(data)

            frame = packet.detection
            if receive_game_controller_signal() in Game_on:
                game_time+=1.0
                if frame:
                    #print("frame: ", frame)
                    if team_name == "blue":
                        robot = frame.robots_blue
                    elif team_name == "yellow":
                        robot = frame.robots_yellow
                    balls = frame.balls
                    #print(robots_blue)
                    if balls:
                        ball=balls[0]
                        if debug:
                            print("ball: ", int(ball.x))
                        if robot:
                            for i in range(len(robot)):
                                ball_to_robots_distance.append((robot[i].x-ball.x)**2+(robot[i].y-ball.y)**2)
                                ball_to_robots_id.append(robot[i].robot_id)
                            if ball_to_robots_distance:
                                min_dist_robot_index=ball_to_robots_distance.index(min(ball_to_robots_distance))
                            if 0 <= min_dist_robot_index < len(robot):
                                if math.atan(robot[min_dist_robot_index].orientation)*(ball.x-robot[min_dist_robot_index].x)+robot[min_dist_robot_index].y+robots_radius > ball.y and math.atan(robot[min_dist_robot_index].orientation)*(ball.x-robot[min_dist_robot_index].x)+robot[min_dist_robot_index].y-robots_radius < ball.y:
                                    if min(ball_to_robots_distance) < holding_distance*holding_distance :
                                        yellow_possession_time+=1.0
                                        holding_num.append(robot[min_dist_robot_index].robot_id)
                                        if holding_num.count(robot[min_dist_robot_index].robot_id) >=10:
                                            #print("yellow",min_dist_robot_index) if team_name=="yellow" else print("blue",min_dist_robot_index)
                                            ball_holding_robot.append([min(ball_to_robots_distance), robot[min_dist_robot_index], balls[0].x, balls[0].y, count_game_time("yellow")])
                                            holding_num.clear()
                                            return [min(ball_to_robots_distance), robot[min_dist_robot_index], balls[0].x, balls[0].y, count_game_time("yellow")]
                        min_dist_robot_index=-1
                        ball_to_robots_distance.clear()
                        ball_to_robots_id.clear()
        except KeyboardInterrupt:
            break

def judge_possesion():
    holding_data=[]
    while not stop_event.is_set():
        try:
            if receive_game_controller_signal() in Game_on:
                blue=possession("blue")
                yellow=possession("yellow")
                if blue and yellow:
                    if blue[0] < yellow[0]:
                        holding_data.append(blue)
                        print("holding",holding_data)
                        df=pd.DataFrame(holding_data,columns=["dist","robot_data","ball_x","ball_y","time"])
                        df.to_csv(possessionPath,header=True,index=False)
                    else:
                        holding_data.append(yellow)
                        print("holding",holding_data)
                        df=pd.DataFrame(holding_data,columns=["dist","robot_data","ball_x","ball_y","time"])
                        df.to_csv(possessionPath,header=True,index=False)
        except KeyboardInterrupt:
            break
    return 0    

if __name__ == "__main__":
    setup_socket()
    # スレッドを作成して、両方の関数を並行して実行
    thread1 = threading.Thread(target=receive_game_controller_signal)
    thread2 = threading.Thread(target=track_ball_position)
    thread3 = threading.Thread(target=judge_possesion)

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

    udp.close()
    sock.close()
    print("ソケットを閉じました")