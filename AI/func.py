'''
一些必要的功能
'''
from Func.constants import S, threshold
import math


# 角色互换
def reverse(r):
    return 2 if r == 1 else 1


# 等于
def equal(a, b):
    b = b or 0.01
    if b >= 0:
        return a >= b / threshold and a <= b * threshold
    else:
        return a >= b * threshold and a <= b / threshold


# 大于
def greatThan(a, b):
    if b >= 0:
        return a >= (b + 0.1) * threshold
    else:
        return a >= (b + 0.1) / threshold


# 大于等于
def greatOrEqualThan(a, b):
    return equal(a, b) or greatThan(a, b)


# 小于
def littleThan(a, b):
    if b >= 0:
        return a <= (b - 0.1) / threshold
    else:
        return a <= (b - 0.1) * threshold


# 小于等于
def littleOrEqualThan(a, b):
    return equal(a, b) or littleThan(a, b)


# “四舍五入”
def round(score):
    neg = -1 if score < 0 else 1
    abs = math.abs(score)
    if abs <= S["ONE"] / 2:
        return 0
    if abs <= S["TWO"] / 2 and abs > S["ONE"] / 2:
        return neg * S["ONE"]
    if abs <= S["THREE"] / 2 and abs > S["TWO"] / 2:
        return neg * S["TWO"]
    if abs <= S["THREE"] * 1.5 and abs > S["THREE"] / 2:
        return neg * S["THREE"]
    if abs <= S["FOUR"] / 2 and abs > S["THREE"] * 1.5:
        return neg * S["THREE"] * 2
    if abs <= S["FIVE"] / 2 and abs > S["FOUR"] / 2:
        return neg * S["FOUR"]
    return neg * S["FIVE"]
