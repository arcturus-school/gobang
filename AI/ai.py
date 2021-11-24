'''
AI 下棋
'''

from minimax import deepAll
from Func.constants import R, C
from board import Board
from opening import open26, board_open_center, create_zeros_board, open_match
import random


class AI():
    # 棋盘对象
    board = None
    '''
    description: 游戏开始
    param {bool} first: 是否 AI 先手
    param {bool} randomOpening: 是否随机开局
    return {*} board: 开局棋盘 name: 开局名称
    '''
    def start(self, first, randomOpening):
        if first:
            if randomOpening:
                # 从 26 个开局中随机获取一种开局
                key = random.sample(list(open26.keys()), 1)[0]
                o = open26[key]["board"]
                self.board = Board(o)
                return {
                    "board": o,
                    "name": open26[key]["name"],
                }
            else:
                # 中心点开局
                o = board_open_center()
                self.board = Board(o)
                return {"board": o}
        else:
            # 如果不是 AI 先手
            # 仅初始化一个全 0 二维数组
            o = create_zeros_board()
            self.board = Board(o)
            return {"board": o}

    '''
    description: AI 落子
    return {list} p: 落子位置 [i, j]
    '''

    def begin(self):
        p = None
        if len(self.board.allSteps) > 1:
            # 采用必胜开局
            p = open_match(self.board)
        # 或者步数只有 0 步或 1 步
        # 使用 deepAll 获取下一步棋子
        p = p or deepAll(None, C["searchDeep"])
        self.board.put(p, R.com)
        return p

    '''
    description: 玩家下完 AI 就开始计算并下子
    param {*} x: 行坐标
    param {*} y: 列坐标
    '''

    def turn(self, x, y):
        self.set(x, y, R.hum)
        return self.begin()

    '''
    description: 仅下子
    param {*} x: 行坐标
    param {*} y: 列坐标
    param {*} r: 下子角色 AI or 玩家
    '''

    def set(self, x, y, r):
        self.board.put([x, y], r)

    # 前进
    def forward(self):
        self.board.forward()

    # 悔棋
    def backward(self):
        self.board.backward()
