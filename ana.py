import socket
import messages_robocup_ssl_wrapper_pb2
import time
import os
import pandas as pd

def main():
    # 通信設定 from SSL-Vision
    local = "127.0.0.1"
    port = 10006
    buffer = 65536
    
    # ログの保存設定
    path = "out/"
    calibPath = path + "calib.txt"
    framePath = path + "ssl-vision-client.csv"
    pojidata = path + "pojition.dat"

    ###==== 通信開始 ====###
    addr = ('', port)
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp.bind(addr)
    tcp.listen(1)
    print("Waiting for a connection...")

    conn, addr = tcp.accept()
    print(f"Connected by {addr}")

    calibDone = False
    calib = None
    frames = []

    while True:
        try:
            parser = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data = conn.recv(buffer)
            if not data:
                break
            parser.ParseFromString(data)
            
            # カメラのキャリブレーションデータ
            if not calibDone:
                calib = parser.geometry.calib
                if calib:
                    calib = calib[0]
                    calibDone = True
            
            # ボールの検出データ
            frame = parser.detection
            if frame:
                balls = frame.balls
                if balls:
                    balls = balls[0]
                xdata = 0
                ydata = 0
                tmp = [0] * 35
                for i in frame.robots_yellow:
                    tmp[i.robot_id*2+1] = i.x
                    tmp[i.robot_id*2+2] = i.y
                frames.append(tmp)
                print("frame: ", frame.frame_number)
            time.sleep(0.001)
        except KeyboardInterrupt:
            break

    ###==== ログの保存 ====###
    if not os.path.isdir(path):
        os.mkdir(path)
    if calibDone:
        with open(calibPath, mode="w") as f:
            f.write(str(calib))
    if frames:
        columns_ = []
        for i in range(len(tmp)):
            if i % 2 == 1:
                columns_.append(str(i) + "p_x")
            if i % 2 == 0:
                columns_.append(str(i) + "p_y")
        df = pd.DataFrame(frames, columns=columns_)
        df.to_csv(framePath, header=True, index=False)
    conn.close()
    tcp.close()

if __name__ == "__main__":
    main()

