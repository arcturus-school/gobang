# TCP 协议
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
# 多线程
from threading import Thread
# GUI
import tkinter.ttk as ttk
from tkinter import Scrollbar, Listbox, messagebox, Tk
from tkinter.constants import END, FLAT, N, S, W, E, VERTICAL
from Func.board import Board
from Func.chat import Chat

import json
import random


def randomNum():
    '''
    随机开局
    只能说是野路子了 🤣🤣
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
        self.role = 0  # 默认无对手...
        self.s = socket(AF_INET, SOCK_STREAM)  # 创建套接字对象

        if myPort:
            self.s.bind(("", myPort))  # 绑定客户端地址

    def quit(self):
        '''
        结束进程
        '''
        try:
            self.s.shutdown(SHUT_RDWR)  # 关闭接收与发送
            self.s.close()  # 关闭 TCP 连接
        except OSError:
            print("套接字不存在, 因为连接超时啦")

    def sendChat(self, event):
        '''
        发送聊天信息
        '''
        sendData = self.chat.t2.get("0.0", "end")
        print(sendData)
        # 要求输入不为空
        if sendData:
            # 向 ScrolledText 写入数据
            self.chat.writeToText(sendData, self.myIP, self.myPort)

            # 向服务器发送数据
            a = {"chat": sendData}
            s = json.dumps(a).encode('gb2312')
            self.s.send(s)

    def sendPosition(self, p):
        '''
        发送坐标信息
        '''
        # 向服务器发送数据
        data = {"board": p}
        data = json.dumps(data).encode('gb2312')
        self.s.send(data)

    def mouseClick(self, event):
        '''
        鼠标左键点击事件
        '''
        if not self.board._isfinish:
            x, y = self.board.find_pos(event.x, event.y)  # 获取落子坐标
            # 只有能落子时才落子
            if x is not None and y is not None and self.board.who == self.role:
                self.board.put([x, y], self.board.who)  # 落子
                self.sendPosition([x, y])

    def NET(self, HOME):
        '''
        展示在线人数
        '''
        def receive():
            '''
            获取在线人员详细地址
            '''
            while True:
                try:
                    res = self.s.recv(1024)
                    data = json.loads(res.decode('gb2312'))
                    if "online" in data:
                        # 如果是在线人数
                        self.onlinePeople = data["online"]
                        # 展示在线人数
                        self.onlineList.delete(0, END)  # 先清空原来的
                        for i in self.onlinePeople:
                            # 重新展示新的
                            self.onlineList.insert('end', f"{i[0]}:{i[1]}")
                    elif "chat" in data:
                        content = data["chat"]["content"]
                        IP = data["chat"]["IP"]
                        PORT = data["chat"]["PORT"]
                        self.chat.writeToText(content, IP, PORT)
                    elif "board" in data:
                        # 对方落子
                        p = data["board"]
                        self.board.put(p, self.board.who)
                    elif "invite" in data:
                        # 如果是对战请求
                        info = data["invite"]
                        IP = info["IP"]
                        PORT = info["port"]
                        accept = messagebox.askyesno(
                            message=f'是否接受{IP}:{PORT}的对战邀请?',
                            icon='question',
                            title='对战邀请')
                        if accept:
                            print(f"接受了{IP}:{PORT}的对战邀请")
                            role = randomNum()  # 对手是先手还是后手
                            s = json.dumps({
                                "invite_OK": {
                                    "IP": IP,
                                    "port": PORT,
                                    "role": role
                                }
                            }).encode('gb2312')

                            self.s.send(s)
                            # 如果 role == 1 说明对手是先手
                            # 因此我方为 2
                            self.role = 2 if role == 1 else 1
                            nonlocal listPanel
                            listPanel.destroy()
                            self.NET_Board(HOME)
                        else:
                            print(f"拒绝了{IP}:{PORT}的对战邀请")
                            s = json.dumps({
                                "refuse": {
                                    "IP": IP,
                                    "port": PORT
                                }
                            }).encode('gb2312')
                            self.s.send(s)
                    elif "invite_OK" in data:
                        # 如果接收到同意对战
                        self.role = data["invite_OK"]["role"]
                        # 开启棋盘页面
                        listPanel.destroy()
                        self.NET_Board(HOME)
                    elif "refuse" in data:
                        # 如果被拒绝
                        messagebox.showinfo(title='嘤嘤嘤', message='被拒绝了')
                    elif "quit" in data:
                        messagebox.showinfo(title='哼哼哼', message='对方逃掉了')
                        # 把棋盘和聊天窗全部关闭
                        self.frame1.destroy()
                        self.frame2.destroy()
                        btn = ttk.Button(self.net, text="返回主页", command=quit)
                        btn.grid(pady=300, padx=300)
                        break
                    elif "undo" in data:
                        accept = messagebox.askyesno(message="是否同意对方悔棋?",
                                                     icon="question",
                                                     title="悔棋")
                        if accept:
                            s = json.dumps({"undo_OK": True}).encode('gb2312')
                            self.s.send(s)
                            self.board.undo2()
                        else:
                            s = json.dumps({"undo_OK": False}).encode('gb2312')
                            self.s.send(s)
                    elif "undo_OK" in data:
                        if data["undo_OK"]:
                            self.board.undo1()
                        else:
                            messagebox.showinfo(title='嘤嘤嘤', message='对方不给悔棋')
                    elif "resume_OK" in data:
                        if data["resume_OK"]:
                            self.board.resume()
                        else:
                            messagebox.showinfo(title='嘤嘤嘤', message='对方不想重开')
                    elif "resume" in data:
                        accept = messagebox.askyesno(message="对方询问是否重新开局?",
                                                     icon="question",
                                                     title="重新开局")
                        if accept:
                            s = json.dumps({
                                "resume_OK": True
                            }).encode('gb2312')
                            self.s.send(s)
                            self.board.resume()
                        else:
                            s = json.dumps({
                                "resume_OK": False
                            }).encode('gb2312')
                            self.s.send(s)
                except ConnectionAbortedError:
                    # socket 被 recv 阻塞过程中...
                    # 如果直接 socket.close() 会触发此异常
                    print("客户端强制退出...")
                    break
                except OSError:
                    # 调用 socket.shutdown(SHUT_RDWR) 的后果
                    print("套接字已经被删除了...")
                    break

        def quit():
            '''
            返回主页
            '''
            try:
                self.s.shutdown(SHUT_RDWR)
                self.s.close()
            except OSError:
                print("关闭套接字失败, 因为未连接至服务器...")
            self.net.destroy()
            HOME()

        def invite():
            '''
            发送对战邀请
            '''
            index = self.onlineList.curselection()[0]
            info = self.onlineList.get(index)

            if info == f"{self.myIP}:{self.myPort}":
                messagebox.showinfo(title='提示', message='不可以和自己对战哦')
            else:
                print(f"邀请{info}对战...")
                info = info.split(":")
                data = json.dumps({
                    "invite": {
                        "IP": info[0],
                        "port": int(info[1])
                    }
                }).encode('gb2312')

                self.s.send(data)

        self.net = Tk()  # 保存客户端面版
        self.net.title("在线列表")
        self.net.configure(bg="#e6e6e6")
        self.net.iconbitmap("src/favicon.ico")

        listPanel = ttk.Frame(self.net)
        listPanel.pack()

        self.onlineList = Listbox(listPanel, relief=FLAT)
        self.onlineList.grid(columnspan=2,
                             sticky=(N, W, E, S),
                             padx=(10, 0),
                             pady=(10, 0))

        # 创建一个滚动条, 并可以上下滚动 Listbox
        s = Scrollbar(listPanel,
                      orient=VERTICAL,
                      command=self.onlineList.yview)
        s.grid(column=2, row=0, sticky=(N, S), padx=(0, 10), pady=(10, 0))

        self.onlineList['yscrollcommand'] = s.set
        listPanel.grid_columnconfigure(0, weight=1)
        listPanel.grid_rowconfigure(0, weight=1)

        self.btn1 = ttk.Button(listPanel, text="邀请", command=invite)
        self.btn1.grid(row=1, column=0, pady=5, padx=(10, 5))

        btn2 = ttk.Button(listPanel, text="返回", command=quit)
        btn2.grid(row=1, column=1, pady=5, padx=(5, 0))

        try:
            # 连接服务器
            self.s.connect((self.HOST, self.PORT))
            self.myPort = self.s.getsockname()[1]  # 本机端口
            self.myIP = self.s.getsockname()[0]  # 本机IP
            # 开启一个线程用于接收服务端消息
            t1 = Thread(target=receive)
            t1.start()
        except ConnectionRefusedError:
            print("服务器连接超时...")
            self.onlineList.insert('end', "服务器连接超时...")
            self.btn1['state'] = "disable"

        self.net.mainloop()

    def NET_Board(self, HOME):
        '''
        进入联机界面
        '''
        self.net.title('五子棋')

        # 左右布局
        s = ttk.Style()
        s.configure('TFrame', background="#e6e6e6")
        self.frame1 = ttk.Frame(self.net, padding=10, style='TFrame')
        self.frame1.grid(row=0, column=0)
        self.frame2 = ttk.Frame(self.net, padding=10, style='TFrame')
        self.frame2.grid(row=0, column=1)

        # 创建棋盘界面
        self.board = Board(15, 15, 5, self.role)
        self.board.NET(self.net, self.frame1, HOME, self.s)

        # 创建聊天界面
        self.chat = Chat()
        self.chat.interfaces(self.frame2)

        # 棋盘绑定鼠标点击事件
        self.board._canvas.bind("<Button-1>", self.mouseClick)

        # 发送按钮绑定事件
        self.chat.button.bind("<Button-1>", self.sendChat)
