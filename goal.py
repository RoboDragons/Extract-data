import os
import pandas as pd
import math

def determine_attacking_team(robot_positions, goal_side):
    """
    ゴール側に近いロボットのチームカラーを判定
    goal_side: 'right' (x>0) or 'left' (x<0)
    """
    team_distances = {'yellow': [], 'blue': []}
    
    for color in ['yellow', 'blue']:
        if color in robot_positions:
            for robot_id, (x, y) in robot_positions[color].items():
                if goal_side == 'right':
                    # 右ゴールへの距離
                    distance = abs(x - 6000)
                else:
                    # 左ゴールへの距離  
                    distance = abs(x - (-6000))
                team_distances[color].append(distance)
    
    # 各チームの平均距離を計算
    avg_distances = {}
    for color, distances in team_distances.items():
        if distances:
            avg_distances[color] = sum(distances) / len(distances)
        else:
            avg_distances[color] = float('inf')
    
    # より近いチームを攻撃チームとして返す
    if avg_distances['yellow'] < avg_distances['blue']:
        return 'yellow'
    else:
        return 'blue'

def calculate_ball_angle(ball_velocity_data):
    """
    ボールの速度データから角度を計算
    """
    if len(ball_velocity_data) >= 2:
        x1, y1, _, _ = ball_velocity_data[0]
        x2, y2, _, _ = ball_velocity_data[1]
        vx = x2 - x1
        vy = y2 - y1
        if vx != 0 or vy != 0:
            angle = math.atan2(vy, vx) * 180 / math.pi  # 度単位
            return angle, math.sqrt(vx**2 + vy**2)
    return None, None

def goal_scene(udp, receive_packet, receive_game_controller_signal, stop_event, path, debug, sock):
    # 左右ゴール用の別々のファイルパス
    left_goal_path = os.path.join(path, "robot_position_left_goal.csv")
    right_goal_path = os.path.join(path, "robot_position_right_goal.csv")
    robot_position_path = os.path.join(path, "robot_position.csv")
    
    # ゴール座標の定義
    right_goal_x = 6000   # 右ゴール
    left_goal_x = -6000   # 左ゴール
    goal_y_max = 600      # ゴールのY座標上限
    goal_y_min = -600     # ゴールのY座標下限
    
    # ボール速度追跡用
    ball_velocity_data = []
    
    if not os.path.isdir(path):
        os.mkdir(path)
        
    while not stop_event.is_set():
        try:
            # Import the tracking functions here to use them properly
            from ball import track_ball_position
            from robot import track_robot_position
            
            balls_position = track_ball_position(udp, receive_packet, receive_game_controller_signal, stop_event, debug, sock)
            robot_poji = track_robot_position(udp, receive_packet, path)
            
            if balls_position and robot_poji:
                ball_x, ball_y, state = balls_position[-1]
                
                # ボール速度データを更新
                ball_velocity_data.append((ball_x, ball_y, state, len(ball_velocity_data)))
                if len(ball_velocity_data) > 2:
                    ball_velocity_data.pop(0)
                
                # 右ゴールの判定
                if ball_x > right_goal_x and goal_y_min < ball_y < goal_y_max:
                    attacking_team = determine_attacking_team(robot_poji, 'right')
                    angle, speed = calculate_ball_angle(ball_velocity_data)
                    
                    if os.path.exists(robot_position_path):
                        df_robot_position = pd.read_csv(robot_position_path)
                        last_20_frames = df_robot_position.tail(120)
                        
                        # チーム情報と角度情報を追加
                        goal_data = last_20_frames.copy()
                        goal_data['attacking_team'] = attacking_team
                        goal_data['goal_side'] = 'right'
                        goal_data['ball_angle'] = angle if angle is not None else 0
                        goal_data['ball_speed'] = speed if speed is not None else 0
                        goal_data['ball_x'] = ball_x
                        goal_data['ball_y'] = ball_y
                        
                        # ヘッダー付きで保存
                        write_header = not os.path.exists(right_goal_path) or os.path.getsize(right_goal_path) == 0
                        goal_data.to_csv(right_goal_path, mode='a', header=write_header, index=False)
                        
                        if debug:
                            print(f"右ゴールシーンを保存しました - 攻撃チーム: {attacking_team}, 角度: {angle}")
                
                # 左ゴールの判定
                elif ball_x < left_goal_x and goal_y_min < ball_y < goal_y_max:
                    attacking_team = determine_attacking_team(robot_poji, 'left')
                    angle, speed = calculate_ball_angle(ball_velocity_data)
                    
                    if os.path.exists(robot_position_path):
                        df_robot_position = pd.read_csv(robot_position_path)
                        last_20_frames = df_robot_position.tail(120)
                        
                        # チーム情報と角度情報を追加
                        goal_data = last_20_frames.copy()
                        goal_data['attacking_team'] = attacking_team
                        goal_data['goal_side'] = 'left'
                        goal_data['ball_angle'] = angle if angle is not None else 0
                        goal_data['ball_speed'] = speed if speed is not None else 0
                        goal_data['ball_x'] = ball_x
                        goal_data['ball_y'] = ball_y
                        
                        # ヘッダー付きで保存
                        write_header = not os.path.exists(left_goal_path) or os.path.getsize(left_goal_path) == 0
                        goal_data.to_csv(left_goal_path, mode='a', header=write_header, index=False)
                        
                        if debug:
                            print(f"左ゴールシーンを保存しました - 攻撃チーム: {attacking_team}, 角度: {angle}")
                            
        except KeyboardInterrupt:
            break
        except Exception as e:
            if debug:
                print(f"Error in goal_scene: {e}")
            continue