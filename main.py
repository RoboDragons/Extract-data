import threading
from network import setup_socket, udp, receive_packet, receive_game_controller_signal
from ball import store_ball_position,track_ball_position,ball_velocity
from robot import store_robot_position,track_robot_position 
from goal import goal_scene
from posssession import count_game_time, possession, store_possesion 
from count_pass import count_passes
# from posssession import possession,judge_possession,save_data_to_csv
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
    thread_ballvelocity = threading.Thread(target=ball_velocity, args=(udp, receive_packet,receive_game_controller_signal, stop_event, path, debug, sock))
    thread_robot = threading.Thread(target=store_robot_position, args=(udp, receive_packet, path, stop_event, debug))
     # thread_goal = threading.Thread(target=goal_scene, args=(track_ball_position, track_robot_position, path, stop_event, debug))
    thread_possession= threading.Thread(target=store_possesion, args=(udp, receive_packet,receive_game_controller_signal, stop_event, path, debug, sock))
     # thread_goal.start()
    thread_pass = threading.Thread(
        target=count_passes,
        args=(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock)
    )
     
    thread_ball.start()
    thread_robot.start()
    thread_ballvelocity.start()
    thread_possession.start()
    thread_pass.start()

    try:
        thread_ball.join()
        thread_robot.join()
         # thread_goal.join()
        thread_ballvelocity.join()
        thread_possession.join()
        thread_pass.join()
    except KeyboardInterrupt:
        stop_event.set()
        thread_ball.join()
        thread_robot.join()
         # thread_goal.join()
        thread_ballvelocity.join()
        thread_pass.join()
    udp.close()
    sock.close()
    print("ソケットを閉じました")