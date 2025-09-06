import socket
import struct
import messages_robocup_ssl_wrapper_pb2
import ssl_gc_referee_message_pb2

local = "127.0.0.1"
multicast = "224.5.23.2"
port = 10006
buffer = 65536
addr = ('', port)
ref_signal= [None, None]  # [command, state]

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp.bind(addr)
udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast) + socket.inet_aton(local))

def setup_socket():
    global sock
    buffer_size = 4096
    multicast_group = '224.5.23.1'
    server_address = ('', 10003)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def receive_packet(udp):
    packet = messages_robocup_ssl_wrapper_pb2.SSL_WrapperPacket()
    data, _ = udp.recvfrom(buffer)
    packet.ParseFromString(data)
    return packet

def receive_game_controller_signal(sock, stop_event, buffer_size=4096, debug=False):
    global ref_signal
    try:
        while not stop_event.is_set():
            data, address = sock.recvfrom(buffer_size)
            try:
                referee_message = ssl_gc_referee_message_pb2.Referee()
                referee_message.ParseFromString(data)
                # print(referee_message.command)
                # print("referee_message:", referee_message)
                # print("-----------------------")
                if(ref_signal[0] is None):
                    ref_signal[0] = referee_message.command
                    # print(ref_signal[0])
                    print("de")
                    
                else:
                    ref_signal[1] = referee_message.command
                    # print(ref_signal)
                    if ref_signal[1]!=ref_signal[0]:
                        print("Referee Command Changed:", referee_message.command)
                        ref_signal[0]=ref_signal[1]
                    
                # if debug:
                # print("Referee Message (人間が読みやすい形式):")
                # print(referee_message.command)
                # print("Referee Command:", type(referee_message.command))
                return referee_message.command
                # return referee_message
            except Exception as e:
                print("RefereeMessage デコードエラー:", e)
                # print("----------------------")
    except KeyboardInterrupt:
        print("終了処理を開始します...")