from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import strftime, localtime
from src.utils.json_byte import json_to_byte, byte_to_json
from src.utils.get_ip import getIPv4


# 服务器
class server:
    def __init__(self, HOST: str, PORT: int) -> None:
        self.HOST = HOST  # 服务器 IP
        self.PORT = PORT  # 服务器端口
        self.online: list[socket] = []  # 连接玩家的套接字对象
        self.IP_PORT = []  # 与套接字对象对应的 ip 和端口列表
        self.contact = {}  # 玩家对战关联表

    # 开启服务器
    def start(self):
        s = socket(AF_INET, SOCK_STREAM)
        # 绑定服务器使用的端口和 IP 地址
        s.bind((self.HOST, self.PORT))
        # 服务器监听
        s.listen()

        print(f"服务器IP: {self.HOST}, 端口号: {self.PORT}")

        while True:
            conn, addr = s.accept()
            self.online.append(conn)  # 保存已建立连接 conn 对象
            self.IP_PORT.append(conn.getpeername())  # 保存对应的 IP 和端口

            print(f"来自 {addr[0]}:{addr[1]} 的连接")

            self.sendOnline()  # 只要有人连接, 就发送在线人员信息

            # 开启新线程读取消息
            t = Thread(target=self.receive, args=(conn, addr))
            t.start()

    # 根据 IP 和 Port 利用对战关联表找到对手的套接字对象
    def search_rival_conn(self, IP: str, Port: int):
        try:
            f = f"{IP}:{Port}"
            t = self.contact[f].split(":")
            index = self.IP_PORT.index((t[0], int(t[1])))
            return self.online[index]
        except Exception:
            print("找不到目标地址")

    # 根据 IP 和 Port 寻找对应套接字对象
    def search_conn(self, IP: str, Port: int):
        index = self.IP_PORT.index((IP, Port))
        return self.online[index]

    # 接收客户端消息
    def receive(self, conn: socket, addr):
        ip_1, port_1 = addr

        while True:
            try:
                res = conn.recv(1024)
                # 如果读入数据失败, 说明远程主机主动关闭连接
                if not res:
                    print(f"客户端 {ip_1}:{port_1} 已断开连接...")
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
                    self.write(ip=ip_1, port=port_1, res=res_)

                    if "invite_OK" in res_:
                        ip_2 = res_["info"]["IP"]
                        port_2 = res_["info"]["Port"]

                        c = self.search_conn(ip_2, port_2)

                        if res_["invite_OK"]:
                            print(f"{ip_1}:{port_1} 接受 {ip_2}:{port_2} 对战")

                            # 建立对战关联表
                            vs_dict = {
                                f"{ip_1}:{port_1}": f"{ip_2}:{port_2}",
                                f"{ip_2}:{port_2}": f"{ip_1}:{port_1}",
                            }

                            self.contact.update(vs_dict)
                            s = json_to_byte(
                                {
                                    "invite_OK": True,
                                    "info": {
                                        "IP": ip_1,
                                        "Port": port_1,
                                        "role": res_["info"]["role"],
                                    },
                                }
                            )
                        else:
                            print(f"{ip_1}:{port_1} 拒绝 {ip_2}:{port_2} 对战")
                            s = json_to_byte(
                                {
                                    "invite_OK": False,
                                    "info": {
                                        "IP": ip_1,
                                        "Port": port_1,
                                    },
                                }
                            )
                        c.send(s)
                    elif "invite" in res_:
                        ip_2 = res_["invite"]["IP"]
                        port_2 = res_["invite"]["Port"]

                        print(f"{ip_1}:{port_1} 邀请 {ip_2}:{port_2} 对战")

                        c = self.search_conn(ip_2, port_2)
                        s = json_to_byte(
                            {
                                "invite": {
                                    "IP": ip_1,
                                    "Port": port_1,
                                }
                            }
                        )
                        c.send(s)
                    else:
                        c = self.search_rival_conn(ip_1, port_1)
                        c.send(res)

                        if "quit" in res_:
                            # 有用户退出了就删掉对战关联表对应内容
                            self.contact.pop(f"{ip_1}:{port_1}")

            except ConnectionResetError:
                ip, port = conn.getpeername()
                print(f"客户端 {ip}:{port} 强制关闭了连接...")

                # 清除远程主机信息
                self.online.remove(conn)
                self.IP_PORT.remove(conn.getpeername())

                # 重新发送在线人员列表
                self.sendOnline()
                break

    # 服务器收到的信息写入 txt 文件
    def write(self, **kwarg):
        # 获取当前时间
        t = strftime("%Y-%m-%d %H:%M:%S", localtime())
        ip = kwarg["ip"]
        port = kwarg["port"]
        res = kwarg["res"]
        chatRecord = f"[{t}] # {ip}:{port}>\n{res}\n"
        # 在文末追加写入内容
        f = open("log.txt", "a", encoding="utf-8")
        f.write(chatRecord)

    # 向客户端发送在线人员信息
    def sendOnline(self):
        onlinePeople = json_to_byte({"online": self.IP_PORT})

        for conn in self.online:
            conn.send(onlinePeople)


if __name__ == "__main__":
    s = server(getIPv4(), 50007)
    s.start()
