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
lock = threading.Lock()
robots_yellow = []
robots_blue = []
poji_goal_x=5990
poji_goal_y=900
nega_goal_x=-5990
nega_goal_y=-900


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

packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()

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

def receive_packet():
    data, _ = udp.recvfrom(buffer)
    packet.ParseFromString(data)
    return packet
    
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
    balls_position = []
    # packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
    # data, _ = udp.recvfrom(buffer)
    # packet.ParseFromString(data)
    packet= receive_packet()
    frame = packet.detection
    if debug:
        print("frame: ", frame)
    if frame:
        balls = frame.balls  
        if balls:        
            ball = balls[0]
            balls_position.append([int(ball.x) , int(ball.y), receive_game_controller_signal()])
                    #print("ball_position: ", balls_position)
            return balls_position

def store_ball_position():
    while not stop_event.is_set():
        try:
            ball_position=track_ball_position()
            ballpojiPath = path + "ball_position.csv"
            if not os.path.isdir(path):
                os.mkdir(path)
            
            if ball_position:
                df = pd.DataFrame(ball_position, columns=["x", "y", "state"])
                if not os.path.exists(ballpojiPath):
                    df.to_csv(ballpojiPath, mode='w', header=True, index=False)
                else:
                    df.to_csv(ballpojiPath, mode='a', header=False, index=False)

            if debug:
                print("ball_position: ", ball_position)
                print("\n")
        except KeyboardInterrupt:
            break

def track_robot_position():
    if not os.path.isdir(path):
        os.mkdir(path)
    packet = receive_packet()
    robots_yellow = packet.detection.robots_yellow
    robots_blue = packet.detection.robots_blue
    robot_positions = {"yellow": {}, "blue": {}}
    if robots_yellow:
        for yellow_robot in robots_yellow:
            if 0 <= yellow_robot.robot_id < 17:
                robot_positions["yellow"][yellow_robot.robot_id] = (int(yellow_robot.x), int(yellow_robot.y))
    if robots_blue:
        for blue_robot in robots_blue:
            if 0 <= blue_robot.robot_id < 17:
                robot_positions["blue"][blue_robot.robot_id] = (int(yellow_robot.x), int(yellow_robot.y))
    return robot_positions

def store_robot_position():
    robot_locate = []
    while not stop_event.is_set():
        try:
            positions = track_robot_position()
            if positions:
                # 1フレーム分のデータを1行にまとめる
                row = {}
                for color in ["yellow", "blue"]:
                    for robot_id, (x, y) in positions[color].items():
                        row[f"{color}_{robot_id}_x"] = x
                        row[f"{color}_{robot_id}_y"] = y
                robot_locate.append(row)

                # 保存処理（例：10フレームごとに保存）
                if len(robot_locate) >= 10:
                    robotPath = os.path.join(path, "robot_position.csv")
                    df = pd.DataFrame(robot_locate)
                    if not os.path.exists(robotPath):
                        df.to_csv(robotPath, mode='w', header=True, index=False)
                    else:
                        df.to_csv(robotPath, mode='a', header=False, index=False)
                    robot_locate.clear()
                if debug:
                    print(f"robot_locate (バッファ内): {len(robot_locate)}")
        except KeyboardInterrupt:
            break
                
def goal_scene():
    robot_poji_goal_path = path + "robot_position_goal.csv"
    robot_position_path = path + "robot_position.csv"
    if not os.path.isdir(path):
        os.mkdir(path)
    while not stop_event.is_set():
        try:
            
            balls_position = track_ball_position()
            robot_poji = track_robot_position()
            if balls_position and robot_poji:
                ball_x, ball_y, state = balls_position[-1]
                #print([len(v) for v in robot_poji])
                columns_ = [f"{int(i/2)}{'blue_' if i >= 34 else 'yellow_'}{'x' if i % 2 == 0 else 'y'}" for i in range(len(robot_poji))]
                # if -900<ball_y<900:
                #     print("goal_y",ball_y)
                #     print("goal_x",ball_x)
                if ball_x > 6000:
                    if robot_poji and ((ball_x > poji_goal_x and (ball_y < poji_goal_y and ball_y > nega_goal_y)) or (ball_x < nega_goal_x and (ball_y < poji_goal_y and ball_y > nega_goal_y))):
                        print("poji_goal", (ball_x > poji_goal_x and (ball_y < poji_goal_y and ball_y > nega_goal_y)))
                        print("nega_goal", (ball_x < nega_goal_x and (ball_y < poji_goal_y and ball_y > nega_goal_y)))
                        
                        # robot_position.csvの末尾から20フレーム分のデータを取得
                        # if os.path.exists(robot_position_path):
                        df_robot_position = pd.read_csv(robot_position_path)
                        last_20_frames = df_robot_position.tail(120)
                        print("Last 20 frames of robot position:")
                        print(last_20_frames)
                        
                        df = pd.DataFrame(last_20_frames, columns=columns_)
                        df.to_csv(robot_poji_goal_path, header=True, index=False)
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
            frame = packet.detection
            if receive_game_controller_signal() in Game_on:
                game_time+=1.0
                if frame:
                    #print("frame: ", frame)
                    if team_name == "b":
                        robot = frame.robots_blue
                    elif team_name == "y":
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
    while not stop_event.is_set():
        try:
            if receive_game_controller_signal() in Game_on:
                yellow = possession("y")
                blue = possession("b")

                if blue and yellow:
                    if blue[0] < yellow[0]:  # どちらがボールを保持しているか判定
                        holding_data.append([blue[0], blue[1].robot_id, blue[1].x, blue[1].y, blue[2], blue[3], blue[4]])
                    else:
                        holding_data.append([yellow[0], yellow[1].robot_id, yellow[1].x, yellow[1].y, yellow[2], yellow[3], yellow[4]])
                    # データを CSV に保存
                if holding_data:
                    df = pd.DataFrame(holding_data, columns=["dist", "robot_id", "robot_x", "robot_y", "ball_x", "ball_y", "time"])
                    df.to_csv(possessionPath, header=True, index=False)
                    # デバッグ出力
                    #print("holding data:", holding_data[-1])  # 最新のデータのみ表示
        except KeyboardInterrupt:
            break
#       except Exception as e:
#            print("Error: ", e)
            #print("blue",blue[1],blue[2],blue[3],blue[4])
    return 0               
if __name__ == "__main__":
    setup_socket()
    # スレッドを作成して、両方の関数を並行して実行
    thread1 = threading.Thread(target=receive_game_controller_signal)
    thread2 = threading.Thread(target=store_ball_position)
    thread3 = threading.Thread(target=judge_possesion)
    thread4 = threading.Thread(target=store_robot_position)
    thread5 = threading.Thread(target=goal_scene)
    thread6 = threading.Thread(target=receive_packet)

    thread6.start()
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()


    try:
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()
        thread6.join()
    except KeyboardInterrupt:
        stop_event.set()
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()
        thread6.join()

    udp.close()
    sock.close()
    print("ソケットを閉じました")