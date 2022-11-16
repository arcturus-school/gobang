from tkinter import Canvas, messagebox, Tk, ttk
from .constants import R, r, tr, NO
import numpy as np
import string


# 棋盘类
class Board:
    def __init__(self, m: int, n: int, num: int):
        self.m = m  # m 行
        self.n = n  # n 列
        self.NUM = num  # 多少连子获胜
        self.ALLSTEPS: list[list[int]] = []  # 下棋步骤
        self.BG = "white"  # 棋盘颜色
        self.GAP = 30  # 棋盘格子边长
        self.WIDTH = self.GAP * (n - 1)  # 棋盘宽度
        self.HEIGHT = self.GAP * (m - 1)  # 棋盘高度
        self.MARGIN = 30  # 棋盘外边距
        self.IDs = []  # 各棋子 ID
        self.RADIUS = 10  # 棋子半径
        self.STEPTAILS: list[tuple[list[int], int]] = []  # 悔棋步骤
        self.BOARD = np.zeros([m, n], dtype=int)  # 棋盘数组
        self.ISFINISH: bool = False  # 本局游戏是否结束
        self.WHO: int = R["rival"]  # 默认黑棋先手
        self.CANVAS: Canvas | None = None
        self.WHOID: ttk.Label | None = None

    # 鼠标位置转成棋盘坐标
    def find_pos(self, x: int, y: int):
        """
        x 鼠标行坐标
        y 鼠标列坐标
        """
        gap = self.GAP
        half_gap = gap / 2
        x -= self.MARGIN
        y -= self.MARGIN
        i = x // gap + 1 if x % gap > half_gap else x // gap
        j = y // gap + 1 if y % gap > half_gap else y // gap

        # 只返回棋盘数组相符合的坐标
        if i >= 0 and i < self.m and j >= 0 and j < self.n:
            return i, j
        else:
            return None, None

    # 绘制棋盘
    def drawBoard(self, window: Tk):
        margin = self.MARGIN
        gap = self.GAP
        width = self.WIDTH + margin * 2
        height = self.HEIGHT + margin * 2

        self.CANVAS = Canvas(
            window,
            bg=self.BG,
            width=width,
            height=height,
        )

        self.CANVAS.grid(rowspan=6)
        self.CANVAS.config(highlightthickness=0)

        # 绘制格子
        for i in range(self.n):
            # 棋盘上 1 2 3 4 ...
            self.CANVAS.create_text(
                gap * i + margin,
                margin - 20,
                font=("Consolas", 10),
                text=NO[i],
            )

            col = (
                gap * i + margin,
                margin,
                gap * i + margin,
                self.HEIGHT + margin,
            )

            # 竖线
            self.CANVAS.create_line(col)

        for i in range(self.m):
            # 棋盘上 A B C D ...
            self.CANVAS.create_text(
                margin - 20,
                gap * i + margin,
                font=("Consolas", 10),
                text=string.ascii_uppercase[i],
            )

            row = (
                margin,
                gap * i + margin,
                self.WIDTH + margin,
                gap * i + margin,
            )

            # 横线
            self.CANVAS.create_line(row)

        # 棋盘中心锚点
        cx = (self.m // 2) * gap + margin
        cy = (self.n // 2) * gap + margin
        center = (cx - 3, cy - 3, cx + 3, cy + 3)
        self.CANVAS.create_oval(center, fill="black")

    # 落子
    def put(self, p: list[int], role: int, clear=True):
        """
        p: 落子坐标
        role: 落子方
        clear 是否清空悔棋步骤
        """

        if self.BOARD[p[0], p[1]] == R["empty"]:
            # 只有棋盘上该位置为空才能落子
            gap = self.GAP
            margin = self.MARGIN
            radius = self.RADIUS
            x = p[0] * gap + margin
            y = p[1] * gap + margin
            coords = (x - radius, y - radius, x + radius, y + radius)  # 棋子坐标

            id = self.CANVAS.create_oval(coords, fill=r[role])  # 根据角色选择颜色
            self.IDs.append(id)  # 保存节点 ID
            self.ALLSTEPS.append(p)  # 保存落子步骤
            self.BOARD[p[0], p[1]] = role  # 落子

            if clear:
                self.STEPTAILS.clear()  # 下棋后就不能悔棋了
                winList = self.succession([p[0], p[1]], role)

                if winList:
                    self.afterWin(winList)
                    self.isfinish = True  # 获胜了不能再继续落子了
                    self.WHOID["text"] = f"{tr[role]}方获胜"
                    self.WHOID["foreground"] = "red"
                    return

            self.reverse()  # 下一次棋翻转一次角色
            self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"
            self.draw()

    # 判断位置 p 是否获胜
    def succession(self, p: list[int], role: int):
        """
        p: 元素坐标, [i, j]
        role: AI or 玩家
        winList: 获胜坐标
        """
        # 四个方向(水平, 垂直, 左上到右下, 右上到左下)
        dir = [(0, 1), (1, 0), (1, 1), (1, -1)]
        # 棋子坐标
        x, y = p

        board = self.BOARD
        rlen = board.shape[0]  # 棋盘行数
        clen = board.shape[1]  # 棋盘列数

        for item in dir:
            # 连子位置
            winList = [[x, y]]
            for i in range(1, self.NUM):
                x_ = x + i * item[0]
                y_ = y + i * item[1]

                if (
                    x_ < rlen
                    and y_ < clen
                    and y_ >= 0
                    and board[x_, y_] == role  # noqa E501
                ):
                    winList.append([x_, y_])
                else:
                    # 不在范围内的直接退出循环
                    break

            for i in range(1, self.NUM):
                x_ = x - i * item[0]
                y_ = y - i * item[1]

                if x_ >= 0 and y_ >= 0 and y_ < clen and board[x_, y_] == role:
                    winList.append([x_, y_])
                else:
                    break

            if len(winList) >= self.NUM:
                print(f"获胜坐标: {winList}")
                return winList

    # 获胜后改变连子边框颜色
    def afterWin(self, winList: list[list[int]]):
        for i in winList:
            # allSteps 里坐标与 ids 元素一一对应
            index = self.ALLSTEPS.index(i)
            id = self.IDs[index]
            self.CANVAS.itemconfigure(id, outline="red", width=2)

    #  翻转角色
    def reverse(self):
        self.WHO = R["oneself"] if self.WHO == R["rival"] else R["rival"]

    # 重新开局
    def resume(self, first=True):
        for i in self.IDs:
            self.CANVAS.delete(i)

        self.ALLSTEPS.clear()  # 清空下棋步骤
        self.IDs.clear()  # 清空棋子 ID
        self.STEPTAILS.clear()  # 清空悔棋步骤
        self.ISFINISH = False  # 游戏未结束
        self.BOARD = np.zeros([self.m, self.n], dtype=int)  # 棋盘置空
        self.WHO = R["rival"]  # 恢复开局方
        self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"
        self.WHOID["foreground"] = "black"

        if not first:
            # 电脑先手, 重新开局还是下正中间
            self.put([7, 7], self.WHO)

    # 平局判断
    def draw(self):
        if (
            len(np.extract(self.BOARD == 0, self.BOARD)) == 0
            and not self.ISFINISH  # noqa E501
        ):
            self.WHOID["text"] = "平局"
            self.WHOID["foreground"] = "red"
            messagebox.showinfo(title="啊", message="平局了")
