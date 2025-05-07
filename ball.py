import os
import pandas as pd
import math
def track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug=False, sock=None):
    balls_position = []
    packet = receive_packet(udp)
    frame = packet.detection
    if debug:
        print("frame: ", frame)
    if frame:
        balls = frame.balls
        if balls:
            ball = balls[0]
            # sockを引数で受け取るか、グローバルから参照
            state = receive_game_controller_signal(sock, stop_event)
            balls_position.append([int(ball.x), int(ball.y), state,receive_packet(udp).detection.frame_number])
            return balls_position

def store_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug=False, sock=None):
    while not stop_event.is_set():
        try:
            ball_position = track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug,sock)
            ballpojiPath = os.path.join(path, "ball_position.csv")
            if not os.path.isdir(path):
                os.mkdir(path)
            if ball_position:
                df = pd.DataFrame(ball_position, columns=["x", "y", "state","frame_number"])
                if not os.path.exists(ballpojiPath):
                    df.to_csv(ballpojiPath, mode='w', header=True, index=False)
                else:
                    df.to_csv(ballpojiPath, mode='a', header=False, index=False)
            if debug:
                print("ball_position: ", ball_position)
                print("\n")
        except KeyboardInterrupt:
            break

def ball_velocity(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock):
    ball_posi = []
    while not stop_event.is_set():
        try:
            
            ball_position = track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug, sock)
            if ball_position:
                ball_posi.append(ball_position[0])  # 最新データを追加
                # print("ball_position: ", ball_position)
                print("---------------------------------\n")
                print("ball_position[0]: ", ball_position[0])
                print("---------------------------------\n")
                # print("ball_posi: ", ball_posi)
                print("---------------------------------\n")
                print("ball_posi[0]: ", ball_posi[0])
                if len(ball_posi) == 2:
                    x1, y1, state1, frame1 = ball_posi[0]
                    x2, y2, state2, frame2 = ball_posi[1]
                    dt = (frame2 - frame1) * (1/60)
                    vx = (x2 - x1) / dt
                    vy = (y2 - y1) / dt
                    speed = math.sqrt(vx ** 2 + vy ** 2) 
                    print("vx:", vx)
                    print("vy:", vy)
                    print("ball_velocity:", speed)

                    ball_posi[0] = ball_posi[1]  # 最新データを更新
                    ball_posi.pop(-1)  # 2つを超えたら古いものを削除
        except KeyboardInterrupt:
            break