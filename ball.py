import os
import pandas as pd

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
            balls_position.append([int(ball.x), int(ball.y), state])
            return balls_position
def store_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug=False, sock=None):
    while not stop_event.is_set():
        try:
            ball_position = track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug,sock)
            ballpojiPath = os.path.join(path, "ball_position.csv")
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