from tkinter import Menu, Tk
import webbrowser
import ctypes


# 设置窗口样式
def windowStyle(
    w: Tk,
    title="五子棋",
    bg="#e6e6e6",
    ico="src/assets/favicon.ico",
):
    # 标题
    w.title(title)

    # 窗口背景
    w.configure(bg=bg)

    # 图标
    w.iconbitmap(ico)

    # 调用 api 设置成由应用程序缩放
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    # 调用 api 获得当前的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

    # 设置缩放因子
    w.tk.call("tk", "scaling", ScaleFactor / 75)


# 顶部菜单栏
def menu(w: Tk, m: dict):
    menubar = Menu(w)
    for i in m.items():
        a = Menu(menubar, tearoff=0)
        for j in i[1].items():
            a.add_command(label=j[0], command=j[1])
        menubar.add_cascade(label=i[0], menu=a)

    w["menu"] = menubar


# 打开浏览器
def about():
    webbrowser.open("https://github.com/ICE99125/gobang.git")
