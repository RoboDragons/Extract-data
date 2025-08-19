import socket
import struct
import messages_robocup_ssl_wrapper_pb2
import ssl_gc_referee_message_pb2

local = "127.0.0.1" # ローカルアドレスを指定
multicast = "224.5.23.2" # マルチキャストアドレスを指定
port = 10006 # ポート番号を指定
buffer = 65536 # バッファサイズを指定
addr = ('', port) # アドレスを指定

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDPソケットを作成
udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # アドレスの再利用を許可
udp.bind(addr) # ソケットをバインド
udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast) + socket.inet_aton(local)) # マルチキャストグループに参加

def setup_socket(): # ソケットのセットアップ
    global sock # ソケットをグローバル変数として宣言
    buffer_size = 4096 # バッファサイズを指定
    multicast_group = '224.5.23.1' # マルチキャストグループを指定
    server_address = ('', 10003) # サーバーアドレスを指定
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # アドレスの再利用を許可
    sock.bind(server_address) # ソケットをバインド
    group = socket.inet_aton(multicast_group) # マルチキャストグループを指定
    mreq = struct.pack('4sL', group, socket.INADDR_ANY) # マルチキャストグループへの参加要求を作成
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # マルチキャストグループに参加
    return sock

def receive_packet(udp): # パケットを受信
    packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket() # SSL_WrapperPacketを作成
    data, _ = udp.recvfrom(buffer) # データを受信
    packet.ParseFromString(data) # 受信したデータを解析,変換
    return packet

def receive_game_controller_signal(sock, stop_event, buffer_size=4096, debug=False): # ゲームコントローラーの信号を受信
    try:
        while not stop_event.is_set(): # 停止イベントがセットされるまでループ
            data, address = sock.recvfrom(buffer_size) # データを受信
            if debug:
                print("データを受信しました from", address) # 受信元アドレスを表示
                print("受信データ (バイナリ):", data) # 受信データ (バイナリ) を表示
            try:
                referee_message = ssl_gc_referee_message_pb2.Referee() # Refereeメッセージを作成
                referee_message.ParseFromString(data) # 受信したデータを解析
                if debug:
                    print("Referee Message (人間が読みやすい形式):") # 人間が読みやすい形式で表示
                return referee_message.command
            except Exception as e: # デコードエラー処理
                print("RefereeMessage デコードエラー:", e)
                print("----------------------")
    except KeyboardInterrupt: # キーボード割り込み処理
        print("終了処理を開始します...")