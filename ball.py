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

def ball_velocity(udp,receive_packet,ball_position):
    if len(ball_position) < 2:
        return 0, 0
    x1, y1 = ball_position[-2][:2]
    x2, y2 = ball_position[-1][:2]
    vx = (x2 - x1) / 0.033  # Assuming a frame rate of 30 FPS
    vy = (y2 - y1) / 0.033
    
    return vx, vy