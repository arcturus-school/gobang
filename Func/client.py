from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from threading import Thread
import tkinter.ttk as ttk
from tkinter import Scrollbar, Listbox, messagebox, Tk
from tkinter.constants import END, FLAT, N, S, W, E, VERTICAL
from Func.board import Net_board
from Func.chat import Chat
from Func.json_byte import json_to_byte, byte_to_json
import random


def randomNum():
    '''
    随机开局
    我也不知道 1 和 2 要怎么才能随机
    '''
    # 随机生成包含 200 个 1~20 整数的列表
    list_ = [random.randint(1, 20) for _ in range(200)]
    # 随机抽取一个, 这个数如果是偶数...
    if random.choices(list_, k=1)[0] % 2 == 0:
        return 2
    else:
        return 1


# 客户端类
class Client:
    def __init__(self, HOST, PORT, myPort=None):
        self.HOST = HOST  # 服务器 IP
        self.PORT = PORT  # 服务器端口
        self.onlinePeople = {}  # 在线人员列表
        self.socket = socket(AF_INET, SOCK_STREAM)  # 创建套接字对象

        if myPort:
            self.socket.bind(("", myPort))  # 绑定客户端地址

    def send_chat(self):
        '''
        发送聊天信息
        '''
        send_data = self.chat.t2.get("0.0", "end")
        print(f"将发送的数据: {send_data}")
        # 要求输入不为空才能发送
        if send_data:
            # 向 ScrolledText 写入数据
            self.chat.writeToText(send_data, self.myIP, self.myPort)

            # 向服务器发送
            s = json_to_byte({"chat": send_data})
            self.socket.send(s)

    def sendPosition(self, p):
        '''
        发送坐标信息
        '''
        s = json_to_byte({"board": p})
        self.socket.send(s)

    def mouseClick(self, event):
        '''
        鼠标左键点击事件
        '''
        if not self.board.isfinish:
            x, y = self.board.find_pos(event.x, event.y)  # 获取落子坐标
            if x is not None and y is not None and self.board.who == self.role:
                '''
                坐标位于棋盘中且当前落子对象(board.who)是自己(role)时
                '''
                self.board.put([x, y], self.board.who)  # 落子
                self.sendPosition([x, y])

    def invite_window(self, HOME):
        '''
        邀请窗口
        '''
        def receive():
            '''
            接收服务器数据
            '''
            while True:
                try:
                    res = byte_to_json(self.socket.recv(1024))
                    if "online" in res:
                        self.onlinePeople = res["online"]
                        # 展示在线人数
                        self.onlineList.delete(0, END)  # 先清空原来的
                        for i in self.onlinePeople:
                            # 重新展示新的
                            self.onlineList.insert('end', f"{i[0]}:{i[1]}")
                    elif "chat" in res:
                        IP = self.rival_IP
                        Port = self.rival_Port
                        self.chat.writeToText(res["chat"], IP, Port)
                    elif "board" in res:
                        # 获取对方落子坐标
                        p = res["board"]
                        self.board.put(p, self.board.who)
                    elif "invite" in res:
                        IP = res["invite"]["IP"]
                        Port = res["invite"]["Port"]
                        accept = messagebox.askyesno(
                            message=f'是否接受 {IP}:{Port} 的对战邀请?',
                            icon='question',
                            title='对战邀请')
                        if accept:
                            print(f"接受了 {IP}:{Port} 的对战邀请")
                            # 保存对手信息
                            self.rival_IP = IP
                            self.rival_Port = Port
                            role = randomNum()  # 随机生成先后手
                            s = json_to_byte({
                                "invite_OK": True,
                                "info": {
                                    "IP": IP,
                                    "Port": Port,
                                    "role": role
                                }
                            })
                            self.socket.send(s)
                            '''
                            棋盘默认先手为 1
                            并且规定如果发送邀请方产生随机数 1, 则不做先手
                            '''
                            self.role = 2 if role == 1 else 1
                            nonlocal invite_panel
                            invite_panel.destroy()
                            self.vs_window(HOME)
                        else:
                            print(f"拒绝了 {IP}:{Port} 的对战邀请")
                            s = json_to_byte({
                                "invite_OK": False,
                                "info": {
                                    "IP": IP,
                                    "Port": Port
                                }
                            })
                            self.socket.send(s)
                    elif "invite_OK" in res:
                        IP = res["info"]["IP"]
                        Port = res["info"]["Port"]
                        if res["invite_OK"]:
                            # 如果对方同意对战
                            print(f"{IP}:{Port} 接受了对战邀请")
                            self.rival_IP = IP
                            self.rival_Port = Port
                            self.role = res["info"]["role"]
                            # 开启棋盘页面
                            invite_panel.destroy()
                            self.vs_window(HOME)
                        else:
                            # 如果被拒绝
                            print(f"{IP}:{Port} 拒绝了对战邀请")
                            messagebox.showinfo(title='嘤嘤嘤', message='被拒绝了')
                    elif "quit" in res:
                        messagebox.showinfo(title='哼哼哼', message='对方逃掉了')
                        # 把棋盘和聊天窗全部关闭
                        self.frame1.destroy()
                        self.frame2.destroy()
                        btn = ttk.Button(self.net, text="返回主页", command=quit)
                        btn.grid(pady=300, padx=300)
                        break
                    elif "undo" in res:
                        accept = messagebox.askyesno(message="是否同意对方悔棋?",
                                                     icon="question",
                                                     title="悔棋")
                        if accept:
                            s = json_to_byte({"undo_OK": True})
                            self.socket.send(s)
                            self.board.undo(0)
                        else:
                            s = json_to_byte({"undo_OK": False})
                            self.socket.send(s)
                    elif "undo_OK" in res:
                        if res["undo_OK"]:
                            # 对方接受悔棋
                            self.board.undo(1)
                        else:
                            messagebox.showinfo(title='嘤嘤嘤', message='对方不给悔棋')
                    elif "resume" in res:
                        # 收到重开请求
                        accept = messagebox.askyesno(message="是否同意对方请求?",
                                                     icon="question",
                                                     title="重新开局")
                        if accept:
                            s = json_to_byte({"resume_OK": True})
                            self.socket.send(s)
                            self.board.resume()
                        else:
                            s = json_to_byte({"resume_OK": False})
                            self.socket.send(s)
                    elif "resume_OK" in res:
                        # 收到重开请求反馈
                        if res["resume_OK"]:
                            self.board.resume()
                        else:
                            messagebox.showinfo(title='嘤嘤嘤', message='对方不想重开')
                except ConnectionAbortedError:
                    # socket 被 recv 阻塞过程中...
                    # 如果直接 socket.close() 会触发此异常
                    print("客户端被强制退出...")
                    break
                except OSError:
                    # 调用 socket.shutdown(SHUT_RDWR) 的后果
                    print("套接字被删除了...")
                    break

        def quit():
            '''
            返回主页
            '''
            try:
                self.socket.shutdown(SHUT_RDWR)
                self.socket.close()
            except OSError:
                print("套接字不存在, 可能因为连接超时啦")
            self.net.destroy()
            HOME()

        def invite():
            '''
            发送对战邀请
            '''
            index = self.onlineList.curselection()[0]
            rival_info = self.onlineList.get(index).split(":")  # 获取玩家选择的对手信息
            IP2 = rival_info[0]
            Port2 = int(rival_info[1])

            if IP2 == self.myIP and Port2 == self.myPort:
                messagebox.showinfo(title="提示", message="不可以和自己对战哦")
            else:
                print(f"邀请 {IP2}:{Port2} 进行对战...")
                s = json_to_byte({"invite": {"IP": IP2, "Port": Port2}})
                self.socket.send(s)

        self.net = Tk()
        self.net.title("在线列表")
        self.net.configure(bg="#e6e6e6")
        self.net.iconbitmap("src/favicon.ico")

        invite_panel = ttk.Frame(self.net)
        invite_panel.pack()

        # 创建一个选项表
        self.onlineList = Listbox(invite_panel, relief=FLAT)
        self.onlineList.grid(columnspan=2,
                             sticky=(N, W, E, S),
                             padx=(10, 0),
                             pady=(10, 0))

        # 创建一个滚动条
        s = Scrollbar(invite_panel, orient=VERTICAL)
        s.grid(column=2, row=0, sticky=(N, S), padx=(0, 10), pady=(10, 0))

        # 绑定选项表上下滚动事件
        s["command"] = self.onlineList.yview
        self.onlineList['yscrollcommand'] = s.set
        invite_panel.grid_columnconfigure(0, weight=1)
        invite_panel.grid_rowconfigure(0, weight=1)

        # 创建两个按钮
        self.btn1 = ttk.Button(invite_panel, text="邀请", command=invite)
        self.btn1.grid(row=1, column=0, pady=5, padx=(10, 5))
        btn2 = ttk.Button(invite_panel, text="返回", command=quit)
        btn2.grid(row=1, column=1, pady=5, padx=(5, 0))

        try:
            # 连接服务器
            self.socket.connect((self.HOST, self.PORT))
            self.myIP = self.socket.getsockname()[0]  # 本机 IP
            self.myPort = self.socket.getsockname()[1]  # 本机端口
            # 开启一个线程用于接收服务端消息
            t1 = Thread(target=receive)
            t1.start()
        except ConnectionRefusedError:
            print("服务器连接超时...")
            self.onlineList.insert('end', "服务器连接超时...")
            self.btn1['state'] = "disable"  # 连接服务器超时则禁止邀请

        self.net.protocol("WM_DELETE_WINDOW", quit)
        self.net.mainloop()

    def vs_window(self, HOME):
        '''
        对战窗口
        '''
        self.net.title(f"{self.myIP}:{self.myPort}")

        s = ttk.Style()
        s.configure('TFrame', background="#e6e6e6")
        self.frame1 = ttk.Frame(self.net, padding=10, style='TFrame')
        self.frame1.grid(row=0, column=0)
        self.frame2 = ttk.Frame(self.net, padding=10, style='TFrame')
        self.frame2.grid(row=0, column=1)

        # 创建棋盘界面
        self.board = Net_board(15, 15, 5, self.role)
        self.board.start(self.net, self.frame1, HOME, self.socket)

        # 创建聊天界面
        self.chat = Chat()
        self.chat.interfaces(self.frame2)

        # 棋盘绑定鼠标点击事件
        self.board.canvas.bind("<Button-1>", self.mouseClick)

        # 发送按钮绑定事件
        self.chat.button["command"] = self.send_chat
