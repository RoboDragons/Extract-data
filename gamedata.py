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
Game_on = [2, 3, 4, 5, 8, 9]
stop_event = threading.Event()
game_time=0.0
blue_possession_time=0.0
yellow_possession_time=0.0
robots_radius=800
holding_distance=15000
lock = threading.Lock()

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
    buffer_size = 4096
    try:
        data, address = sock.recvfrom(buffer_size)  # データ受信
        if debug:
            print("データを受信しました from", address)
            print("受信データ (バイナリ):", data)  # 受信データをバイナリ形式で表示

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
                        if frame.frame_number % 10 == 0:
                            balls_position = [int(ball.x) / 10, int(ball.y) / 10, receive_game_controller_signal()]
                            return balls_position
    
        except KeyboardInterrupt:
            break

def store_ball_position():
    ballpojiPath = path + "ball_position.csv"
    if not os.path.isdir(path):
        os.mkdir(path)
        
    while not stop_event.is_set():
        try:
            ball_position=track_ball_position()    
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
    with lock:
        if receive_game_controller_signal() in Game_on:
            if name == "b":
                blue_possession_time+=1.0
            elif name == "y":
                yellow_possession_time+=1.0 
            game_time+=1.0

def possession(team_name):
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
            if frame and receive_game_controller_signal() in Game_on:
                #print("frame: ", frame)
                if team_name == "b":
                    robot = frame.robots_blue
                elif team_name == "y":
                    robot = frame.robots_yellow
                balls = frame.balls
                #print(robots_blue)
                if debug:
                    print("ball: ", int(ball.x))
                if robot and balls:
                    ball=balls[0]
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
                                    ball_holding_robot.append([min(ball_to_robots_distance), robot[min_dist_robot_index], balls[0].x, balls[0].y, count_game_time(team_name)])
                                    holding_num.clear()
                                    return [min(ball_to_robots_distance), robot[min_dist_robot_index], balls[0].x, balls[0].y, count_game_time(team_name)]
                min_dist_robot_index=-1
                ball_to_robots_distance.clear()
                ball_to_robots_id.clear()
        except KeyboardInterrupt:
            break

def judge_possesion():
    holding_data=[]
    possessionPath = os.path.join(path, "possession.csv")
    os.makedirs(path, exist_ok=True)
    
    while not stop_event.is_set():
        try:
            if receive_game_controller_signal() in Game_on:
                yellow = possession("y")
                blue = possession("b")

                if blue and yellow:
                    if blue[0] < yellow[0]:  # どちらがボールを保持しているか判定
                        holding_data.append(["blue",blue[0], blue[1].robot_id, blue[1].x, blue[1].y, blue[2], blue[3], blue[4]])
                        return ("blue")
                    else:
                        holding_data.append(["yellow",yellow[0], yellow[1].robot_id, yellow[1].x, yellow[1].y, yellow[2], yellow[3], yellow[4]])
                        return("yellow")
                    # データを CSV に保存
                if holding_data:
                    df = pd.DataFrame(holding_data, columns=["dist", "robot_id", "robot_x", "robot_y", "ball_x", "ball_y", "time"])
                    df.to_csv(possessionPath, header=True, index=False)
                    # デバッグ出力
                    #print("holding data:", holding_data[-1])  # 最新のデータのみ表示
        except KeyboardInterrupt:
            print("here_judgepossession")
            break
#       except Exception as e:
#            print("Error: ", e)
            #print("blue",blue[1],blue[2],blue[3],blue[4])


def count_pass():
    """ パス回数をカウント """
    passPath = os.path.join(path, "pass.csv")
    os.makedirs(path, exist_ok=True)

    pass_data = []
    count_pass_num = {"blue": 0, "yellow": 0}

    while not stop_event.is_set():
        team = judge_possesion()
        if team:
            pass_data.append(team)

        if len(pass_data) > 3:
            pass_data.clear()

        if len(pass_data) == 2 and pass_data[0] == pass_data[1]:
            count_pass_num[team] += 1

        df = pd.DataFrame(count_pass_num.items(), columns=["team", "pass_num"])
        df.to_csv(passPath, mode='w', header=True, index=False)
    
if __name__ == "__main__":
    setup_socket()
    threads = [
        threading.Thread(target=store_ball_position),
        threading.Thread(target=judge_possesion),
        threading.Thread(target=count_pass),
    ]

    for thread in threads:
        thread.start()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        stop_event.set()
        for thread in threads:
            thread.join()

    udp.close()
    sock.close()
    print("ソケットを閉じました")