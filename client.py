# -*- coding: UTF-8 -*-

import socket
import time
import struct
import math
import random

SERVER_IP = input("serverIP: ")  # 服务器（主机）的IP地址
SERVER_PORT = int(input("serverPort: "))  # 定义端口号
TIMEOUT = 0.1  # 设置超时时间为100ms
MAX_RETRIES = 2  # 最大重传次数
VERSION = 2
CLASS = 1
STU_ID = "221002518"
def res(response):
    seq_no = struct.unpack('!H', response[:2])[0]
    ver = struct.unpack('!B', response[2:3])[0]
    system_time = response[3:].decode('utf-8').strip('\x00')
    return seq_no, ver, system_time

def packing(seq_no, ver, class_, student_id):
    seq_no_bytes = struct.pack('!H', seq_no)
    ver_bytes = struct.pack('!B', ver)
    class_bytes = struct.pack('!B', class_)
    student_id_bytes = student_id.encode('utf-8')
    student_id_bytes = student_id_bytes[:9]
    student_id_bytes = student_id_bytes.ljust(9, b'\x00')
    packet = seq_no_bytes + ver_bytes + class_bytes + student_id_bytes
    return packet


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建一个UDP socket
    client.settimeout(TIMEOUT)  # 设置socket的超时时间

    print('Sending SYN to server...')
    client.sendto('SYN'.encode('utf-8'), (SERVER_IP, SERVER_PORT))  # 将消息编码为UTF-8，然后发送到服务器

    data, server = client.recvfrom(1024)
    if data.decode() == "ACK":
        client.sendto('ACK'.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        print("Connection established with the server.")

        RTTs = []
        total_packets = 0
        received_packets = 0

        i = 0
        while i <= 12:
            attempts = 0
            i += 1
            while attempts <= MAX_RETRIES:
                message = packing(i, VERSION, CLASS, STU_ID)
                start_time = time.perf_counter()
                client.sendto(message, (SERVER_IP, SERVER_PORT))
                total_packets += 1

                try:
                    data, server = client.recvfrom(1024)
                    end_time = time.perf_counter()
                    RTT = (end_time - start_time) * 1000
                    RTTs.append(RTT)
                    received_packets += 1
                    seq_no, ver, system_time = res(data)
                    print(f"Received response for packet {seq_no} with RTT {RTT:.2f} ms from Server_Port {SERVER_PORT}")
                    break
                except socket.timeout:
                    print(f"Packet {i} lost. Retrying...")
                    attempts += 1

            if attempts > MAX_RETRIES:
                print(f"Packet {i} lost after {MAX_RETRIES} retries. Giving up.")

        drop_rate = (total_packets - received_packets) / total_packets * 100
        print(f"\nSummary:")
        print(f"Drop rate: {drop_rate:.2f}%")
        print(f"Max RTT: {max(RTTs):.2f} ms")
        print(f"Min RTT: {min(RTTs):.2f} ms")
        print(f"Avg RTT: {sum(RTTs)/len(RTTs):.2f} ms")
        print(f"RTT标准差: {math.sqrt(sum(RTTs) / len(RTTs)):.2f} ms")
        total_time = sum(RTTs)
        print(f"Total time: {total_time:.2f} ms")

    else:
        print("Failed to establish connection with the server.")
        client.close()

if __name__ == '__main__':
    main()
