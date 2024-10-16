
import socket
import messages_robocup_ssl_wrapper_pb2
import time

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
    pojidata = path + "pojition.dat"

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
              #  print(str(frame));
                balls = frame.balls
                if balls:
                    balls = balls[0]

                xdata=0           
                ydata=0
        
                #if frame.robots_blue:
                tmp=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
                
                for i in frame.robots_blue:
                    print(i)
                    tmp[i.robot_id*2+1]=i.x
                    tmp[i.robot_id*2+2]=i.y
                    
                        
        

                #tmp = [   
                #frame.frame_number,
                #frame.t_capture,
                #balls.x,
                #balls.y ,  
                #balls.pixel_x,
                #balls.pixel_y,
                #xdata,
                #ydata,
                #]
                frames.append(tmp)
                #print("robots_x_position_info: ", (frame.robots_blue[0].x));
                #print("robots_y_position_info: ", (frame.robots_blue[0].y));
                #print("robots[1]_info: ", (frame.robots_blue[1].robot_id));
                #print("robots[2]_info: ", (frame.robots_blue[2].robot_id));
                #print("robots[3]_info: ", (frame.robots_blue[3].robot_id));

            

            time.sleep(0.001)
        except KeyboardInterrupt:
            break

    ###==== ログの保存 ====###
    if not os.path.isdir(path):
        os.mkdir(path)

    if calibDone:
        with open(calibPath, mode="w") as f:
            f.write(str(calib))
        #print(calib)

    if frames:
        df = pd.DataFrame(
            frames, columns=["1position_x","2positon_y",
                             "3position_x","4positon_y",
                             "5position_x","6positon_y",
                             "7position_x","8positon_y",
                             "9position_x","10positon_y",
                             "11position_x","12positon_y",
                             "13position_x","14positon_y",
                             "15position_x","16positon_y",
                             "17position_x","18positon_y",
                             "19position_x","20positon_y",
                             "21position_x","22positon_y",
                             "23position_x","24positon_y",

                             # "t_capture", 
                             # "x", 
                             # "y", 
                             # "pixel_x", 
                             # "pixel_y"
                             ])
       # df = df.sort_values("frame_number")
        df.to_csv(framePath, header=True, index=False)
        
        #df.to_dat(pojidata, header=True, index=False)

    udp.close()

if __name__=="__main__":
    main()

"""# TCP setup
addr = ('', port)  # Replace '' with your desired IP address or leave it as an empty string to bind to all interfaces
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp.bind(addr)
tcp.listen(1)
calibDone = False
calib = None
frames = []

# Accepting a connection
conn, addr = tcp.accept()

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
                tmp = [
                    frame.frame_number,
                    frame.t_capture,
                    balls.x,
                    balls.y,
                    balls.pixel_x,
                    balls.pixel_y,
                ]
                frames.append(tmp)
                print("frame: ", frame.frame_number)
        
        time.sleep(0.001)
    except KeyboardInterrupt:
        break

conn.close()
tcp.close()
"""