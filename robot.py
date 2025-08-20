import os
import pandas as pd

def track_robot_position(udp, receive_packet, path): # ロボットの位置を追跡
    if not os.path.isdir(path):
        os.mkdir(path) # ディレクトリが存在しない場合は作成
    packet = receive_packet(udp) # パケットを受信
    robots_yellow = packet.detection.robots_yellow # 黄色ロボットの情報
    robots_blue = packet.detection.robots_blue # 青色ロボットの情報
    robot_positions = {"yellow": {}, "blue": {}} # ロボットの位置を格納する辞書
    if robots_yellow:
        for yellow_robot in robots_yellow: # 黄色ロボットの数だけループ
            if 0 <= yellow_robot.robot_id < 17: # ロボットIDが有効な範囲内かチェック
                robot_positions["yellow"][yellow_robot.robot_id] = (int(yellow_robot.x), int(yellow_robot.y)) # 黄色ロボットの位置を格納
    if robots_blue:
        for blue_robot in robots_blue: # 青色ロボットの数だけループ
            if 0 <= blue_robot.robot_id < 17: # ロボットIDが有効な範囲内かチェック
                robot_positions["blue"][blue_robot.robot_id] = (int(blue_robot.x), int(blue_robot.y)) # 青色ロボットの位置を格納
    return robot_positions

def store_robot_position(udp, receive_packet, path, stop_event, debug=False): # ロボットの位置を保存
    robot_locate = [] # ロボットの位置を格納するリスト
    while not stop_event.is_set(): # スレッドが停止されるまでループ
        try:
            positions = track_robot_position(udp, receive_packet, path) # ロボットの位置を追跡
            if positions:
                row = {} # 各フレームのロボットの位置を格納する辞書
                for color in ["yellow", "blue"]: # チームカラーでループ
                    for robot_id, (x, y) in positions[color].items(): # それぞれの色のロボットを１台ずつ取り出し、IDと位置を取得
                        row[f"{color}_{robot_id}_x"] = x # X座標を格納
                        row[f"{color}_{robot_id}_y"] = y # Y座標を格納
                robot_locate.append(row) # 各フレームのロボットの位置を格納
                if len(robot_locate) >= 10: # バッファが10フレームに達したら保存
                    robotPath = os.path.join(path, "robot_position.csv") # ロボットの位置を保存するCSVファイルのパス
                    df = pd.DataFrame(robot_locate) # データフレームに変換
                    write_header = not os.path.exists(robotPath) or os.path.getsize(robotPath) == 0 # ヘッダーを書き込むかどうか
                    df.to_csv(robotPath, mode='a', header=write_header, index=False) # CSVファイルに追記
                    robot_locate.clear() # バッファをクリア
                if debug:
                    print(f"robot_locate (バッファ内): {len(robot_locate)}") # デバッグ用にバッファ内のロボット位置データの数を表示
        except KeyboardInterrupt: # キーボード割り込みで終了
            break