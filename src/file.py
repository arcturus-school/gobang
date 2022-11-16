from tkinter import filedialog, messagebox

from .ai.func import reverse
from .constants import R
from . import boards

import os
import json


# 保存棋盘
def save_chess_manual(steps, first=False):
    steps.reverse()
    path = os.getcwd() + "/src/chess"

    data = {
        "steps": steps,
        "first": first,
    }

    filename = filedialog.asksaveasfilename(
        title="保存棋盘",
        filetypes=[("TXT", ".txt")],
        defaultextension=".txt",
        initialdir=(path),
    )

    if filename:
        with open(file=filename, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(data))


# 导入棋谱
def import_chess_manual(board: boards.AI_board | boards.Oneself_board):

    path = os.getcwd() + "/src/chess"

    filename = filedialog.askopenfilename(title="导入棋盘", initialdir=(path))

    if filename:
        from .ai import minimax

        with open(file=filename, mode="r", encoding="utf-8") as file:
            data = json.loads(file.read())
            board.resume()  # 导入时先清空一下棋盘

            if data["first"]:
                # 如果玩家是先手...
                board.WHO = R["oneself"]

                r = board.m
                c = board.n

                for i in data["steps"]:
                    x, y = i

                    if x >= c or y >= r:
                        messagebox.showinfo(title="导入失败", message="棋谱大小不正确")
                        return

                    board.put(i, board.WHO)
                    board.ZOBRIST.go(i[0], i[1], reverse(board.WHO))
                    board.updateScore(i)

                if board.__class__.__name__ != "Oneself_board":
                    if len(data["steps"]) % 2 != 0:
                        # 如果步数不是偶数, 说明电脑还要再走一步
                        p = minimax.deepAll(board, board.DEPTH)
                        board.put(p, board.WHO)

                print("白棋先手, 棋盘导入成功")

            elif board.FIRST == data["first"]:
                # 从本地棋盘导入到人机时
                # 本地默认黑棋先走(first=False)
                # 如果从 AI 先手导入...
                r = board.m
                c = board.n

                for i in data["steps"]:
                    x, y = i

                    if x >= c or y >= r:
                        messagebox.showinfo(title="导入失败", message="棋谱大小不正确")
                        return

                    board.put(i, board.WHO)

                if board.__class__.__name__ != "Oneself_board":
                    if len(data["steps"]) % 2 == 0:
                        # 如果步数是偶数, 说明电脑还要再走一步
                        p = minimax.deepAll(board, board.DEPTH)
                        board.put(p, board.WHO)

                print("黑棋先手, 棋盘导入成功")

            else:
                # 从本地黑棋先手到人机的玩家(白棋)先手
                messagebox.showinfo(title="导入失败", message="请使用电脑先手重试")
