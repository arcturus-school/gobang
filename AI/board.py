'''
Author: ARCTURUS
Date: 2021-11-12 16:46:58
LastEditTime: 2021-11-16 11:01:48
LastEditors: ARCTURUS
Description: 生成落子点
'''

from evaluate import s as scorePoint
from zobrist import Zobrist
from constants import R, S, C
import numpy as np
import math
'''
description: 评分修正
param {int} type: 原始分数
return {int}: 修正后分数
'''


class Board():
    '''
    description: 棋盘初始化
    param {*} board: 棋盘二维数组
    '''
    def __init__(self, board):
        self.evaluateCache = {}
        self.currentSteps = []
        self.allSteps = []  # 落子步骤记录
        self.stepsTail = []  # 悔棋步骤
        self.zobrist = Zobrist()
        self._last = [False, False]  # 记录最后一步

        # 初始化 board
        self.board = board
        # 棋盘总落子数
        # 因为存在随机开局,因此棋盘开局的落子数不一定为 0
        # 使用 np 的 extract 获二维数组内不等于 0 的元素个数
        self.count = len(np.extract(board != 0, board))

        # 存储双方得分数组
        n = board.shape[0]
        m = board.shape[1]
        self.comScore = np.zeros([n, m], dtype=int)
        self.humScore = np.zeros([n, m], dtype=int)

        # 某坐标分数缓存数组
        self.scoreCache = []
        for i in range(3):
            if i == 0:
                # 第一个为空数组/占位
                self.scoreCache.append([])
            else:
                # 代表 AI 和 玩家
                # 需要 4 个数组是为了能够存储上、下、斜四个方向上的分数
                mylist = []
                for _ in range(4):
                    mylist.append(np.zeros([n, m], dtype=int))
                self.scoreCache.append(mylist)

        # 当前局势打分
        self.initScore()

    '''
    description: 对当前棋盘进行打分
    return {*}
    '''

    def initScore(self):
        board = self.board
        for i, item in enumerate(board):
            for j, item_ in enumerate(item):
                # 空位,双方都打分
                if item_ == R["empty"]:
                    # 附件必须有子才行
                    # 在以 (i,j) 为中心的 5 × 5 范围内需要存在 2 个邻居
                    if self.hasNeighbor(i, j, 2, 2):
                        cs = scorePoint(self, i, j, R["com"])
                        hs = scorePoint(self, i, j, R["hum"])
                        self.comScore[i, j] = cs
                        self.humScore[i, j] = hs
                elif item_ == R["com"]:
                    # 对 AI 打分,玩家此位置分数为 0
                    self.comScore[i, j] = scorePoint(self, i, j, R["com"])
                    self.humScore[i, j] = 0
                elif item_ == R["hum"]:
                    # 对玩家打分,AI 分数为 0
                    self.humScore[i, j] = scorePoint(self, i, j, R["hum"])
                    self.comScore[i, j] = 0

    '''
    description: 更新一个位置的分数
    param {list} p: 需要更新分数的位置的坐标
    '''

    def updateScore(self, p):
        radius = 4
        # 棋盘维度 n × m
        n = self.board.shape[0]
        m = self.board.shape[1]
        # 坐标
        x = p[0]
        y = p[1]

        def update(x, y, dir):
            role = self.board[x, y]

            # 与 initScore 不同的是为空时不需要判断附近有没有子了
            # 因此用 != 可以省去判断为空的部分
            # 如果该点不是玩家(空或者 AI)
            if role != R["hum"]:
                cs = scorePoint(self, x, y, R["com"], dir)
                self.comScore[x, y] = cs
            else:
                # 是人,则 AI 分数为 0
                self.comScore[x, y] = 0

            # 如果该点不是 AI(空或玩家)
            if role != R["com"]:
                hs = scorePoint(self, x, y, R["hum"], dir)
                self.humScore[x, y] = hs
            else:
                # 如果是 AI,玩家分数为 0
                self.humScore[x, y] = 0

        # 无论是不是空位,都需要更新
        # 横向 ——
        for i in range(-radius, radius + 1):
            x_ = x
            y_ = y + i
            if y_ < 0:
                continue
            if y_ >= m:
                break
            update(x_, y_, 0)

        # 纵向 |
        for i in range(-radius, radius + 1):
            x_ = x + i
            y_ = y
            if x_ < 0:
                continue
            if x_ >= n:
                break
            update(x_, y_, 1)

        # 斜向 \
        for i in range(-radius, radius + 1):
            x_ = x + i
            y_ = y + i
            if x_ < 0 or y_ < 0:
                continue
            if x_ >= n or y_ >= m:
                break
            update(x_, y_, 2)

        # 斜向 /
        for i in range(-radius, radius + 1):
            x_ = x + i
            y_ = y - i
            if x_ < 0 or y_ >= m:
                continue
            if x_ >= n or y_ < 0:
                continue
            update(x_, y_, 3)

    '''
    description: 落子
    param {*} p: 落子坐标/[i, j]
    param {*} role: 谁落子
    '''

    def put(self, p, role):
        x = p[0]
        y = p[1]
        # 落子
        self.board[x, y] = role
        # 落子后更新 zobrist 键值
        self.zobrist.go(x, y, role)
        # 更新分数
        self.updateScore(p)
        # 记录落子点
        self.allSteps.append(p)
        self.currentSteps.append(p)
        # 清空悔棋的步骤
        # 即落子后不能再返回原来悔棋前的棋局
        self.stepsTail.clear()
        # 记录下棋次数
        self.count += 1

    '''
    description: 移除棋子
    param {*} p: 移除坐标/[i, j]
    '''

    def remove(self, p):
        x = p[0]
        y = p[1]
        role = self.board[x, y]
        # 悔棋后需要更新 zobrist 键值
        self.zobrist.go(x, y, role)
        # 将棋盘对应位置置 0
        self.board[x, y] = R["empty"]
        # 更新分数
        self.updateScore(p)
        # 从步骤中删除最后一个步骤
        self.allSteps.pop()
        self.currentSteps.pop()
        # 下棋次数减一次
        self.count -= 1

    '''
    description: 悔棋
    '''

    def backward(self):
        # 如果只有 0 或 1 步
        if len(self.allSteps) < 2:
            return
        i = 0
        # 删除 AI 下的和人下的共两步棋
        while i < 2:
            # 最后一步棋坐标
            s = self.allSteps[-1]
            # 最后一步棋是谁下的
            role = self.board[s[0], s[1]]
            self.remove(s)
            # 把悔棋的步骤保存起来
            self.stepsTail.append([s, role])
            i += 1

    '''
    description: 不想悔棋了可以返回
    '''

    def forward(self):
        if len(self.stepsTail) < 2:
            return
        i = 0
        while i < 2:
            # 删除悔棋步骤,并获取悔棋坐标
            s = self.stepsTail.pop()
            # 利用坐标重新下
            self.put(s[0], s[1])
            i += 1

    '''
    description: 分数修正
    param {*} score: 分数
    return {*}
    '''

    def fixScore(self, score):
        # 如果分数在活四和死四之间(10000~100000)
        if score < S["FOUR"] and score >= S["BLOCKED_FOUR"]:
            # 如果分数小于死四与活三之和(10000~11000)
            if score < S["BLOCKED_FOUR"] + S["THREE"]:
                # 降低 AI 冲四行为(通过降低其评分至与活三一致)
                # 冲四局面: 再下一个子就能连五了
                return S["THREE"]
            elif score < S["BLOCKED_FOUR"] * 2:
                # 如果分数小于死四分数的两倍
                # 升高其分数,使其冲四活三
                return S["FOUR"]
            else:
                # 双冲四
                return S["FOUR"] * 2
        return score

    '''
    description: 评估函数的局部刷新
    param {*} role
    return {*}
    '''

    def evaluate(self, role):
        self.comMaxScore = 0
        self.humMaxScore = 0

        board = self.board

        # 遍历棋盘, 获取修正后 AI 和玩家的总分
        for i, item in enumerate(board):
            for j, item_ in enumerate(item):
                # 累加 AI 或人的每一个位置的分数
                if item_ == R["com"]:
                    self.comMaxScore += self.fixScore(self.comScore[i, j])
                elif item_ == R["hum"]:
                    self.humMaxScore += self.fixScore(self.humScore[i, j])

        neg = 1 if role == R["com"] else -1
        '''
        如果估分对象是 AI,且 self.comMaxScore - self.humMaxScore < 0
        AI 分数低,result 是负数,说明该棋面对 AI 不利
        如果估分对象是对手,且 self.comMaxScore - self.humMaxScore < 0
        AI 分数低,result 是正数,说明棋面对人有利
        '''
        result = neg * (self.comMaxScore - self.humMaxScore)
        return result

    '''
    description: 启发式评估函数
    对某个空位进行评分,判断是否能够成五、活四等等
    优先对这些可能会获胜的点进行递归,能够提高搜索速度/剪枝效率
    注意区别于 evaluate.py(对四个方向进行评分)
    param {*} role
    param {*} onlyThrees
    param {*} starSpread
    return {list} 需要进行递归评分的列表
    '''

    def gen(self, role):
        if self.count == 0:
            return [7, 7]

        fives = []  # 连五
        com_fours = []  # AI 活四
        hum_fours = []  # 玩家活四
        com_blocked_fours = []  # AI 死四
        hum_blocked_fours = []  # 玩家死四
        com_double_threes = []  # AI 双三
        hum_double_threes = []  # 玩家双三
        com_threes = []  # AI 活三
        hum_threes = []  # 玩家活三
        com_twos = []  # AI 活二
        hum_twos = []  # 玩家活二
        neighbors = []

        board = self.board

        for i, item in enumerate(board):
            for j, item_ in enumerate(item):
                if item_ == R["empty"]:
                    if len(self.allSteps) < 6:
                        if not self.hasNeighbor(i, j, 1, 1):
                            # 以 [i, j] 为中心的边长为 3 格的方形范围内
                            # 不存在 1 个己方棋子
                            # 后面代码不用考虑了
                            continue
                        elif not self.hasNeighbor(i, j, 2, 2):
                            # 如果以 [i, j] 为中心的边长为 3 格的方形范围内
                            # 存在 1 个己方棋子, 则扩大搜索范围
                            # 以 [i, j] 为中心的边长为 5 格的方形范围内
                            # 不存在 2 个己方棋子, 后面代码也不用考虑了
                            continue

                    scoreHum = self.humScore[i, j]
                    scoreCom = self.comScore[i, j]
                    # 比较 (i,j) 位置 AI 和人谁的评分更高
                    maxScore = math.max(scoreCom, scoreHum)

                    # 若只考虑大于等于活三的情况
                    # 并且分数还低于活三的, 直接跳过
                    if C["onlyThrees"] and maxScore < S["THREE"]:
                        continue

                    p = [i, j]

                    if scoreCom >= S["FIVE"]:
                        # 先看 AI 能不能“连五”
                        fives.append(p)
                    elif scoreHum >= S["FIVE"]:
                        # 再看玩家能不能“连五”
                        fives.append(p)
                    elif scoreCom >= S["FOUR"]:
                        # AI 有没有活四
                        com_fours.append(p)
                    elif scoreHum >= S["FOUR"]:
                        # 玩家有没有活四
                        hum_fours.append(p)
                    elif scoreCom >= S["BLOCKED_FOUR"]:
                        # AI 有没有死四
                        com_blocked_fours.append(p)
                    elif scoreHum >= S["BLOCKED_FOUR"]:
                        # 玩家有没有死四
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
        if role == R["com"] and len(com_fours):
            return com_fours
        if role == R["hum"] and len(hum_fours):
            return hum_fours

        # AI 无冲四玩家有活四
        if role == R["com"] and len(hum_fours) and len(com_blocked_fours) == 0:
            return hum_fours
        # 玩家不能冲四但 AI 有活四
        if role == R["hum"] and len(com_fours) and len(hum_blocked_fours) == 0:
            return com_fours

        # 冲四/活四
        if role == R["com"]:
            fours = com_fours + hum_fours
        else:
            fours = hum_fours + com_fours
        if role == R["com"]:
            blockedfours = com_blocked_fours + hum_blocked_fours
        else:
            blockedfours = hum_blocked_fours + com_blocked_fours
        if len(fours):
            return fours + blockedfours

        # 双三/活三/死三等情况
        result = []
        if role == R["com"]:
            result = (com_double_threes + hum_double_threes +
                      com_blocked_fours + result + hum_blocked_fours +
                      com_threes + hum_threes)
        if role == R["hum"]:
            result = (hum_double_threes + com_double_threes +
                      hum_blocked_fours + com_blocked_fours + hum_threes +
                      com_threes)

        if len(com_double_threes) or len(hum_double_threes):
            return result

        # 只考虑大于等于活三的情况
        if C["onlyThrees"]:
            return result

        # 还考虑活二等情况
        if role == R["com"]:
            twos = com_twos + hum_twos
        else:
            twos = hum_twos + com_twos

        # 降序
        def dscore(x):
            r = self.board[x[0], x[1]]
            if r == R["com"]:
                return self.comScore[x[0], x[1]]
            elif r == R["hum"]:
                return self.humScore[x[0], x[1]]

        twos.sort(key=dscore, reverse=False)

        result.extend(twos if len(twos) else neighbors)

        # 分数低的不用全部计算了
        # 即 gen 返回的节点数不能超过给定值 C["countLimit"]
        if len(result) > C["countLimit"]:
            return result[0:C["countLimit"]]

        return result

    '''
    description: 判断某点附近是否存在指定数目的棋子
    param {*} x: 行坐标
    param {*} y: 列坐标
    param {*} distance: 判断范围
    param {*} count: 所需子数最小值
    return {bool}
    '''

    def hasNeighbor(self, x, y, distance, count):
        board = self.board
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
