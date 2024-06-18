import socket
import struct
import random

def send_file_to_server(filename):
    server_ip = input("请输入server IP: ")
    server_port = int(input("请输入server端口号: "))
    lmin = int(input("请输入发送data的最小长度： "))
    lmax = int(input("请输入发送data的最大长度： "))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((server_ip, server_port))
        except Exception as e:
            print(f"连接建立失败，不能通信: {e}")
            return

        print(f"Connected to server ip:{server_ip}, port：{server_port}")

        with open(filename, 'r') as f:
            content = f.read()

            # 先随机确定待发送文件中各块的字节长度
            lengths = []
            while len(content) > lmax:
                length = random.randint(lmin, lmax)
                lengths.append(length)
                content = content[length:]
            lengths.append(len(content))

            # 计算块数并发送Initialization报文
            n = len(lengths)
            s.sendall(struct.pack('!HI', 1, n))

            # 等待server的agree报文
            type_data = s.recv(2)
            type = struct.unpack('!H', type_data)[0]
            if type == 2:
                print("收到来自server的agree报文！")
            else:
                print("没收到agree报文！over！")
                return;
            # 打开一个新的文件，用于保存反转后的数据
            with open('E:\\reversed_story.txt', 'w') as out:
                # 逐块发送reverseRequest报文并接收reverseAnswer报文
                with open(filename, 'r') as f:
                    for i in range(n):
                        data = f.read(lengths[i])
                        print(f"Sending block {i + 1}, data={data}")
                        s.sendall(struct.pack('!HI', 3, len(data)) + data.encode())
                        type_data = s.recv(2)
                        type = struct.unpack('!H', type_data)[0]
                        if type != 4:
                            print(f"Did not receive reverse answer for block {i + 1}")
                            return
                        length_data = s.recv(4)
                        length = struct.unpack('!I', length_data)[0]
                        reversed_data = s.recv(length).decode()
                        print(f"Received reversed block {i + 1}, data={reversed_data}")
                        # 将反转后的数据写入到新的文件中
                        out.write(reversed_data)
if __name__ == "__main__":
    send_file_to_server('E:\\story.txt')
