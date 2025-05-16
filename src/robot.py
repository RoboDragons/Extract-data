import os
import pandas as pd

def track_robot_position(udp, receive_packet, path):
    if not os.path.isdir(path):
        os.mkdir(path)
    packet = receive_packet(udp)
    robots_yellow = packet.detection.robots_yellow
    robots_blue = packet.detection.robots_blue
    robot_positions = {"yellow": {}, "blue": {}}
    if robots_yellow:
        for yellow_robot in robots_yellow:
            if 0 <= yellow_robot.robot_id < 17:
                robot_positions["yellow"][yellow_robot.robot_id] = (int(yellow_robot.x), int(yellow_robot.y))
    if robots_blue:
        for blue_robot in robots_blue:
            if 0 <= blue_robot.robot_id < 17:
                robot_positions["blue"][blue_robot.robot_id] = (int(blue_robot.x), int(blue_robot.y))
    return robot_positions

def store_robot_position(udp, receive_packet, path, stop_event, debug=False):
    import os
    import pandas as pd
    robot_locate = []
    while not stop_event.is_set():
        try:
            positions = track_robot_position(udp, receive_packet, path)
            if positions:
                row = {}
                for color in ["yellow", "blue"]:
                    for robot_id, (x, y) in positions[color].items():
                        row[f"{color}_{robot_id}_x"] = x
                        row[f"{color}_{robot_id}_y"] = y
                robot_locate.append(row)
                if len(robot_locate) >= 10:
                    robotPath = os.path.join(path, "robot_position.csv")
                    df = pd.DataFrame(robot_locate)
                    write_header = not os.path.exists(robotPath) or os.path.getsize(robotPath) == 0
                    df.to_csv(robotPath, mode='a', header=write_header, index=False)
                    robot_locate.clear()
                if debug:
                    print(f"robot_locate (バッファ内): {len(robot_locate)}")
        except KeyboardInterrupt:
            break