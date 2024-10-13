import os
import pandas as pd
import socket
import time
import messages_robocup_ssl_wrapper_pb2

def main():
    # 通信設定 from SSL-Vision
    local       = "127.0.0.1"
    multicast   = "224.5.23.2"
    port        = 10006
    buffer      = 65536

    # ログの保存設定
    path = "out/"
    calibPath = path + "calib.txt"
    framePath = path + "ssl-vision-client.csv"

    ###==== 通信開始 ====###
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
    while True:
        try:
            parser = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
            data, _ = udp.recvfrom(buffer)
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
                    tmp = [
                     frame.frame_number,
                     frame.t_capture,
                     balls.x,
                     balls.y ,  
                     balls.pixel_x,
                     balls.pixel_y,
                    ]
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
        print(calib)

    if frames:
        df = pd.DataFrame(frames, columns=["frame_number", "t_capture", "x", "y", "pixel_x", "pixel_y"])
        df = df.sort_values("frame_number")
        df.to_csv(framePath, header=True, index=False)

    udp.close()

if __name__=="__main__":
    main()