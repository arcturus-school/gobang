from tkinter import filedialog, messagebox
from AI.func import reverse
from AI.minimax import deepAll
from Func.constants import R
import os
import json


def save(steps, first=False):
    '''
    保存棋盘
    '''
    steps.reverse()
    path = os.getcwd() + '/chessmanual'
    data = {"steps": steps, "first": first}
    filename = filedialog.asksaveasfilename(title="保存棋盘",
                                            filetypes=[("TXT", ".txt")],
                                            defaultextension=".txt",
                                            initialdir=(path))
    if filename:
        with open(file=filename, mode='w', encoding='utf-8') as file:
            file.write(json.dumps(data))


def import_(board):
    '''
    导入棋盘
    '''
    path = os.getcwd() + '/chessmanual'
    filename = filedialog.askopenfilename(title='导入棋盘', initialdir=(path))

    if filename:
        with open(file=filename, mode='r', encoding='utf-8') as file:
            data = json.loads(file.read())
            board.resume()  # 导入时先清空一下棋盘
            if data["first"]:
                # 如果玩家是先手...
                board.who = R["oneself"]
                for i in data["steps"]:
                    board.put(i, board.who)
                    board._zobrist.go(i[0], i[1], reverse(board.who))
                    board.updateScore(i)
                if len(data["steps"]) % 2 != 0:
                    # 如果步数不是偶数, 说明电脑还要再走一步
                    p = deepAll(board, board._depth)
                    board.put(p, board.who)
                print("白棋先手, 棋盘导入成功")
            elif board._first == data["first"]:
                # 从本地棋盘导入到人机时
                # 本地默认黑棋先走(first=False)
                # 如果从AI先手导入...
                for i in data["steps"]:
                    board.put(i, board.who)

                if len(data["steps"]) % 2 == 0:
                    # 如果步数是偶数, 说明电脑还要再走一步
                    p = deepAll(board, board._depth)
                    board.put(p, board.who)
                print("黑棋先手, 棋盘导入成功")
            else:
                # 从本地黑棋先手到人机的玩家(白棋)先手
                messagebox.showinfo(title='导入失败', message='请使用电脑先手重试')
