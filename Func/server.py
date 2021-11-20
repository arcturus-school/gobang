# TCP 协议
from socket import socket, AF_INET, SOCK_STREAM
# 多线程
from threading import Thread
from time import strftime, localtime
import json


class server:
    def __init__(self, HOST, PORT) -> None:
        self.HOST = HOST  # 服务器 IP
        self.PORT = PORT  # 服务器端口
        self.online = []  # 连接列表/在线列表(套接字对象)
        self.IP_PORT = []  # 与套接字对应的 ip/端口列表
        self.contact = {}  # 对手表

    def start(self, ):
        '''
        开启服务器
        '''
        s = socket(AF_INET, SOCK_STREAM)
        # 绑定服务器使用的端口和 IP 地址
        s.bind((self.HOST, self.PORT))
        # 服务器监听
        s.listen()

        # 两个线程
        # 一个用来监听哪个客户端连接上了服务器(accept)
        # 一个用来监听客户端发过来的信息(recv)
        while True:
            conn, addr = s.accept()
            self.online.append(conn)  # 保存已建立连接 conn 对象
            self.IP_PORT.append(conn.getpeername())  # 保存对应的IP/端口
            print('来自 %s:%s 的连接' % (addr[0], addr[1]))

            self.sendOnline()  # 发送在线人员列表

            # 开启新线程读取消息
            t = Thread(target=self.receive, args=(conn, addr))
            t.start()

    def receive(self, conn, addr):
        '''
        接收客户端消息
        '''
        while True:
            try:
                data = conn.recv(1024)
                # 如果读入数据失败, 说明远程主机主动关闭连接
                if not data:
                    print(f'客户端 {addr[0]}:{addr[1]} 已断开连接...')
                    # 删掉对应的信息
                    self.online.remove(conn)
                    self.IP_PORT.remove(conn.getpeername())
                    conn.close()  # 关闭发送客户端
                    # 有人下线了, 则重新发送在线人员列表
                    self.sendOnline()
                    break
                else:
                    data_ = json.loads(data.decode('gb2312'))
                    print(f'收到来自 {addr[0]}:{addr[1]} 的信息: {data_}')
                    self.write(ip=addr[0], port=addr[1], data=data_)

                    if "chat" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "chat": {
                                "content": data_["chat"],
                                "IP": addr[0],
                                "PORT": addr[1]
                            }
                        }).encode('gb2312')
                        c.send(s)
                    elif "board" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "board": data_["board"]
                        }).encode('gb2312')
                        c.send(s)
                    elif "quit" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "quit": data_["quit"]
                        }).encode('gb2312')
                        c.send(s)
                    elif "undo" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "undo": data_["undo"]
                        }).encode('gb2312')
                        c.send(s)
                    elif "invite" in data_:
                        a = data_["invite"]
                        # 根据邀请对象查找套接字对象
                        b = (a["IP"], a["port"])
                        print(f"打算邀请的人员:{b}")
                        index = self.IP_PORT.index(b)
                        c = self.online[index]
                        s = json.dumps({
                            "invite": {
                                "IP": addr[0],
                                "port": addr[1]
                            }
                        }).encode('gb2312')
                        # 向对方发送邀请请求
                        c.send(s)
                    elif "invite_OK" in data_:
                        # 收到接受请求
                        a = data_["invite_OK"]
                        b = (a["IP"], a["port"])
                        print(f"收到{addr[0]}:{addr[1]}接受{b[0]}:{b[1]}的请求")
                        index = self.IP_PORT.index(b)
                        c = self.online[index]
                        s = json.dumps({
                            "invite_OK": {
                                "IP": addr[0],
                                "port": addr[1],
                                "role": a["role"]
                            }
                        }).encode('gb2312')
                        # 向对方发送接受请求
                        c.send(s)
                        # 将对手互相绑定
                        self.contact.update({
                            f"{addr[0]}:{addr[1]}":
                            f"{b[0]}:{b[1]}",
                            f"{b[0]}:{b[1]}":
                            f"{addr[0]}:{addr[1]}"
                        })
                    elif "board" in data_:
                        pass
                    elif "refuse" in data_:
                        # 如果拒绝邀请
                        a = data_["refuse"]
                        b = (a["IP"], a["port"])
                        print(f"收到{addr[0]}:{addr[1]}拒绝{b[0]}:{b[1]}的请求")
                        index = self.IP_PORT.index(b)
                        c = self.online[index]
                        s = json.dumps({
                            "refuse": {
                                "IP": addr[0],
                                "port": addr[1]
                            }
                        }).encode('gb2312')
                        # 向对方发送拒绝请求
                        c.send(s)
                    elif "undo" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "undo": True
                        }).encode('gb2312')
                        c.send(s)
                    elif "undo_OK" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "undo_OK": data_["undo_OK"]
                        }).encode('gb2312')
                        c.send(s)
                    elif "resume" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "resume": True
                        }).encode('gb2312')
                        c.send(s)
                    elif "resume_OK" in data_:
                        a = f"{addr[0]}:{addr[1]}"
                        b = self.contact[a].split(":")
                        c = (b[0], int(b[1]))
                        index = self.IP_PORT.index(c)
                        c = self.online[index]
                        s = json.dumps({
                            "resume_OK": data_["resume_OK"]
                        }).encode('gb2312')
                        c.send(s)
            except ConnectionResetError:
                ip, port = conn.getpeername()
                print(f'远程主机 {ip}:{port} 意外退出...')
                # 清除远程主机信息
                self.online.remove(conn)
                self.IP_PORT.remove(conn.getpeername())
                # 有人下线了, 则重新发送在线人员列表
                self.sendOnline()
                break
            except ValueError as e:
                print(e)

    def write(self, **kwarg):
        '''
        服务器收到的信息写入 txt 文件
        '''
        # 获取当前时间
        t = strftime("%Y-%m-%d %H:%M:%S", localtime())
        ip = kwarg["ip"]
        port = kwarg["port"]
        data = kwarg["data"]
        chatRecord = f"[{t}] # {ip}:{port}>\n{data}\n"
        # 在文末追加写入内容
        f = open("log.txt", 'a', encoding="utf-8")
        f.write(chatRecord)

    def sendOnline(self):
        '''
        向客户端发送在线人员信息
        '''
        online_str = json.dumps({"online": self.IP_PORT}).encode('gb2312')
        for conn_ in self.online:
            conn_.send(online_str)


s = server("10.22.164.18", 50007)
s.start()
