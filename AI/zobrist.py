'''
Author: ARCTURUS
Date: 2021-11-12 20:56:06
LastEditTime: 2021-11-15 18:05:18
LastEditors: ARCTURUS
Description: Zobrist 哈希算法,对于重复棋盘的优化
'''
from constants import R
import numpy as np
import secrets


class Zobrist:
    def __init__(self, n=15, m=15):
        # 初始化 Zobrist 哈希值
        self._code = self._rand()

        # 初始化两个 n × m 的空数组
        self._com = np.empty([n, m], dtype=int)
        self._hum = np.empty([n, m], dtype=int)

        # 数组与棋盘相对应
        # 给每一个位置附上一个随机数,代表不同的状态
        for x, y in np.nditer([self._com, self._hum], op_flags=["writeonly"]):
            x[...] = self._rand()
            y[...] = self._rand()

    '''
    description: 生成 k 位随机数
    k>=32 时 numpy 会报错 “Python int too large to convert to C long”
    param {*} k: 伪随机数位数
    return {*}
    '''

    def _rand(self, k=31):
        return secrets.randbits(k)

    '''
    param {int} x: 行坐标
    param {int} y: 列坐标
    param {int} role: AI or 玩家
    return {int} code: 新的 Zobrist 哈希值
    '''

    def go(self, x, y, role):
        # 判断本次操作是 AI 还是人,并返回相应位置的随机数
        code = self._com[x, y] if role == R["com"] else self._hum[x, y]
        # 当前键值异或位置随机数
        self._code = self._code ^ code
        return self._code
