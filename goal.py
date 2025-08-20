import os
import pandas as pd

def goal_scene(track_ball_position, track_robot_position, path, stop_event, debug=False): # ゴールシーンの抽出
    robot_poji_goal_path = os.path.join(path, "robot_position_goal.csv") # ロボットのポジションがゴールの時のCSVファイルパス
    robot_position_path = os.path.join(path, "robot_position.csv") # ロボットのポジションのCSVファイルパス
    poji_goal_x=6000 # 右側ゴールのX座標
    nega_goal_x=-6000 # 左側ゴールのX座標
    poji_goal_y=600 # 右側ゴールのY座標
    nega_goal_y=600 # 左側ゴールのY座標
    if not os.path.isdir(path):
        os.mkdir(path) # ディレクトリが存在しない場合は作成
    while not stop_event.is_set(): # スレッドが停止されるまでループ
        try:
            balls_position = track_ball_position() # ボールの位置を追跡
            robot_poji = track_robot_position() # ロボットの位置を追跡
            if balls_position and robot_poji: 
                ball_x, ball_y, state = balls_position[-1] # ボールの位置の最後の要素を取得
                if ball_x > 6000:
                    if robot_poji and ((ball_x > poji_goal_x and (poji_goal_y > ball_y > nega_goal_y)) or (ball_x < nega_goal_x and (poji_goal_y > ball_y > nega_goal_y))): # ゴールシーンの条件
                        df_robot_position = pd.read_csv(robot_position_path) # ロボットのポジションのCSVファイルを読み込み
                        last_20_frames = df_robot_position.tail(120) # 最後の120フレームを取得
                        df = pd.DataFrame(last_20_frames) # DataFrameを作成
                        df.to_csv(robot_poji_goal_path, header=True, index=False) # ゴールシーンのCSVファイルを保存
                        if debug:
                            print("ゴールシーンを保存しました") # デバッグ用にゴールシーンを保存したことを表示
        except KeyboardInterrupt: # キーボード割り込みが発生した場合
            break