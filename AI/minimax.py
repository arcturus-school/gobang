'''
Author: ARCTURUS
Date: 2021-11-12 16:34:30
LastEditTime: 2021-11-16 12:09:34
LastEditors: ARCTURUS
Description: 极大极小值搜索
'''

from constants import R, S, C
import board
import math
import func

# 正负无穷
MAX = float('inf')
MIN = -MAX

count = 0  # 每次思考的节点数
PVcut = 0
ABcut = 0  # alpha-beta 剪枝次数
Cache = {}  # zobrist 缓存
cacheCount = 0  # zobrist 缓存节点数
cacheGet = 0  # zobrist 缓存命中数量


def r(deep, alpha, beta, role, step, steps, spread):
    global cacheGet, count, ABcut
    # 开启缓存
    if (C["cache"]):
        # 获取缓存中 zobrist 散列键值
        c = Cache[board.zobrist.code]
        if c:
            if c.deep >= deep:
                # 如果缓存中的结果搜索深度不比当前小,则结果完全可用
                cacheGet = cacheGet + 1
                return {
                    "score": c.score.score,
                    "steps": steps,
                    "step": step + c.score.step,
                    "c": c
                }
            else:
                if (func.greatOrEqualThan(c.score, S["FOUR"])
                        or func.littleOrEqualThan(c.score, -S["FOUR"])):
                    cacheGet = cacheGet + 1
                    return c.score

    # 评估函数
    _e = board.evaluate(role)

    leaf = {"score": _e, "step": step, "steps": steps}

    count = count + 1
    #  搜索到底或者已经胜利
    #  注意这里是小于0,而不是1,因为本次直接返回结果并没有下一步棋
    if deep <= 0 or func.greatOrEqualThan(
            _e, score.FIVE) or math.littleOrEqualThan(_e, -score.FIVE):
        return leaf

    best = {"score": MIN, "step": step, "steps": steps}

    # 双方个下两个子之后,开启 star spread 模式
    points = board.gen(role, step > 1 if board.count > 10 else step > 3,
                       step > 1)

    if len(points) == 0:
        return leaf

    for item in points:
        p = item
        board.put(p, role)

        _deep = deep - 1

        _spread = spread

        if _spread < config.spreadLimit:
            #  冲四延伸
            if (role == R.com and p.scoreHum >= score.FIVE) or (
                    role == R.hum and p.scoreCom >= score.FIVE):
                _deep = _deep + 2
                _spread = _spread + 1

        _steps = steps.copy()
        _steps.append(p)

        v = r(_deep, -beta, -alpha, R.reverse(role), step + 1, _steps, _spread)
        v.score = -1 * v.score
        board.remove(p)

        #  注意,这里决定剪枝时使用的值必须比 MAX 小
        if (v.score > best.score):
            best = v

        alpha = math.max(best.score, alpha)
        # alpha-beta 剪枝
        if func.greatOrEqualThan(v.score, beta):
            ABcut = ABcut + 1
            v.score = MAX - 1
            v.abcut = 1  # 剪枝标记
            return v

    cache(deep, best)

    return best


# 缓存
def cache(deep, score):
    global cacheCount
    if not C["cache"]:
        return False
    if score.abcut:
        return False

    Cache[board.zobrist.code] = {
        "deep": deep,
        "score": {
            "score": score.score,
            "steps": score.steps,
            "step": score.step
        },
        board: str(board)
    }

    cacheCount = cacheCount + 1


'''
description: 极大极小值搜索
param {*} candidates: 启发式搜索返回的节点
param {*} role: 落子方
param {*} deep: 搜索深度
param {*} alpha
param {*} beta
return {*} alpha
'''


def negamax(candidates, role, deep, alpha, beta):
    # 每次搜索时重置
    global count, ABcut, PVcut
    count = 0
    ABcut = 0
    PVcut = 0
    board.currentSteps = []

    for item in candidates:
        p = item
        # 在棋盘上落子
        board.put(p, role)
        steps = [p]
        v = r(deep - 1, -beta, -alpha, func.reverse(role), 1, steps.copy(), 0)
        v["score"] = -1 * v["score"]
        alpha = math.max(alpha, v["score"])
        # 从棋盘上移除这个子
        board.remove(p)
        p.v = v
    return alpha


'''
description: 迭代加深
Alpha-beta 剪枝能够找到最优解
比如在第四层找到了一个双三, 但因为评分一致 AI 随机走一条
导致在第六层才找到双三, 虽然都可能赢, 但多走了几步
通过迭代加深找到最短路径
param {*} candidates
param {*} role
param {*} deep
return {*}
'''


def deeping(candidates, role, deep):
    global Cache
    Cache = {}

    # 每次仅尝试偶数层
    for i in range(2, deep, step=2):
        bestScore = negamax(candidates, role, i, MIN, MAX)
        if func.greatOrEqualThan(bestScore, S["FIVE"]):
            break

    # 美化方法
    def bueatiful(d):
        r = [d[0], d[1]]
        r.score = d.v.score
        r.step = d.v.step
        r.steps = d.v.steps
        if d.v.vct:
            r.vct = d.v.vct
        return r

    candidates = list(map(bueatiful, candidates))

    # 排序
    # candidates.sort(function (a, b) {
    #   if math.equal(a.score, b.score):
    #     # 大于零是优势,尽快获胜,因此取步数短的
    #     # 小于0是劣势,尽量拖延,因此取步数长的
    #     if a.score >= 0:
    #       if a.step != b.step:
    #         return a.step - b.step
    #       else:
    #         return b.score - a.score # 否则选取当前分最高的(直接评分)
    #     else:
    #       if a.step != b.step:
    #         return b.step - a.step
    #       else:
    #         return b.score - a.score # 否则选取当前分最高的(直接评分)
    #   else:
    #     return b.score - a.score
    # })

    result = candidates[0]
    # 找到最短路径
    result.min = math.min(list(map(lambda x: x.score), result.steps))

    return result


def deepAll(role=R["com"], deep=C["searchDeep"]):
    # 获取启发式搜索返回的优先搜搜列表
    candidates = board.gen(role)
    return deeping(candidates, role, deep)
