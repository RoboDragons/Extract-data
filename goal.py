import os
import pandas as pd

def goal_scene(track_ball_position, track_robot_position, path, stop_event, debug=False):
    robot_poji_goal_path = os.path.join(path, "robot_position_goal.csv")
    robot_position_path = os.path.join(path, "robot_position.csv")
    poji_goal_x=6000
    nega_goal_x=-6000
    poji_goal_y=600
    nega_goal_y=600
    if not os.path.isdir(path):
        os.mkdir(path)
    while not stop_event.is_set():
        try:
            balls_position = track_ball_position()
            robot_poji = track_robot_position()
            if balls_position and robot_poji:
                ball_x, ball_y, state = balls_position[-1]
                if ball_x > 6000:
                    if robot_poji and ((ball_x > poji_goal_x and (poji_goal_y > ball_y > nega_goal_y)) or (ball_x < nega_goal_x and (poji_goal_y > ball_y > nega_goal_y))):
                        df_robot_position = pd.read_csv(robot_position_path)
                        last_20_frames = df_robot_position.tail(120)
                        df = pd.DataFrame(last_20_frames)
                        df.to_csv(robot_poji_goal_path, header=True, index=False)
                        if debug:
                            print("ゴールシーンを保存しました")
        except KeyboardInterrupt:
            break