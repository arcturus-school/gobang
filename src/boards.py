from tkinter import messagebox, ttk, Tk
from socket import SHUT_RDWR
import numpy as np

from .ai.zobrist import Zobrist

from .constants import S, C, R, tr

from .utils import json_to_byte, windowStyle, menu, about

from .board import Board


# 左右手互博
class Oneself_board(Board):
    def __init__(self, m, n, num):
        super().__init__(m, n, num)
        self.FIRST = False

    # 悔棋
    def undo(self):
        if len(self.ALLSTEPS) == 0:
            messagebox.showinfo(title="提示", message="先走几步再悔棋啦")
        elif self.ISFINISH:
            messagebox.showinfo(title="提示", message="游戏都结束了啦")
        else:
            # 获取并删除最后一步棋对应画布 ID
            s = self.IDs.pop()
            # 获取并删除最后一步棋对应的坐标
            p = self.ALLSTEPS.pop()
            # 最后一步棋是谁下的
            role = self.BOARD[p[0], p[1]]
            self.BOARD[p[0], p[1]] = R["empty"]  # 将棋盘置空
            # 删除画布上对应节点
            self.CANVAS.delete(s)
            # 把悔棋的步骤保存起来
            self.STEPTAILS.append([p, role])
            self.reverse()  # 悔棋一次翻转一次角色
            self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"

    # 撤销悔棋
    def forward(self):
        if len(self.STEPTAILS) == 0:
            messagebox.showinfo(title="嘤嘤嘤", message="没办法撤销啦")
        else:
            # 删除悔棋步骤, 并获取悔棋坐标
            p, r = self.STEPTAILS.pop()
            # 利用坐标重新下, 并且不需要清空悔棋步骤
            self.put(p, r, False)

    # 离开
    def quit(self, w: Tk, HOME: callable):
        w.destroy()
        HOME()

    # 鼠标左键点击事件
    def mouseClick(self, event):
        if not self.ISFINISH:
            x, y = self.find_pos(event.x, event.y)  # 获取落子坐标

            if x is not None and y is not None:
                # 因为坐标存在 [0, 0] 所以不能直接使用 x and y
                self.put([x, y], self.WHO)  # 落子

    # 侧边栏按钮
    def sidebar(self, w: Tk, undo, quit, resume, forward):
        # 执子提示
        self.WHOID = ttk.Label(w, width=12, anchor="center")
        self.WHOID["background"] = "#e6e6e6"
        self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"
        self.WHOID.grid(row=0, column=1, rowspan=2, padx=5)

        # 四个按钮
        button1 = ttk.Button(w, text="悔棋", command=undo, width=5)
        button1.grid(row=2, column=1, padx=5)
        button2 = ttk.Button(w, text="撤销", command=forward, width=5)
        button2.grid(row=3, column=1, padx=5)
        button3 = ttk.Button(w, text="重开", command=resume, width=5)
        button3.grid(row=4, column=1, padx=5)
        button4 = ttk.Button(w, text="返回", command=quit, width=5)
        button4.grid(row=5, column=1, padx=5)

    def start(self, HOME: callable):
        root = Tk()

        from . import file

        # 菜单栏
        m = {
            "文件": {
                "保存": lambda: file.save_chess_manual(self.ALLSTEPS),
                "导入": lambda: file.import_chess_manual(self),
                "退出": lambda: self.quit(root, HOME),
            },
            "帮助": {"关于": about},
        }

        menu(root, m)
        windowStyle(root, "左右手互博")

        self.drawBoard(root)  # 绘制棋盘

        self.sidebar(
            root,
            self.undo,
            lambda: self.quit(root, HOME),
            self.resume,
            self.forward,
        )  # 生成侧边栏

        # 给画布绑定鼠标左键点击事件
        self.CANVAS.bind("<Button-1>", self.mouseClick)

        # 监听窗口关闭事件
        root.protocol("WM_DELETE_WINDOW", lambda: self.quit(root, HOME))
        root.mainloop()


# 局域网联机对战
class Net_board(Board):
    def __init__(self, m, n, num, role):
        super().__init__(m, n, num)
        self.IAMWHO = role  # 当前玩家是先手还是后手

    def undo(self, type_):
        """
        网络对战悔棋操作
        type=0, 同意悔棋方
        type=1, 想要悔棋方
        """

        def a():
            # 获取并删除最后一步棋对应画布 ID
            s = self.IDs.pop()
            # 获取并删除最后一步棋对应的坐标
            p = self.ALLSTEPS.pop()
            self.BOARD[p[0], p[1]] = R["empty"]  # 将棋盘该位置置空
            # 删除画布上对应节点
            self.CANVAS.delete(s)
            self.reverse()  # 悔棋一次翻转一次角色
            self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"

        if type_:
            # 想要悔棋
            if self.WHO == self.IAMWHO:
                """
                当前步骤是自己
                说明对方走了一步
                你上一步棋走错了
                不仅要取消别人的棋, 还要把自己的棋取消
                """
                for _ in range(2):
                    a()
            else:
                """
                当前是对方下棋
                说明对方还没走
                自己刚刚走错了
                只需要悔一步棋
                """
                a()
        else:
            # 同意悔棋方
            if self.WHO == self.IAMWHO:
                """
                当前步骤是自己
                对方想悔棋, 只需要把对方的棋取消
                """
                a()
            else:
                """
                当前步骤是对方
                对方想悔棋, 把自己的棋和对方上一步棋取消
                """
                for _ in range(2):
                    a()

    def ask_undo(self, socket):
        """
        悔棋请求
        """
        # 没下棋、一方获胜了、棋盘上只有一步棋并且当前是自己下棋都不允许悔棋
        if len(self.ALLSTEPS) == 0:
            messagebox.showinfo(title="提示", message="先走几步再悔棋啦")
        elif self.ISFINISH:
            messagebox.showinfo(title="提示", message="游戏都结束了啦")
        elif len(self.ALLSTEPS) == 1 and self.WHO == self.IAMWHO:
            messagebox.showinfo(title="提示", message="才刚刚开始呢~别那么着急嘛")
        else:
            s = json_to_byte({"undo": True})
            socket.send(s)

    def ask_resume(self, socket):
        """重新开局请求"""
        s = json_to_byte({"resume": True})
        socket.send(s)

    def quit(self, root, HOME, socket):
        """返回主页"""
        s = json_to_byte({"quit": True})
        socket.send(s)
        socket.shutdown(SHUT_RDWR)
        socket.close()
        root.destroy()
        HOME()

    # 侧边栏
    def sidebar(self, w, undo, quit, resume):
        me = ttk.Label(w, background="#e6e6e6", width=12, anchor="center")
        me["text"] = f"我是{tr[self.IAMWHO]}方"
        me.grid(row=1, column=1, padx=5)

        # 执子提示
        self.WHOID = ttk.Label(w, width=12, anchor="center")
        self.WHOID["background"] = "#e6e6e6"
        self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"
        self.WHOID.grid(row=0, column=1, padx=5)

        # 四个按钮
        button1 = ttk.Button(w, text="悔棋", command=undo, width=5)
        button1.grid(row=2, column=1, padx=5)
        button2 = ttk.Button(w, text="撤销", width=5)
        button2["state"] = "disable"
        button2.grid(row=3, column=1, padx=5)
        button3 = ttk.Button(w, text="重开", command=resume, width=5)
        button3.grid(row=4, column=1, padx=5)
        button4 = ttk.Button(w, text="返回", command=quit, width=5)
        button4.grid(row=5, column=1, padx=5)

    #  联网对战
    def start(self, root, frame, HOME, socket):
        self.drawBoard(frame)  # 绘制棋盘
        # 生成侧边栏
        self.sidebar(
            frame,
            lambda: self.ask_undo(socket),
            lambda: self.quit(root, HOME, socket),
            lambda: self.ask_resume(socket),
        )

        root.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.quit(root, HOME, socket),
        )


# 人机模式
class AI_board(Board):
    def __init__(self, m: int, n: int, num: int, depth: int, first: bool):
        super().__init__(m, n, num)

        self.ZOBRIST = Zobrist(m, n)  # 初始化 zobrist 散列对象
        self.DEPTH = depth  # 搜索深度
        self.FIRST = first  # 是否先手
        self.CURRENTSTEPS = []  # AI 模拟落子的步骤, 区别与棋盘的 allsteps

        # 存储双方得分数组, 与棋盘大小、维数一致
        self.COMSCORE = np.zeros([m, n], dtype=int)
        self.HUMSCORE = np.zeros([m, n], dtype=int)

        # 某坐标分数缓存数组
        self.SCORECACHE = []

        for i in range(3):
            if i == 0:
                # 第一个为空数组/占位
                self.SCORECACHE.append([])
            else:
                # 代表 AI 和 玩家
                # 需要 4 个数组是为了能够存储上、下、斜四个方向上的分数
                mylist = []

                for _ in range(4):
                    mylist.append(np.zeros([m, n], dtype=int))

                self.SCORECACHE.append(mylist)

        # 初始化分数
        self.initScore()

    # 侧边栏按钮
    def sidebar(self, w: Tk, undo, quit, resume, forward):
        # 执子提示
        self.WHOID = ttk.Label(w, width=12, anchor="center")
        self.WHOID["background"] = "#e6e6e6"
        self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"
        self.WHOID.grid(row=0, column=1, rowspan=2, padx=5)

        # 四个按钮
        button1 = ttk.Button(w, text="悔棋", command=undo, width=5)
        button1.grid(row=2, column=1, padx=5)
        button2 = ttk.Button(w, text="撤销", command=forward, width=5)
        button2.grid(row=3, column=1, padx=5)
        button3 = ttk.Button(w, text="重开", command=resume, width=5)
        button3.grid(row=4, column=1, padx=5)
        button4 = ttk.Button(w, text="返回", command=quit, width=5)
        button4.grid(row=5, column=1, padx=5)

    # 悔棋
    def undo(self):
        def remove():
            # 获取并删除最后一步棋对应画布 ID
            s = self.IDs.pop()
            # 获取并删除最后一步棋对应的坐标
            p = self.ALLSTEPS.pop()
            # 最后一步棋是谁下的
            role = self.BOARD[p[0], p[1]]
            self.BOARD[p[0], p[1]] = R["empty"]  # 将棋盘置空
            # 删除画布上对应节点
            self.CANVAS.delete(s)
            # 把悔棋的步骤保存起来
            self.STEPTAILS.append([p, role])
            self.reverse()  # 悔棋一次翻转一次角色
            self.WHOID["text"] = f"轮到{tr[self.WHO]}方执棋"

            # 悔棋后需要更新 zobrist 键值
            self.ZOBRIST.go(p[0], p[1], role)
            # 更新分数
            self.updateScore(p)

        if len(self.ALLSTEPS) == 0:
            messagebox.showinfo(title="提示", message="先走几步再悔棋啦")
        elif self.ISFINISH:
            messagebox.showinfo(title="提示", message="游戏都结束了啦")
        elif len(self.ALLSTEPS) == 1:
            if self.FIRST:
                remove()
            else:
                messagebox.showinfo(title="提示", message="您还没走呢")
        else:
            # 与 AI 下棋, 一次需要悔棋两步
            for _ in range(2):
                remove()

    # 撤销悔棋
    def forward(self):
        if len(self.STEPTAILS) < 2:
            messagebox.showinfo(title="o(TヘTo)", message="当前不能撤销哦")
        else:
            for _ in range(2):
                # 删除悔棋步骤, 并获取悔棋坐标
                p, r = self.STEPTAILS.pop()
                # 利用坐标重新下, 并且不需要清空悔棋步骤
                self.put(p, r, False)

    # 鼠标左键点击事件
    def mouseClick(self, event):
        if not self.ISFINISH:
            x, y = self.find_pos(event.x, event.y)  # 获取落子坐标

            if (
                x is not None
                and y is not None
                and self.BOARD[x, y] == R["empty"]  # noqa E501
            ):
                self.put([x, y], R["oneself"])  # 落子
                # 落子后更新 zobrist 键值
                self.ZOBRIST.go(x, y, R["oneself"])
                # 更新分数
                self.updateScore([x, y])

                # 只要还没赢 AI 就落子
                if not self.ISFINISH:
                    from .ai import minimax

                    # 获取坐标
                    p = minimax.deepAll(self, self.DEPTH)
                    self.put(p, R["rival"])
                    # 电脑落子后更新分数
                    self.updateScore(p)
                    # 电脑落子后更新 zobrist 键值
                    self.ZOBRIST.go(x, y, R["oneself"])

    def quit(self, root: Tk, HOME):
        root.destroy()
        HOME()

    # 人机对战
    def start(self, HOME):
        root = Tk()

        from . import file

        # 菜单栏
        m = {
            "文件": {
                "保存": lambda: file.save_chess_manual(
                    self.ALLSTEPS,
                    self.FIRST,
                ),
                "导入": lambda: file.import_chess_manual(self),
                "退出": lambda: self.quit(root, HOME),
            },
            "帮助": {
                "关于": about,
            },
        }

        menu(root, m)
        windowStyle(root, "人机对战")

        self.drawBoard(root)  # 绘制棋盘

        # 生成侧边栏
        self.sidebar(
            root,
            self.undo,
            lambda: self.quit(root, HOME),
            lambda: self.resume(self.FIRST),
            self.forward,
        )

        # 给画布绑定鼠标左键
        self.CANVAS.bind("<Button-1>", self.mouseClick)

        if not self.FIRST:
            # 电脑先手, 下在中间
            self.put([self.m // 2, self.n // 2], self.WHO)

        root.protocol("WM_DELETE_WINDOW", lambda: self.quit(root, HOME))
        root.mainloop()

    def hasNeighbor(self, x: int, y: int, distance: int, count: int) -> bool:
        """
        判断某点附近是否存在指定数目的棋子
        x: 行坐标
        y: 列坐标
        distance: 判断范围
        count: 所需子数最小值
        """
        board = self.BOARD
        n = board.shape[0]
        m = board.shape[1]

        startX = x - distance
        endX = x + distance
        startY = y - distance
        endY = y + distance

        for i in range(startX, endX + 1):
            # 行越界的邻居跳过
            if i < 0 or i >= n:
                continue
            for j in range(startY, endY + 1):
                # 列越界的邻居跳过
                if j < 0 or j >= m:
                    continue
                # 如果邻居是自己也跳过
                if i == x and j == y:
                    continue
                # 附近有子,计数减一
                if board[i, j] != R["empty"]:
                    count -= 1
                # 计数降至 0,说明邻居数超过给定值
                # 符合条件,返回 True
                if count <= 0:
                    return True
        # 邻居数没有超过给定数目,返回 False
        return False

    def gen(self, role: int, onlyThrees: bool):
        """
        启发式评估函数
        对整个棋盘空位进行评分, 判断是否能够成五、活四等等
        优先对这些可能会获胜的点进行递归, 能够提高搜索速度/剪枝效率
        注意区别于 evaluate.py(对四个方向进行评分)
        """
        if len(self.ALLSTEPS) == 0:
            return [7, 7]

        fives = []  # 连五
        com_fours = []  # AI 活四
        hum_fours = []  # 玩家活四
        com_blocked_fours = []  # AI 眠四
        hum_blocked_fours = []  # 玩家眠四
        com_double_threes = []  # AI 双三
        hum_double_threes = []  # 玩家双三
        com_threes = []  # AI 活三
        hum_threes = []  # 玩家活三
        com_twos = []  # AI 活二
        hum_twos = []  # 玩家活二
        neighbors = []  # 附近点

        board = self.BOARD

        for i, item in enumerate(board):
            for j, item_ in enumerate(item):
                if item_ == R["empty"]:
                    if len(self.ALLSTEPS) < 6:
                        if not self.hasNeighbor(i, j, 1, 1):
                            # 以 [i, j] 为中心的边长为 3 格的方形范围内
                            # 不存在棋子, 不用考虑这个点了
                            continue
                    elif not self.hasNeighbor(i, j, 2, 2):
                        continue

                    scoreHum = self.HUMSCORE[i, j]
                    scoreCom = self.COMSCORE[i, j]
                    # 比较 (i,j) 位置 AI 和人谁的评分更高
                    maxScore = max(scoreCom, scoreHum)

                    if onlyThrees and maxScore < S["THREE"]:
                        continue

                    p = {"p": [i, j], "score": maxScore}

                    if scoreCom >= S["FIVE"] or scoreHum >= S["FIVE"]:
                        # 先看 AI 能不能“连五”, 再看玩家能不能“连五”
                        fives.append(p)
                    elif scoreCom >= S["FOUR"]:
                        # AI 有没有活四
                        com_fours.append(p)
                    elif scoreHum >= S["FOUR"]:
                        # 玩家有没有活四
                        hum_fours.append(p)
                    elif scoreCom >= S["BLOCKED_FOUR"]:
                        # AI 有没有眠四
                        com_blocked_fours.append(p)
                    elif scoreHum >= S["BLOCKED_FOUR"]:
                        # 玩家有没有眠四
                        hum_blocked_fours.append(p)
                    elif scoreCom >= 2 * S["THREE"]:
                        # AI 有没有双三
                        com_double_threes.append(p)
                    elif scoreHum >= 2 * S["THREE"]:
                        # 玩家有没有双三
                        hum_double_threes.append(p)
                    elif scoreCom >= S["THREE"]:
                        # AI 有没有活三
                        com_threes.append(p)
                    elif scoreHum >= S["THREE"]:
                        # 玩家有没有活三
                        hum_threes.append(p)
                    elif scoreCom >= S["TWO"]:
                        # AI 有没有活二
                        com_twos.append(p)
                    elif scoreHum >= S["TWO"]:
                        # 玩家有没有活二
                        hum_twos.append(p)
                    else:
                        neighbors.append(p)

        # 成五
        if len(fives):
            return fives

        # 活四
        if role == R["rival"] and len(com_fours):
            return com_fours
        if role == R["oneself"] and len(hum_fours):
            return hum_fours

        # AI 无冲四玩家有活四
        if (
            role == R["rival"]
            and len(hum_fours)
            and len(com_blocked_fours) == 0  # noqa E501
        ):
            return hum_fours
        # 玩家不能冲四但 AI 有活四
        if (
            role == R["oneself"]
            and len(com_fours)
            and len(hum_blocked_fours) == 0  # noqa E501
        ):
            return com_fours

        # 冲四/活四
        if role == R["rival"]:
            fours = com_fours + hum_fours
        else:
            fours = hum_fours + com_fours
        if role == R["rival"]:
            blockedfours = com_blocked_fours + hum_blocked_fours
        else:
            blockedfours = hum_blocked_fours + com_blocked_fours
        if len(fours):
            return fours + blockedfours

        # 双三/活三/眠三等情况
        result = []
        if role == R["rival"]:
            result = (
                com_double_threes
                + hum_double_threes
                + com_blocked_fours
                + result
                + hum_blocked_fours
                + com_threes
                + hum_threes
            )
        if role == R["oneself"]:
            result = (
                hum_double_threes
                + com_double_threes
                + hum_blocked_fours
                + com_blocked_fours
                + hum_threes
                + com_threes
            )

        if len(com_double_threes) or len(hum_double_threes):
            return result

        # 如果只考虑双三的话...
        if onlyThrees:
            return result

        # 有活二等情况
        if role == R["rival"]:
            twos = com_twos + hum_twos
        else:
            twos = hum_twos + com_twos

        twos.sort(key=lambda x: x["score"], reverse=True)

        # 如果没有活二就下在附近...
        result.extend(twos if len(twos) else neighbors)

        # 分数低的不用全部计算了
        # 即 gen 返回的节点数不能超过给定值 C["countLimit"]
        if len(result) > C["countLimit"]:
            return result[0 : C["countLimit"]]  # noqa E203

        return result

    # 评估函数的局部刷新
    def evaluate(self, role: int) -> int:
        comMaxScore = 0
        humMaxScore = 0

        board = self.BOARD

        # 遍历棋盘, 获取修正后 AI 和玩家的总分
        for i, item in enumerate(board):
            for j, item_ in enumerate(item):
                # 累加 AI 或人的每一个位置的分数
                if item_ == R["rival"]:
                    comMaxScore += self.fixScore(self.COMSCORE[i, j])
                elif item_ == R["oneself"]:
                    humMaxScore += self.fixScore(self.HUMSCORE[i, j])

        neg = 1 if role == R["rival"] else -1
        """
        如果估分对象是 AI,且 comMaxScore - humMaxScore < 0
        AI 分数低, result 是负数, 说明该棋面对 AI 不利
        如果估分对象是对手,且 comMaxScore - humMaxScore < 0
        AI 分数低, result 是正数, 说明棋面对人有利
        """
        result = neg * (comMaxScore - humMaxScore)
        return result

    # 分数修正
    def fixScore(self, score: int):
        # 如果分数在活四和眠四之间(10000~100000)
        if score < S["FOUR"] and score >= S["BLOCKED_FOUR"]:
            # 如果分数小于眠四与活三之和(10000~11000)
            if score < S["BLOCKED_FOUR"] + S["THREE"]:
                # 降低 AI 冲四行为(通过降低其评分至与活三一致)
                # 冲四局面: 再下一个子就能连五了
                return S["THREE"]
            elif score < S["BLOCKED_FOUR"] * 2:
                # 如果分数小于眠四分数的两倍(11000~20000)
                # 升高其分数, 使其冲四
                return S["FOUR"]
            else:
                # 双冲四(20000~100000)
                return S["FOUR"] * 2
        return score

    # 更新一个位置的分数
    def updateScore(self, p: tuple[int, int]):
        # 更新范围
        radius = self.NUM - 1
        # 棋盘维度 m × n
        m = self.m
        n = self.n
        # 坐标
        x = p[0]
        y = p[1]

        from .ai.evaluate import s as scorePoint

        def update(x, y, dir):
            role = self.BOARD[x, y]
            """
            与 initScore 不同的是为空时不需要判断附近有没有子了
            因此用 != 可以省去判断为空的部分
            """
            if role != R["oneself"]:
                # 如果该点不是玩家(空或者 AI)
                cs = scorePoint(self, x, y, R["rival"], dir)
                self.COMSCORE[x, y] = cs
            else:
                # 是人, 则 AI 分数为 0
                self.COMSCORE[x, y] = 0

            if role != R["rival"]:
                # 如果该点不是 AI(空或玩家)
                hs = scorePoint(self, x, y, R["oneself"], dir)
                self.HUMSCORE[x, y] = hs
            else:
                # 如果是 AI,玩家分数为 0
                self.HUMSCORE[x, y] = 0

        # 横向 ——
        for i in range(-radius, radius + 1):
            x_ = x
            y_ = y + i
            if y_ < 0:
                continue
            if y_ >= n:
                break
            update(x_, y_, 0)

        # 纵向 |
        for i in range(-radius, radius + 1):
            x_ = x + i
            y_ = y
            if x_ < 0:
                continue
            if x_ >= m:
                break
            update(x_, y_, 1)

        # 斜向 \
        for i in range(-radius, radius + 1):
            x_ = x + i
            y_ = y + i
            if x_ < 0 or y_ < 0:
                continue
            if x_ >= m or y_ >= n:
                break
            update(x_, y_, 2)

        # 斜向 /
        for i in range(-radius, radius + 1):
            x_ = x + i
            y_ = y - i
            if x_ < 0 or y_ >= n:
                continue
            if x_ >= m or y_ < 0:
                continue
            update(x_, y_, 3)

    # 对当前棋盘进行打分
    def initScore(self):
        from .ai.evaluate import s as scorePoint

        board = self.BOARD
        for i, item in enumerate(board):
            for j, item_ in enumerate(item):
                # 空位, 双方都打分
                if item_ == R["empty"]:
                    # 但要求以 (i,j) 为中心 5 × 5 范围内存在 2 个邻居
                    if self.hasNeighbor(i, j, 2, 2):
                        cs = scorePoint(self, i, j, R["rival"])
                        hs = scorePoint(self, i, j, R["oneself"])
                        self.COMSCORE[i, j] = cs
                        self.HUMSCORE[i, j] = hs
                elif item_ == R["rival"]:
                    # 对 AI 打分, 玩家此位置分数为 0
                    self.COMSCORE[i, j] = scorePoint(self, i, j, R["rival"])
                    self.HUMSCORE[i, j] = 0
                elif item_ == R["oneself"]:
                    # 对玩家打分, AI 分数为 0
                    self.HUMSCORE[i, j] = scorePoint(self, i, j, R["oneself"])
                    self.COMSCORE[i, j] = 0

    def AIput(self, p, role):
        self.BOARD[p[0], p[1]] = role
        self.ZOBRIST.go(p[0], p[1], role)
        self.updateScore(p)
        self.ALLSTEPS.append(p)
        self.CURRENTSTEPS.append(p)

    def AIremove(self, p):
        r = self.BOARD[p[0], p[1]]
        self.ZOBRIST.go(p[0], p[1], r)
        self.BOARD[p[0], p[1]] = R["empty"]
        self.updateScore(p)
        self.ALLSTEPS.pop()
        self.CURRENTSTEPS.pop()
