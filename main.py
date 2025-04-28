import threading
from network import setup_socket, udp, receive_packet, receive_game_controller_signal
from ball import store_ball_position
from robot import store_robot_position
from goal import goal_scene
import os

path = "out/"
stop_event = threading.Event()
debug = False

if __name__ == "__main__":
    sock = setup_socket()
    # main.py など
    thread_ball = threading.Thread(
        target=store_ball_position,
        args=(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock)
    )
    thread_robot = threading.Thread(target=store_robot_position, args=(udp, receive_packet, path, stop_event, debug))
    thread_goal = threading.Thread(target=goal_scene, args=(track_ball_position, track_robot_position, path, poji_goal_x, poji_goal_y, nega_goal_x, nega_goal_y, stop_event, debug))
    
    thread_goal.start()
    thread_ball.start()
    thread_robot.start()

    try:
        thread_ball.join()
        thread_robot.join()
        thread_goal.join()
    except KeyboardInterrupt:
        stop_event.set()
        thread_ball.join()
        thread_robot.join()
        thread_goal.join()
    udp.close()
    sock.close()
    print("ソケットを閉じました")