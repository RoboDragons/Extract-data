import threading
import socket
import struct
import os
import pandas as pd
import time
import messages_robocup_ssl_wrapper_pb2
import ssl_gc_state_pb2
import ssl_gc_engine_pb2
import ssl_gc_referee_message_pb2
debug = False

def receive_game_controller_signal():
    buffer_size = 4096  # バッファサイズを増やす
    multicast_group = '224.5.23.1'
    server_address = ('', 10003)

    # ソケットの作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ソケットにオプションを設定し、マルチキャストグループに参加
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)

    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

   
    try:
        while True:
            data, address = sock.recvfrom(buffer_size)  # データ受信
            if not data:
                break  # 接続が切れた場合、ループを抜ける
            if debug:
                print("データを受信しました from", address)
                print("受信データ (バイナリ):", data)  # 受信データをバイナリ形式で表示
            
            try:
                # RefereeMessageのデコード
                referee_message = ssl_gc_referee_message_pb2.Referee()
                referee_message.ParseFromString(data)
                if debug:                
                    print("Referee Message (人間が読みやすい形式):")
                    print(referee_message.command)
                return referee_message.command
            except Exception as e:
                print("RefereeMessage デコードエラー:", e)
                print("----------------------")

    except KeyboardInterrupt:
        print("終了処理を開始します...")
    finally:
        sock.close()  # ソケットを閉じる
        print("ソケットを閉じました")

def track_ball_position():
    local       = "127.0.0.1"
    multicast   = "224.5.23.2"
    port        = 10006
    buffer      = 65536

    path = "out/"
    calibPath = path + "calib.txt"
    framePath = path + "ssl-vision-client.csv"

    addr = ('', port)
    udp  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(addr)
    udp.setsockopt(socket.IPPROTO_IP,
                   socket.IP_ADD_MEMBERSHIP,
                   socket.inet_aton(multicast) + socket.inet_aton(local))

    calibDone = False
    calib     = None
    frames    = []
    ball_position = []
    while True:
        try:
            parser = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data, _ = udp.recvfrom(buffer)
            parser.ParseFromString(data)

            # カメラからのデータ
            if not calibDone:
                calib = parser.geometry.calib
                if calib:
                    calib = calib[0]
                    calibDone = True

            # ボールの位置データ
            frame = parser.detection
            print("frame: ", frame)
            if frame:
                balls = frame.balls
                if balls:
                    balls = balls[0]
                    tmp = [
                     frame.frame_number,
                     frame.t_capture,
                     balls.x,
                     balls.y ,  
                     balls.pixel_x,
                     balls.pixel_y,
                    ]
                    if receive_game_controller_signal() == 2 or 3 or 8 or 9:
                        balls_position=[int(balls.x)/10,int(balls.y)/10]
                        ball_position.append(balls_position)
                        print("ball_position: ", ball_position)
                        print("\n")
                    #frames.append(tmp)
                    #print("frame: ", frame.frame_number)

            time.sleep(0.001)
        except KeyboardInterrupt:
            break

    if not os.path.isdir(path):
        os.mkdir(path)

    if calibDone:
        with open(calibPath, mode="w") as f:
            f.write(str(calib))
        print(calib)

    if ball_position:
        df = pd.DataFrame(ball_position, columns=["x", "y"])
        df = df.sort_values("x")
        df.to_csv(framePath, header=True, index=False)

    udp.close()

if __name__ == "__main__":
    # スレッドを作成して、両方の関数を並行して実行
    thread1 = threading.Thread(target=receive_game_controller_signal)
    thread2 = threading.Thread(target=track_ball_position)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()