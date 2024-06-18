import socket
import struct

def reverse_string(s):
    return s[::-1]

def handle_client(conn):
    while True:
        # 接收报文类型
        type_data = conn.recv(2)
        if not type_data:
            break
        type = struct.unpack('!H', type_data)[0]

        if type == 1:  # Initialization报文
            n_data = conn.recv(4)
            n = struct.unpack('!I', n_data)[0]
            print(f"Received initialization message, N={n}")
            # 发送agree报文
            conn.sendall(struct.pack('!H', 2))
        elif type == 3:  # reverseRequest报文
            length_data = conn.recv(4)
            length = struct.unpack('!I', length_data)[0]
            data = conn.recv(length).decode()
            print(f"Received reverse request, data={data}")
            # 发送reverseAnswer报文
            reversed_data = reverse_string(data)
            conn.sendall(struct.pack('!HI', 4, len(reversed_data)) + reversed_data.encode())
        else:
            print(f"Unknown type {type}")
            break

def start_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen()
        print(f"Server started at {ip}，port：{port}")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                handle_client(conn)

if __name__ == "__main__":
    ip = '172.26.80.9'
    port = int(input("请输入server端口号: "))
    start_server(ip, port)
