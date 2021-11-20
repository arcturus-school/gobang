from tkinter import Tk, PhotoImage, Menu
from tkinter.constants import TOP
import tkinter.ttk as ttk
from Func.board import Board
from Func.client import Client
import webbrowser
import ctypes


def about():
    '''
    打开浏览器
    '''
    webbrowser.open("https://github.com/ICE99125/gobang.git")


def windowStyle(w):
    '''
    设置窗口样式
    '''
    # 标题
    w.title('五子棋')

    # 窗口背景
    w.configure(bg="#e6e6e6")

    # 图标
    w.iconbitmap("src/favicon.ico")

    # 调用 api 设置成由应用程序缩放
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    # 调用 api 获得当前的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

    # 设置缩放因子
    w.tk.call('tk', 'scaling', ScaleFactor / 75)


def HOME():
    '''
    主页
    '''
    home = Tk()
    windowStyle(home)

    p1 = PhotoImage(file="src/ai.png").subsample(3, 3)
    btn1 = ttk.Button(home, text='人机对战', width=10, image=p1, compound=TOP)
    btn1["command"] = lambda: AI(home)
    btn1.grid(padx=10, pady=10)

    p2 = PhotoImage(file="src/net.png").subsample(3, 3)
    btn2 = ttk.Button(home, text='联网对战', width=10, image=p2, compound=TOP)
    btn2["command"] = lambda: INVITE(home)
    btn2.grid(row=0, column=1, padx=10, pady=10)

    p3 = PhotoImage(file="src/go.png").subsample(3, 3)
    btn3 = ttk.Button(home, text='左右互博', width=10, image=p3, compound=TOP)
    btn3.grid(row=0, column=2, padx=10, pady=10)
    btn3["command"] = lambda: LOCAL(home)

    # 启动窗口
    home.mainloop()


def AI(h):
    '''
    人机对战
    '''
    h.destroy()
    ai = Tk()
    windowStyle(ai)


def INVITE(h):
    '''
    网络联机
    '''
    h.destroy()

    # 开启客户端
    client = Client("10.22.164.18", 50007)
    client.NET(HOME)


def LOCAL(h):
    '''
    左右互搏
    '''
    h.destroy()
    local = Tk()

    def save():
        '''
        保存棋盘
        '''
        pass

    # 菜单栏
    m = {
        "文件": {
            "保存": save,
            "退出": lambda: local.destroy()
        },
        "帮助": {
            "关于": about
        }
    }
    menu(local, m)
    windowStyle(local)
    # 新建一个棋盘对象
    b = Board(15, 15, 5)
    # 由于不能相互 import, 所以只能传入 HOME
    b.LOCAL(local, HOME)

    local.mainloop()


def menu(w, m):
    '''
    顶部菜单栏
    '''
    menubar = Menu(w)
    for i in m.items():
        a = Menu(menubar, tearoff=0)
        for j in i[1].items():
            a.add_command(label=j[0], command=j[1])
        menubar.add_cascade(label=i[0], menu=a)

    w['menu'] = menubar
