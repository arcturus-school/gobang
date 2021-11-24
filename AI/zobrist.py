'''
Zobrist 哈希算法, 对重复棋盘的优化
'''
from Func.constants import R
import numpy as np
import secrets


class Zobrist:
    def __init__(self, n=15, m=15):
        # 初始化 Zobrist 哈希值
        self.code = self._rand()

        # 初始化两个 n × m 的空数组
        self._com = np.empty([n, m], dtype=int)
        self._hum = np.empty([n, m], dtype=int)

        # 数组与棋盘相对应
        # 给每一个位置附上一个随机数, 代表不同的状态
        for x, y in np.nditer([self._com, self._hum], op_flags=["writeonly"]):
            x[...] = self._rand()
            y[...] = self._rand()

    def _rand(self, k=31):
        '''
        生成 k 位随机数(k<=31)
        :param {int} k: 随机数位数
        :return {int} k 位随机数
        '''
        return secrets.randbits(k)

    def go(self, x, y, role):
        '''
        :param {int} x: 行坐标
        :param {int} y: 列坐标
        :param {int} role: AI or 玩家
        :return {int} code: 新的 Zobrist 哈希值
        '''
        # 判断本次操作是 AI 还是人, 并返回相应位置的随机数
        code = self._com[x, y] if role == R["rival"] else self._hum[x, y]
        # 当前键值异或位置随机数
        self.code = self.code ^ code
