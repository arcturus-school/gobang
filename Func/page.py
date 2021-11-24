from tkinter import Tk, PhotoImage
from tkinter.constants import TOP
from Func.board import Oneself_board, AI_board
from Func.client import Client
from Func.page_style import windowStyle
import tkinter.ttk as ttk


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
    b = AI_board(15, 15, 5, depth, role)
    b.start(HOME)


def play_online(h):
    '''
    网络联机
    '''
    h.destroy()

    # 开启客户端
    client = Client("10.22.164.18", 50007)
    client.invite_window(HOME)


def amuse_oneself(h):
    '''
    普通模式, 左右手互搏
    '''
    h.destroy()
    # 新建一个棋盘对象
    b = Oneself_board(15, 15, 5)
    b.start(HOME)