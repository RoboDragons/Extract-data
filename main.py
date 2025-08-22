import threading
from network import setup_socket, udp, receive_packet, receive_game_controller_signal
from ball import store_ball_position,track_ball_position,ball_velocity
from robot import store_robot_position,track_robot_position 
from goal import goal_scene
#プレフィックス省略のため from ファイル名 import メソッド名の形をとる。今後メソッドを追加した場合は追記すること。
import os

path = "out/" # 出力先ディレクトリ
stop_event = threading.Event() # スレッド停止用イベント
debug = False # デバッグ用フラグ

if __name__ == "__main__":
    sock = setup_socket() # ソケットのセットアップ
    thread_ball = threading.Thread( # ボール位置のスレッド
        target=store_ball_position, # ボール位置の保存
        args=(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock) # ボール位置のスレッド引数
    )

    thread_ballvelocity = threading.Thread( # ボール速度のスレッド
        target=ball_velocity, # ボール速度の保存
        args=(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock) # ボール速度のスレッド引数
    )

    # thread_robot = threading.Thread( # ロボット位置のスレッド
    #     target=store_robot_position, # ロボット位置の保存
    #     args=(udp, receive_packet, path, stop_event, debug) # ロボット位置のスレッド引数
    # )

    # thread_goal = threading.Thread( # ゴール位置のスレッド
    #     target=goal_scene, # ゴール位置の保存
    #     args=(track_ball_position, track_robot_position, path, stop_event, debug) # ゴール位置のスレッド引数
    # )

    # スレッドの開始
    # thread_goal.start()
    thread_ball.start()
    # thread_robot.start()
    thread_ballvelocity.start()

    try: # スレッド終了を待機
        thread_ball.join() 
        # thread_robot.join()
        # thread_goal.join()
        thread_ballvelocity.join()
    except KeyboardInterrupt:  # キーボード割り込みで終了
        stop_event.set() # スレッド停止イベントをセット
        thread_ball.join()
        # thread_robot.join()
        # thread_goal.join()
        thread_ballvelocity.join()
    udp.close()
    sock.close() 
    print("ソケットを閉じました")