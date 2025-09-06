
import socket
import struct
import messages_robocup_ssl_wrapper_pb2
import ssl_gc_referee_message_pb2
from ssl_gc_referee_message_pb2 import Referee
import os
import math
import threading
import pandas as pd

# グローバル変数 公開
game_time = 0.0
blue_possession_time = 0.0
yellow_possession_time = 0.0
holding_num = []
lock = threading.Lock()

# 定数
HOLDING_DISTANCE = 250 #ボールの直経 42.67mm
ROBOT_RADIUS = 180
POSSESSION_FILENAME = "possession.csv"
GAME_ON_COMMANDS = [2, 3, 4, 5, 8, 9]

         


def count_game_time(team_name, receive_game_controller_signal, sock, stop_event):
    global game_time, blue_possession_time, yellow_possession_time
    with lock:
        if receive_game_controller_signal(sock, stop_event) in GAME_ON_COMMANDS:
            if team_name == "b":
                blue_possession_time += 1.0
            if team_name == "y":
                yellow_possession_time += 1.0
            game_time += 1.0
        return [game_time, blue_possession_time, yellow_possession_time]

# 各チームの一番ボールに近いロボットを取得する関数

def possession(team_name, udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock):
    global holding_num
    """各チームの一番ボールに近いロボットを取得し、ボール保持判定を行う"""
    possession_path = os.path.join(path, POSSESSION_FILENAME)
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

    ball_to_robots_distance = []
    min_dist_robot_index = 0
    
    # データ取得
    # with lock:
    if True:
        packet = receive_packet(udp)
        frame = packet.detection
        ref_signal = receive_game_controller_signal(sock, stop_event)
        if ref_signal in GAME_ON_COMMANDS and frame:
            if team_name == "b":
                robots = frame.robots_blue
            elif team_name == "y":
                robots = frame.robots_yellow
            else:
                return None
            balls = frame.balls
            if balls and robots:
                ball = balls[0]
                for i, rob in enumerate(robots):
                    dist = (rob.x - ball.x) ** 2 + (rob.y - ball.y) ** 2
                    ball_to_robots_distance.append(dist)
                if ball_to_robots_distance:
                    min_dist_robot_index = ball_to_robots_distance.index(min(ball_to_robots_distance))
                    closest_robot = robots[min_dist_robot_index]
                    # ロボットの前方にボールがあるか判定
                    orientation = math.atan(closest_robot.orientation)
                    front_y = orientation * (ball.x - closest_robot.x) + closest_robot.y
                    if (front_y + ROBOT_RADIUS > ball.y) and (front_y - ROBOT_RADIUS < ball.y):
                        if min(ball_to_robots_distance) < HOLDING_DISTANCE ** 2:
                            print("hold:"+str(closest_robot.robot_id))
                            if not holding_num or holding_num[-1] == closest_robot.robot_id:
                                holding_num.append(closest_robot.robot_id)
                                # print(holding_num)
                            else:
                                # print(holding_num)
                                holding_num.clear()
                            
                            # 6回以上連続で保持していたら保持判定
                            if holding_num.count(closest_robot.robot_id) >= 6:
                                print(f"{team_name} holding: robot_id={closest_robot.robot_id}")
                                holding_num.clear()
                                return [min(ball_to_robots_distance), closest_robot, ball.x, ball.y, count_game_time(team_name, receive_game_controller_signal, sock, stop_event)]
        return None

#どちらがボールを占有しているかを判断する関数

def judge_possession(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock):
    """どちらがボールを占有しているかを判断し、CSVに記録"""
    possession_path = os.path.join(path, POSSESSION_FILENAME)
    columns = ["team_color", "dist", "robot_id", "robot_x", "robot_y", "ball_x", "ball_y", "time"]
    yellow = possession("y", udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock)
    blue = possession("b", udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock)
    row = None
    if blue and yellow:
        if blue[0] < yellow[0]:
            row = ["b", blue[0], blue[1].robot_id, blue[1].x, blue[1].y, blue[2], blue[3], blue[4]]
        else:
            row = ["y", yellow[0], yellow[1].robot_id, yellow[1].x, yellow[1].y, yellow[2], yellow[3], yellow[4]]
    elif blue:
        row = ["b", blue[0], blue[1].robot_id, blue[1].x, blue[1].y, blue[2], blue[3], blue[4]]
    elif yellow:
        row = ["y", yellow[0], yellow[1].robot_id, yellow[1].x, yellow[1].y, yellow[2], yellow[3], yellow[4]]
    if row:
        return row


def store_possesion(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock):
    possession_path = os.path.join(path, POSSESSION_FILENAME)
    # columns = ["team_color", "dist", "robot_id", "robot_x", "robot_y", "ball_x", "ball_y", "time"]
    
    while not stop_event.is_set():
        try:
            # break
            row=judge_possession(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock)    
            if(row):
                # df = pd.DataFrame([row], columns=columns)
                df = pd.DataFrame([row])
                df.to_csv(possession_path, mode='a', header=not os.path.exists(possession_path), index=False)
        except Exception as e: print(e)
        except KeyboardInterrupt:
            break