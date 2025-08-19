import os
import pandas as pd
import math
def track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug=False, sock=None): # ボール位置の追跡
    balls_position = [] # ボール位置を保存するリスト
    packet = receive_packet(udp) # パケットを受信
    frame = packet.detection # フレームを取得
    if debug:
        print("frame: ", frame) # デバッグ用にフレームを表示
    if frame:
        balls = frame.balls # ボールのリストを取得
        if balls:
            ball = balls[0] # 最初のボールを取得
            # sockを引数で受け取るか、グローバルから参照
            state = receive_game_controller_signal(sock, stop_event) # ゲームコントローラーの信号を受信
            balls_position.append([int(ball.x), int(ball.y), state,receive_packet(udp).detection.frame_number]) # ボール位置を保存
            return balls_position

def store_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug=False, sock=None): # ボール位置の保存
    while not stop_event.is_set(): # スレッドが停止されるまでループ
        try:
            ball_position = track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug,sock) # ボール位置を追跡
            ball_position_path = os.path.join(path, "ball_position.csv") # ボール位置のCSVファイルパス
            if not os.path.isdir(path):
                os.mkdir(path) # 出力先ディレクトリが存在しない場合は作成
            if ball_position:
                df = pd.DataFrame(ball_position, columns=["x", "y", "state","frame_number"]) # ボール位置のデータフレームを作成
                if not os.path.exists(ball_position_path):
                    df.to_csv(ball_position_path, mode='w', header=True, index=False) # ボール位置のCSVファイルが存在しない場合は新規作成
                else:
                    df.to_csv(ball_position_path, mode='a', header=False, index=False) # 存在する場合は追記
            if debug:
                print("ball_position: ", ball_position) # デバッグ用にボール位置を表示
                print("\n")
        except KeyboardInterrupt: # キーボード割り込みで終了
            break

def ball_velocity(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock): # ボール速度の計算
    ball_posi = [] # 過去のボール位置のリスト
    while not stop_event.is_set(): # スレッドが停止されるまでループ
        try:
            ball_position = track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug, sock) # ボール位置を追跡
            if ball_position:
                ball_posi.append(ball_position[0]) # ボール位置をball_posiに追加
                print("---------------------------------\n")
                print("ball_position[0]: ", ball_position[0]) # 最新のボール位置を表示
                print("---------------------------------\n")
                print("ball_posi[0]: ", ball_posi[0]) # ひとつ前のボール位置を表示
                
                if len(ball_posi) == 2: # 2つのボール位置がある場合
                    x1, y1, state1, frame1 = ball_posi[0] # ひとつ前のボール位置,状態,フレーム番号
                    x2, y2, state2, frame2 = ball_posi[1] # 最新のボール位置,状態,フレーム番号
                    dt = (frame2 - frame1) * (1/60) # フレーム間隔を秒に変換
                    vx = (x2 - x1) / dt # x方向の速度
                    vy = (y2 - y1) / dt # y方向の速度
                    speed = math.sqrt(vx ** 2 + vy ** 2) # ボールの速度
                    print("vx:", vx) # x方向の速度を表示
                    print("vy:", vy) # y方向の速度を表示
                    print("ball_velocity:", speed) # ボールの速度を表示

                    ball_posi[0] = ball_posi[1]  # 最新データを更新
                    ball_posi.pop(-1)  # 2つを超えたら古いものを削除
        except KeyboardInterrupt: # キーボード割り込みで終了
            break