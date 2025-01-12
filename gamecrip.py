import socket
import messages_robocup_ssl_wrapper_pb2
import time
import os
import pandas as pd


def main():
    # 通信設定
    local_address = "127.0.0.1"
    multicast_address = "224.5.23.2"
    port = 10006
    buffer_size = 65536

    # ログの保存設定
    output_path = "out/"
    calibration_file_path = os.path.join(output_path, "calib.txt")
    offense_frame_file_path = os.path.join(output_path, "offense_frame.csv")
    defense_frame_file_path = os.path.join(output_path, "defense_frame.csv")
    

    # ソケットのセットアップ
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(('', port))
    udp_socket.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(multicast_address) + socket.inet_aton(local_address)
    )

    calibration_done = False
    calibration_data = None
    offense_frames = []
    

    try:
        while True:
            try:
                # データの受信と解析
                wrapper_packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
                data, _ = udp_socket.recvfrom(buffer_size)
                wrapper_packet.ParseFromString(data)

                # キャリブレーションデータの取得
                if not calibration_done:
                    if wrapper_packet.HasField("geometry") and wrapper_packet.geometry.calib:
                        calibration_data = wrapper_packet.geometry.calib[0]
                        calibration_done = True

                # ボールとロボットのデータ処理
                if wrapper_packet.HasField("detection"):
                    detection_data = wrapper_packet.detection

                    # ボールデータの取得
                    ball = None
                    if detection_data.balls:
                        ball = detection_data.balls[0]

                    # ロボットの位置データ
                    pside_offense_robo_position = [None] * 24# 12台のロボット、各ロボットのxとyを記録するため24要素
                    pside_defence_robo_position = [None] * 24
                    nside_offense_robo_position = [None] * 24
                    nside_defence_robo_position = [None] * 24
                    attacking_blue_robots_count = 0
                    attacking_yellow_robots_count = 0
                    defending_blue_robots_count = 0
                    defending_yellow_robots_count = 0
                    
                    total_blue_robots = len(detection_data.robots_blue)
                    total_yellow_robots = len(detection_data.robots_yellow)
                    #コートの判定
                    #print(detection_data)
                    print(calibration_data)
                    #bulearea=detection_data.center_circle_radius
                    blue_robot=detection_data.robots_blue
                    yellow_robot=detection_data.robots_yellow
                    #途中で変わる可能性ある笑
                    #審判の信号とれるといいよね！
                    
                    #ゴールエリアにいるロボットがどっちかでコートを判定します！
                    if(4800<blue_robot.x &6000>blue_robot.x &1800>blue_robot.y & -1800<blue_robot.y ):
                        pside_team=blue_robot
                        nside_team=yellow_robot
                    else:
                        pside_team=yellow_robot
                        nside_team=blue_robot
                        
                    # 攻撃しているロボットのカウントと位置を記録
                        #オフェンスディフェンスのフラグ（いるかもで作った）
                        pside_team_offence=False
                        pside_team_defence=False
                        nside_team_offence=False
                        nside_team_defence=False
                    #ボールの保持を定義
                        #print(blue_robot.pixel_x)
                        print(container)

                    #pojiサイドの攻めの人数
                        for robot in pside_team:
                            if robot.x > 0:
                                attacking_blue_robots_count += 1
                                pside_offense_robo_position[robot.robot_id * 2] = robot.x
                                pside_offense_robo_position[robot.robot_id * 2 + 1] = robot.y
                                
                        for robot in pside_team:
                            if robot.x > 0:
                                attacking_blue_robots_count += 1
                                pside_offense_robo_position[robot.robot_id * 2] = robot.x
                                pside_offense_robo_position[robot.robot_id * 2 + 1] = robot.y
                    
                    #攻めの定義ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
                    #攻めをロボットが半分以上相手コートにいた時と定義しました．検証する必要あり！
                    # 攻撃条件に基づくロジック
                    if ball and ball.x > 0 and attacking_blue_robots_count > total_blue_robots / 2:
                        offense_frames.append(pside_offense_robo_position)
                    

            except Exception as e:
                print(f"Error while processing data: {e}")
                continue

    except KeyboardInterrupt:
        print("\n終了処理を開始します...")

    finally:
        # ログの保存
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if calibration_done:
            with open(calibration_file_path, "w") as calib_file:
                calib_file.write(str(calibration_data))
            print(f"Calibration data saved to {calibration_file_path}")

        if offense_frames:
            columns = [f"{i // 2 + 1}_posi_x" if i % 2 == 0 else f"{i // 2 + 1}_posi_y" for i in range(24)]
            df = pd.DataFrame(offense_frames, columns=columns)
            df.to_csv(offense_frame_file_path, index=False)
            print(f"offense_frames saved to {offense_frame_file_path}")

        if offense_frames:
            columns = [f"{i // 2 + 1}_posi_x" if i % 2 == 0 else f"{i // 2 + 1}_posi_y" for i in range(24)]
            df = pd.DataFrame(offense_frames, columns=columns)
            df.to_csv(offense_frame_file_path, index=False)
            print(f"offense_frames saved to {offense_frame_file_path}")

        udp_socket.close()
        print("ソケットを閉じました")


if __name__ == "__main__":
    main()
