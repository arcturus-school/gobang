from tkinter import Tk, PhotoImage, IntVar, StringVar, messagebox
from tkinter.constants import TOP
from Func.board import Oneself_board, AI_board
from Func.client import Client
from Func.page_style import windowStyle
from Func.get_ip import getIPv4
import tkinter.ttk as ttk
from re import compile


def select(board, depth=None, role=None):
    '''
    选择棋盘大小
    '''
    selected = Tk()
    windowStyle(selected, "选择棋盘")
    list = tuple([i for i in range(9, 20)])

    ttk.Label(selected, text="行", background="#e6e6e6").grid(pady=5)
    r = IntVar()
    row = ttk.Combobox(selected, textvariable=r)
    row.state(["readonly"])
    row['values'] = list
    row.set(9)
    row.grid(row=1, column=0, padx=10, pady=20)

    ttk.Label(selected, text="列", background="#e6e6e6").grid(row=0,
                                                             column=1,
                                                             pady=5)
    c = IntVar()
    col = ttk.Combobox(selected, textvariable=c)
    col.state(["readonly"])
    col['values'] = list
    col.set(9)
    col.grid(row=1, column=1, padx=10, pady=20)

    def start():
        selected.destroy()
        # 新建一个棋盘对象
        print(depth, role)
        if depth and role is not None:
            b = board(r.get(), c.get(), 5, depth, role)
        else:
            b = board(r.get(), c.get(), 5)
        b.start(HOME)

    button = ttk.Button(selected, text='开始游戏', command=start)
    button.grid(row=2, column=0, columnspan=2, pady=20)

    def quit():
        selected.destroy()
        HOME()

    # 监听窗口关闭事件
    selected.protocol("WM_DELETE_WINDOW", quit)
    selected.mainloop()


def HOME():
    '''
    主页
    '''
    home = Tk()
    windowStyle(home)

    p1 = PhotoImage(file="src/ai.png").subsample(3, 3)
    btn1 = ttk.Button(home, text='人机对战', width=10, image=p1, compound=TOP)
    btn1["command"] = lambda: ai(home)
    btn1.grid(padx=10, pady=10)

    p2 = PhotoImage(file="src/net.png").subsample(3, 3)
    btn2 = ttk.Button(home, text='联网对战', width=10, image=p2, compound=TOP)
    btn2["command"] = lambda: play_online(home)
    btn2.grid(row=0, column=1, padx=10, pady=10)

    p3 = PhotoImage(file="src/go.png").subsample(3, 3)
    btn3 = ttk.Button(home, text='左右互博', width=10, image=p3, compound=TOP)
    btn3.grid(row=0, column=2, padx=10, pady=10)
    btn3["command"] = lambda: amuse_oneself(home)

    # 启动窗口
    home.mainloop()


def ai(h):
    '''
    人机对战
    '''
    h.destroy()
    select_mode()


def quit(root):
    '''返回主页'''
    root.destroy()
    HOME()


def select_mode():
    '''
    选择难度
    '''
    root = Tk()
    windowStyle(root, "模式")

    p1 = PhotoImage(file="src/easy.png").subsample(3, 3)
    btn1 = ttk.Button(root, text='简单', image=p1, compound=TOP)
    btn1["command"] = lambda: who_first(root, 4)
    btn1.grid(padx=10, pady=10)

    p2 = PhotoImage(file="src/medium.png").subsample(3, 3)
    btn2 = ttk.Button(root, text='中等', image=p2, compound=TOP)
    btn2["command"] = lambda: who_first(root, 6)
    btn2.grid(row=0, column=1, padx=10, pady=10)

    p3 = PhotoImage(file="src/advance.png").subsample(3, 3)
    btn3 = ttk.Button(root, text='困难', image=p3, compound=TOP)
    btn3.grid(row=0, column=2, padx=10, pady=10)
    btn3["command"] = lambda: who_first(root, 8)

    root.protocol("WM_DELETE_WINDOW", lambda: quit(root))
    root.mainloop()


def who_first(w, depth):
    '''
    先后手选择
    '''
    w.destroy()
    root = Tk()
    windowStyle(root, "谁先开局")

    p1 = PhotoImage(file="src/com.png").subsample(3, 3)
    btn1 = ttk.Button(root, text='电脑', width=10, image=p1, compound=TOP)
    btn1["command"] = lambda: ai_start(root, depth, False)
    btn1.grid(padx=10, pady=10)

    p2 = PhotoImage(file="src/player.png").subsample(3, 3)
    btn2 = ttk.Button(root, text='玩家', width=10, image=p2, compound=TOP)
    btn2["command"] = lambda: ai_start(root, depth, True)
    btn2.grid(row=0, column=1, padx=10, pady=10)

    root.protocol("WM_DELETE_WINDOW", lambda: quit(root))
    root.mainloop()


def ai_start(w, depth, role):
    '''
    进入游戏
    '''
    w.destroy()
    select(AI_board, depth, role)


def play_online(h):
    '''
    网络联机
    '''
    h.destroy()
    input_ip = Tk()
    windowStyle(input_ip, "服务器地址")

    ttk.Label(input_ip, text="服务器IP地址", background="#e6e6e6").grid(pady=5,
                                                                   padx=10)

    server_ip = StringVar()
    ip = ttk.Entry(input_ip, textvariable=server_ip, width=30)
    ip.insert(0, getIPv4())  # 插入默认值
    ip.grid(row=1, padx=10)

    def connect():
        r = r"25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d"
        RegEx = compile(f"^({r}).({r}).({r}).({r})$")
        ip_ = ip.get()

        if RegEx.search(ip_):
            # 开启客户端
            input_ip.destroy()
            client = Client(ip_, 50007)
            client.invite_window(HOME)
        else:
            messagebox.showinfo(title='(╯°□°）╯', message='输个对的IP啊')

    button = ttk.Button(input_ip, text='连接', command=connect)
    button.grid(row=2, pady=20)

    def quit():
        input_ip.destroy()
        HOME()

    # 监听窗口关闭事件
    input_ip.protocol("WM_DELETE_WINDOW", quit)
    input_ip.mainloop()


def amuse_oneself(h):
    '''
    普通模式, 左右手互搏
    '''
    h.destroy()
    select(Oneself_board)
