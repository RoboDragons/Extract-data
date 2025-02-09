import socket
import struct
import ssl_gc_state_pb2

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

    print("Waiting for a connection from SSL Game Controller...")

    try:
        while True:
            data, address = sock.recvfrom(buffer_size)  # データ受信
            if not data:
                break  # 接続が切れた場合、ループを抜ける

            print("データを受信しました from", address)
            print("受信データ (バイナリ):", data)  # 受信データをバイナリ形式で表示

            try:
                game_state = ssl_gc_state_pb2.GameState()  # 修正箇所
                game_state.ParseFromString(data)
                print("Game State:", game_state)
            except (UnicodeDecodeError, Exception) as e:  # `DecodeError` を `Exception` に変更
                print("デコードまたは解析エラー:", e)

            print("----------------------------------")

    except KeyboardInterrupt:
        print("終了処理を開始します...")
    finally:
        sock.close()  # ソケットを閉じる
        print("ソケットを閉じました")

if __name__ == "__main__":
    receive_game_controller_signal()
