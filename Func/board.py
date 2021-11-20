from tkinter import Canvas, messagebox, ttk
from socket import SHUT_RDWR
import numpy as np
import string
import json

R = {"empty": 0, "rival": 1, "oneself": 2}  # 角色表
r = {1: "black", 2: "white"}  # 执子颜色
tr = {1: "黑", 2: "白"}  # 执子方
NO = [x for x in range(1, 20)]  # 1 到 20 列表


# 棋盘类
class Board:
    def __init__(self, m, n, num, role=None):
        '''
        :param m: m 行
        :param n: n 列
        '''
        self.m = m
        self.n = n
        self._bg = "white"  # 棋盘颜色
        self._gap = 30  # 棋盘格子边长
        self._width = self._gap * (n - 1)  # 棋盘宽度
        self._height = self._gap * (m - 1)  # 棋盘高度
        self._margin = 30  # 棋盘外边距
        self._allStep = []  # 下棋步骤
        self._id = []  # 各棋子 ID
        self._radius = 10  # 棋子半径
        self._stepsTail = []  # 悔棋步骤
        self._board = np.zeros([m, n], dtype=int)  # 棋盘数组
        self._isfinish = False  # 本局游戏是否结束
        self._num = num  # 多少连子获胜
        self.who = R["rival"]  # 默认黑棋先手
        self.IamWho = role  # 我是先手还是后手?

    def find_pos(self, x, y):
        '''
        鼠标位置转成棋盘坐标
        :param x 鼠标行坐标
        :param y 鼠标列坐标
        '''
        gap = self._gap
        half_gap = gap / 2
        x -= self._margin
        y -= self._margin
        i = x // gap + 1 if x % gap > half_gap else x // gap
        j = y // gap + 1 if y % gap > half_gap else y // gap

        # 只返回棋盘数组相符合的坐标
        if i >= 0 and i < self.m and j >= 0 and j < self.n:
            return i, j
        else:
            return None, None

    def drawBoard(self, window):
        '''
        绘制棋盘
        :param window: tkinter Surface 对象
        '''
        margin = self._margin
        gap = self._gap
        width = self._width + margin * 2
        height = self._height + margin * 2
        self._canvas = Canvas(window, bg=self._bg, width=width, height=height)
        self._canvas.grid(rowspan=6)
        self._canvas.config(highlightthickness=0)

        # 绘制格子
        for i in range(self.n):
            # 棋盘上 1 2 3 4 ...
            self._canvas.create_text(gap * i + margin,
                                     margin - 20,
                                     font=("Consolas", 10),
                                     text=NO[i])
            col = (gap * i + margin, margin, gap * i + margin,
                   self._height + margin)
            # 竖线
            self._canvas.create_line(col)

        for i in range(self.m):
            # 棋盘上 A B C D ...
            self._canvas.create_text(margin - 20,
                                     gap * i + margin,
                                     font=("Consolas", 10),
                                     text=string.ascii_uppercase[i])
            row = (margin, gap * i + margin, self._width + margin,
                   gap * i + margin)
            # 横线
            self._canvas.create_line(row)

        # 棋盘中心锚点
        cx = (self.m // 2) * gap + margin
        cy = (self.n // 2) * gap + margin
        center = (cx - 3, cy - 3, cx + 3, cy + 3)
        self._canvas.create_oval(center, fill="black")

    def put(self, p, role, clear=True):
        '''
        落子
        :param p: 落子坐标
        :param role: 落子方
        :param clear 是否清空悔棋步骤
        '''
        if self._board[p[0], p[1]] == R["empty"]:
            # 只有棋盘上该位置为空才能落子
            gap = self._gap
            margin = self._margin
            radius = self._radius
            x = p[0] * gap + margin
            y = p[1] * gap + margin
            coords = (x - radius, y - radius, x + radius, y + radius)  # 棋子坐标
            id = self._canvas.create_oval(coords, fill=r[role])  # 根据角色选择颜色
            self._id.append(id)  # 保存节点 ID
            self._allStep.append(p)  # 保存落子步骤
            self._board[p[0], p[1]] = role  # 落子

            if clear:
                self._stepsTail.clear()  # 下棋后就不能悔棋了
                winList = self.succession([p[0], p[1]], self.who)
                if winList:
                    self.afterWin(winList)
                    self._isfinish = True  # 获胜了不能再继续落子了
                    now = tr[self.who]
                    self.whoID["text"] = f'{now}方获胜'
                    self.whoID["foreground"] = "red"
                    return

            self.reverse()  # 下一次棋翻转一次角色
            now = tr[self.who]
            self.whoID["text"] = f'轮到{now}方执棋'

    def succession(self, p, role):
        '''
        判断位置 p 是否获胜
        :param board: 二维数组
        :param p: 元素坐标, [i, j]
        :param role: AI or 玩家
        :return winList: 获胜坐标
        '''
        # 四个方向(水平, 垂直, 左上到右下, 右上到左下)
        dir = [(0, 1), (1, 0), (1, 1), (1, -1)]
        # 棋子坐标
        x = p[0]
        y = p[1]
        board = self._board
        rlen = board.shape[0]  # 棋盘行数
        clen = board.shape[1]  # 棋盘列数

        for item in dir:
            # 连子位置
            winList = [[x, y]]
            for i in range(1, self._num):
                x_ = x + i * item[0]
                y_ = y + i * item[1]
                if (x_ < rlen and y_ < clen and y_ >= 0
                        and board[x_, y_] == role):
                    winList.append([x_, y_])
                else:
                    # 不在范围内的直接退出
                    break

            for i in range(1, self._num):
                x_ = x - i * item[0]
                y_ = y - i * item[1]
                if x_ >= 0 and y_ >= 0 and y_ < clen and board[x_, y_] == role:
                    winList.append([x_, y_])
                else:
                    break
            if len(winList) >= self._num:
                return winList

    def afterWin(self, p):
        '''
        获胜后改变连子的边框
        p: 获胜坐标列表
        '''
        print(self._allStep)
        print(p)
        for i in p:
            # _allStep 里坐标与 _id 元素一一对应
            index = self._allStep.index(i)
            id = self._id[index]
            self._canvas.itemconfigure(id, outline="red", width=2)

    def reverse(self):
        '''
        翻转角色
        '''
        self.who = R["oneself"] if self.who == R["rival"] else R["rival"]

    def resume(self):
        '''
        重新开局
        '''
        for i in self._id:
            self._canvas.delete(i)
        self._allStep = []  # 清空下棋步骤
        self._id = []  # 清空棋子 ID
        self._stepsTail = []  # 清空悔棋步骤
        self._isfinish = False  # 游戏未结束
        self._board = np.zeros([self.m, self.n], dtype=int)  # 棋盘置空
        self.who = R["rival"]  # 默认黑方/对手开局
        now = tr[self.who]
        self.whoID["text"] = f'轮到{now}方执棋'
        self.whoID["foreground"] = "black"

    def sidebar(self, w, undo, quit, resume=None, forward=None):
        '''
        侧边栏
        '''
        # 我是哪一方？
        if self.IamWho:
            me = ttk.Label(w,
                           text=f"我是{tr[self.IamWho]}方",
                           background="#e6e6e6",
                           width=12,
                           anchor="center")
            me.grid(row=1, column=1, padx=5)
        # 执子提示
        now = tr[self.who]
        self.whoID = ttk.Label(w,
                               text=f'轮到{now}方执棋',
                               background="#e6e6e6",
                               width=12,
                               anchor="center")
        self.whoID.grid(row=0, column=1, padx=5)

        # 四个按钮
        button1 = ttk.Button(w, text='悔棋', command=undo, width=5)
        button1.grid(row=2, column=1, padx=5)
        if forward:
            # 对战模式不允许撤销悔棋...
            # 主要是太麻烦了 /(ㄒoㄒ)/~~
            button2 = ttk.Button(w, text='撤销', command=forward, width=5)
        else:
            button2 = ttk.Button(w, text='撤销', width=5)
            button2["state"] = "disable"
        button2.grid(row=3, column=1, padx=5)
        if resume:
            button2 = ttk.Button(w, text='重开', command=resume, width=5)
        else:
            button2 = ttk.Button(w, text='重开', command=self.resume, width=5)
        button2.grid(row=4, column=1, padx=5)
        button2 = ttk.Button(w, text='返回', command=quit, width=5)
        button2.grid(row=5, column=1, padx=5)

    def LOCAL(self, w, HOME):
        '''
        左右互博
        '''
        def undo():
            '''
            悔棋
            '''
            if len(self._allStep) == 0 or self._isfinish:
                messagebox.showinfo(title='提示', message='悔不了了哦')
            else:
                # 获取并删除最后一步棋对应画布 ID
                s = self._id.pop()
                # 获取并删除最后一步棋对应的坐标
                p = self._allStep.pop()
                # 最后一步棋是谁下的
                role = self._board[p[0], p[1]]
                self._board[p[0], p[1]] = R["empty"]  # 将棋盘置空
                # 删除画布上对应节点
                self._canvas.delete(s)
                # 把悔棋的步骤保存起来
                self._stepsTail.append([p, role])
                self.reverse()  # 悔棋一次翻转一次角色
                now = tr[self.who]
                self.whoID["text"] = f'轮到{now}方执棋'

        def forward():
            '''
            撤销悔棋
            '''
            if len(self._stepsTail) == 0:
                messagebox.showinfo(title='嘤嘤嘤', message='您还没有悔过棋呢')
            else:
                # 删除悔棋步骤, 并获取悔棋坐标
                p, r = self._stepsTail.pop()
                # 利用坐标重新下, 并且不需要清空悔棋步骤
                self.put(p, r, False)

        def quit():
            '''
            离开
            '''
            w.destroy()
            HOME()

        def mouseClick(event):
            '''
            鼠标左键点击事件
            '''
            if not self._isfinish:
                x, y = self.find_pos(event.x, event.y)  # 获取落子坐标
                if x is not None and y is not None:
                    self.put((x, y), self.who)  # 落子

        self.drawBoard(w)  # 绘制棋盘
        self.sidebar(w, undo, quit, forward)  # 生成侧边栏
        # 给画布绑定鼠标左键
        self._canvas.bind("<Button-1>", mouseClick)

    def AI(self, w, HOME):
        '''
        人机对战
        '''
        def undo():
            '''
            悔棋
            '''
            pass

        def forward():
            '''
            撤销悔棋
            '''
            pass

        def quit():
            pass

    def NET(self, net, frame, HOME, socket):
        '''
        联网对战
        '''
        def wantundo():
            '''
            悔棋请求
            '''
            s = json.dumps({"undo": True}).encode('gb2312')

            socket.send(s)

        def resume():
            '''重新开局请求'''
            s = json.dumps({"resume": True}).encode('gb2312')

            socket.send(s)

        def quit():
            q = json.dumps({"quit": True}).encode('gb2312')
            socket.send(q)
            socket.shutdown(SHUT_RDWR)
            socket.close()
            net.destroy()
            HOME()

        self.drawBoard(frame)  # 绘制棋盘
        self.sidebar(frame, wantundo, quit, resume)  # 生成侧边栏

        net.protocol("WM_DELETE_WINDOW", quit)

    def undo1(self):
        '''
        网络对战悔棋操作
        争对悔棋方
        '''
        def a():
            # 获取并删除最后一步棋对应画布 ID
            s = self._id.pop()
            # 获取并删除最后一步棋对应的坐标
            p = self._allStep.pop()
            self._board[p[0], p[1]] = R["empty"]  # 将棋盘该位置置空
            # 删除画布上对应节点
            self._canvas.delete(s)
            self.reverse()  # 悔棋一次翻转一次角色
            now = tr[self.who]
            self.whoID["text"] = f'轮到{now}方执棋'

        if len(self._allStep) == 0 or self._isfinish:
            messagebox.showinfo(title='提示', message='悔不了了哦')
        elif self.who == self.IamWho:
            '''如果当前是自己下棋, 则悔棋两步'''
            for _ in range(2):
                a()
        else:
            '''如果当前是对方下棋, 则悔棋一步'''
            a()

    def undo2(self):
        '''
        网络对战悔棋操作
        争对同意悔棋方
        '''
        def a():
            # 获取并删除最后一步棋对应画布 ID
            s = self._id.pop()
            # 获取并删除最后一步棋对应的坐标
            p = self._allStep.pop()
            self._board[p[0], p[1]] = R["empty"]  # 将棋盘该位置置空
            # 删除画布上对应节点
            self._canvas.delete(s)
            self.reverse()  # 悔棋一次翻转一次角色
            now = tr[self.who]
            self.whoID["text"] = f'轮到{now}方执棋'

        if len(self._allStep) == 0 or self._isfinish:
            messagebox.showinfo(title='提示', message='悔不了了哦')
        elif self.who == self.IamWho:
            '''如果当前是自己下棋, 则悔棋两步'''
            a()
        else:
            '''如果当前是对方下棋, 则悔棋一步'''
            for _ in range(2):
                a()
