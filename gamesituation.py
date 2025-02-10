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
STATE_LIST = []
State_num = 0
count = 0
sock = None
Game_on=[2,3,4,5,8,9]

def setup_socket():
    global sock
    buffer_size = 4096  # バッファサイズ データの受け取るお皿の大きさ
    multicast_group = '224.5.23.1'
    server_address = ('', 10003)  # GCのアドレス データが送られてくる元の

    # ソケットの作成 SOCK_DGRAMはUDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ソケットにオプションを設定し、マルチキャストグループに参加
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)

    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def receive_game_controller_signal():
    global sock
    buffer_size = 4096  # バッファサイズ データの受け取るお皿の大きさ

    try:
        data, address = sock.recvfrom(buffer_size)  # データ受信
        if debug:
            print("データを受信しました from", address)
            print("受信データ (バイナリ):", data)  # 受信データをバイナリ形式で表示

        try:
            # RefereeMessageのデコード
            referee_message = ssl_gc_referee_message_pb2.Referee()
            referee_message.ParseFromString(data)
            if debug:
                print("Referee Message (人間が読みやすい形式):")

            print(referee_message.Command.Name(referee_message.command))
            return referee_message.command
            # if len(STATE_LIST) < 5:
            #     STATE_LIST.append(referee_message.command)
            #     #print(len(STATE_LIST))
            #     print(       )
            #     print(referee_message.Command.Name(referee_message.command))
            # else:
            #     for i in range(len(STATE_LIST)):
            #         if STATE_LIST[i] != 0:
            #             State_num = STATE_LIST[i]
            #             #print(STATE_LIST)
            #             #print(State_num)
            #             STATE_LIST.clear()        
            #             print("////",referee_message.Command.Name(State_num))
                        
            #             return State_num
                                            
            #         #else:
                                
                
            #if referee_message.command in [2, 3, 8, 9]:
            #print(referee_message.Command.Name(referee_message.command))
            #return referee_message.command
            # else:
            #     print("    "+referee_message.Command.Name(referee_message.command))    
        except Exception as e:
            print("RefereeMessage デコードエラー:", e)
            print("----------------------")

    except KeyboardInterrupt:
        print("終了処理を開始します...")

def track_ball_position():
    local = "127.0.0.1"
    multicast = "224.5.23.2"
    port = 10006
    buffer = 65536

    path = "out/"
    ballpojiPath = path + "ballpoji.csv"

    addr = ('', port)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(addr)
    udp.setsockopt(socket.IPPROTO_IP,
                   socket.IP_ADD_MEMBERSHIP,
                   socket.inet_aton(multicast) + socket.inet_aton(local))

    ball_position = []

    if not os.path.isdir(path):
        os.mkdir(path)

    while True:
        try:
            packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data, _ = udp.recvfrom(buffer)
            packet.ParseFromString(data)

            frame = packet.detection
            # if frame.frame_number % 100 == 0:
            #     print("frame: ", frame.frame_number)
            #     # count+=1
                # print("   ")
                # print(count)
            if debug:
                print("frame: ", frame)
            if frame:
                balls = frame.balls
                if balls:
                    ball = balls[0]
                    
                    if receive_game_controller_signal() in Game_on:
                    
                        #if frame.frame_number % 100 == 0:
                            print("here")
                            balls_position = [int(ball.x) / 10, int(ball.y) / 10,receive_game_controller_signal()]
                            ball_position.append(balls_position)
                            #print("ball_position: ", ball_position)
                            df = pd.DataFrame(ball_position, columns=["x", "y","state"])
                            df = df.sort_values("x")
                            df.to_csv(ballpojiPath, header=True, index=False)

                            if debug:
                                print("ball_position: ", ball_position)
                                print("\n")
        except KeyboardInterrupt:
            break

        
    udp.close()

if __name__ == "__main__":
    setup_socket()
    # スレッドを作成して、両方の関数を並行して実行
    thread1 = threading.Thread(target=receive_game_controller_signal)
    thread2 = threading.Thread(target=track_ball_position)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    sock.close()
    print("ソケットを閉じました")