# -*- coding: UTF-8 -*-

import socket
import random
import struct
import time

PORT = 1233 # 定义端口号
HOST = '192.168.92.1'  # 主机的IP地址
DROP_RATE = 0.1  # 设置丢包率为10%
MAX_ATTEMPTS = 2  # 最大重传次数

def packing(packet):
    seq_no = struct.unpack('!H', packet[:2])[0]
    ver = struct.unpack('!B', packet[2:3])[0]
    class_ = struct.unpack('!B', packet[3:4])[0]
    student_id = packet[4:13].decode('utf-8').strip('\x00')
    system_time = packet[13:19].decode('utf-8').strip('\x00')
    return seq_no, ver, class_, student_id, system_time

def res(seq_no, ver, system_time):
    seq_no_bytes = struct.pack('!H', seq_no)
    ver_bytes = struct.pack('!B', ver)
    system_time_bytes = system_time.encode('utf-8')
    system_time_bytes = system_time_bytes.ljust(19, b'\x00')
    response = seq_no_bytes + ver_bytes + system_time_bytes #连起来！
    return response

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建一个UDP socket
    server.bind((HOST, PORT))  # 绑定到主机的IP地址和指定的端口号

    print('Waiting for the client to connect...')
    data, client_addr = server.recvfrom(1024)  # 使用recvfrom方法接收客户端发送的数据和客户端的地址
    if data.decode('utf-8') == 'SYN':
        print('Received SYN from client, sending ACK...')
        server.sendto('ACK'.encode('utf-8'), client_addr)

    data, client_addr = server.recvfrom(1024)
    if data.decode('utf-8') == 'ACK':
        print('Received ACK from client, connection established.')

    attempts = 0  # 初始化重传次数
    while True:  # 无限循环，等待接收客户端的消息
        data, client_addr = server.recvfrom(1024)  # 使用recvfrom方法接收客户端发送的数据和客户端的地址
        seq_no, ver, class_, stu_id, alpha = packing(data)
        print(f"Received message from {client_addr}: Seq_no={seq_no}, Ver={ver}, Class={class_},Stu_ID={stu_id}")

        # 如果生成的随机数小于丢包率，那么就丢弃数据包并增加重传次数
        if random.random() < DROP_RATE:
            print('Packet from', client_addr, 'dropped.')
           # server.sendto('no'.encode('utf-8'), client_addr)  # 发送特殊的字符串"no"给客户，表示丢包
            continue

        # 对数据包进行响应
        system_time = time.strftime('%Y-%m-%d %H:%M:%S')  # 获取系统时间
        response = res(seq_no, ver, system_time)
        server.sendto(response, client_addr)  # 发送响应报文
        print(f"Response sent: Seq_no={seq_no}, Ver={ver},Port={PORT} Time={system_time}")
        attempts = 0  # 重置重传次数

        # 如果接收到特殊的消息，就跳出循环
        if data.decode('utf-8') == 'END':
            break

if __name__ == '__main__':
    main()
