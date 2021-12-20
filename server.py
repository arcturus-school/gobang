from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import strftime, localtime
from Func.json_byte import json_to_byte, byte_to_json
from Func.get_ip import getIPv4


# 服务器
class server:
    def __init__(self, HOST, PORT) -> None:
        self.HOST = HOST  # 服务器 IP
        self.PORT = PORT  # 服务器端口
        self.online = []  # 连接玩家的套接字对象
        self.IP_PORT = []  # 与套接字对象对应的 ip/端口列表
        self.contact = {}  # 玩家对战关联表

    def start(self):
        '''
        开启服务器
        '''
        s = socket(AF_INET, SOCK_STREAM)
        # 绑定服务器使用的端口和 IP 地址
        s.bind((self.HOST, self.PORT))
        # 服务器监听
        s.listen()

        print("服务器启动...")
        print(f"服务器IP:{self.HOST},端口号:{self.PORT}")
        while True:
            conn, addr = s.accept()
            self.online.append(conn)  # 保存已建立连接 conn 对象
            self.IP_PORT.append(conn.getpeername())  # 保存对应的IP/端口
            print(f'来自 {addr[0]}:{addr[1]} 的连接')
            '''
            只要有人连接, 就发送在线人员信息
            '''
            self.sendOnline()

            # 开启新线程读取消息
            t = Thread(target=self.receive, args=(conn, addr))
            t.start()

    def search_rival_conn(self, IP, Port):
        '''
        根据 IP 和 Port 利用对战关联表找到对手的套接字对象
        '''
        try:
            from_ = f"{IP}:{Port}"
            to_ = self.contact[from_].split(":")
            index = self.IP_PORT.index((to_[0], int(to_[1])))
            return self.online[index]
        except KeyError:
            print("找不到指定键")

    def search_conn(self, IP, Port):
        '''
        根据 IP 和 Port 寻找对应套接字对象
        '''
        index = self.IP_PORT.index((IP, Port))
        return self.online[index]

    def receive(self, conn, addr):
        '''
        接收客户端消息
        '''
        IP1 = addr[0]
        Port1 = addr[1]

        while True:
            try:
                res = conn.recv(1024)
                # 如果读入数据失败, 说明远程主机主动关闭连接
                if not res:
                    print(f'客户端 {IP1}:{Port1} 已断开连接...')
                    # 删掉对应的信息
                    self.online.remove(conn)
                    self.IP_PORT.remove(conn.getpeername())
                    # 关闭发送客户端
                    conn.close()
                    # 重新发送在线人员列表
                    self.sendOnline()
                    break
                else:
                    res_ = byte_to_json(res)

                    # 将收到的数据写入日志文件
                    self.write(ip=addr[0], port=addr[1], res=res_)

                    if "invite_OK" in res_:
                        IP2 = res_["info"]["IP"]
                        Port2 = res_["info"]["Port"]

                        c = self.search_conn(IP2, Port2)

                        if res_["invite_OK"]:
                            print(f"{IP1}:{Port1} 接受 {IP2}:{Port2} 对战")
                            # 建立对战关联表
                            vs_dict = {
                                f"{IP1}:{Port1}": f"{IP2}:{Port2}",
                                f"{IP2}:{Port2}": f"{IP1}:{Port1}"
                            }
                            self.contact.update(vs_dict)
                            s = json_to_byte({
                                "invite_OK": True,
                                "info": {
                                    "IP": IP1,
                                    "Port": Port1,
                                    "role": res_["info"]["role"]
                                }
                            })
                        else:
                            print(f"{IP1}:{Port1} 拒绝 {IP2}:{Port2} 对战")
                            s = json_to_byte({
                                "invite_OK": False,
                                "info": {
                                    "IP": IP1,
                                    "Port": Port1
                                }
                            })
                        c.send(s)
                    elif "invite" in res_:
                        IP2 = res_["invite"]["IP"]
                        Port2 = res_["invite"]["Port"]
                        print(f"{IP1}:{Port1} 邀请 {IP2}:{Port2} 对战")

                        c = self.search_conn(IP2, Port2)
                        s = json_to_byte(
                            {"invite": {
                                "IP": IP1,
                                "Port": Port1
                            }})
                        c.send(s)
                    else:
                        c = self.search_rival_conn(IP1, Port1)
                        c.send(res)

                        if "quit" in res_:
                            # 有用户退出了就删掉对战关联表对应内容
                            from_ = f"{IP1}:{Port1}"
                            self.contact.pop(from_)
            except ConnectionResetError:
                ip, port = conn.getpeername()
                print(f'客户端 {ip}:{port} 强制关闭了连接...')
                # 清除远程主机信息
                self.online.remove(conn)
                self.IP_PORT.remove(conn.getpeername())
                # 重新发送在线人员列表
                self.sendOnline()
                break

    def write(self, **kwarg):
        '''
        服务器收到的信息写入 txt 文件
        '''
        # 获取当前时间
        t = strftime("%Y-%m-%d %H:%M:%S", localtime())
        ip = kwarg["ip"]
        port = kwarg["port"]
        res = kwarg["res"]
        chatRecord = f"[{t}] # {ip}:{port}>\n{res}\n"
        # 在文末追加写入内容
        f = open("log.txt", "a", encoding="utf-8")
        f.write(chatRecord)

    def sendOnline(self):
        '''
        向客户端发送在线人员信息
        '''
        onlinePeople = json_to_byte({"online": self.IP_PORT})
        for conn in self.online:
            conn.send(onlinePeople)


s = server(getIPv4(), 50007)
s.start()
