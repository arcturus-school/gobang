'''
极大极小值搜索
'''

from Func.constants import R, S, C
import AI.func as func

# 正负无穷
MAX = S["FIVE"] * 10
MIN = -MAX

count = 0  # 每次思考的节点数
ABcut = 0  # alpha-beta 剪枝次数
Cache = {}  # zobrist 缓存
cacheCount = 0  # zobrist 缓存节点数
cacheGet = 0  # zobrist 缓存命中数量


def r(board, deep, alpha, beta, role, step, steps, spread):
    '''
    :param {int} deep: 搜索深度
    :param {} alpha:
    :param {} beta:
    :param {} role:
    :param {int} step:
    :param {list} steps:
    :param {} spread:
    :return {dist} leaf/best:
    '''
    global cacheGet, count, ABcut
    # 开启缓存
    if C["cache"]:
        # 获取缓存中与 zobrist 散列键值相同的缓存数据
        c = Cache.get(board._zobrist.code)
        if c:
            if c["deep"] >= deep:
                # 如果缓存中的结果搜索深度不比当前小, 则结果完全可用
                cacheGet += 1
                return {
                    "score": c["score"]["score"],
                    "steps": steps,
                    "step": step + c["score"]["step"]
                }
            else:
                if (func.greatOrEqualThan(c["score"]["score"], S["FOUR"])
                        or func.littleOrEqualThan(c["score"]["score"],
                                                  -S["FOUR"])):
                    # 如果缓存的结果中搜索深度比当前小
                    # 那么任何一方出现双三及以上结果的情况下可用
                    cacheGet += 1
                    return {
                        "score": c["score"]["score"],
                        "steps": steps,
                        "step": step + c["score"]["step"]
                    }

    # 评估函数
    _e = board.evaluate(role)

    leaf = {"score": _e, "step": step, "steps": steps}

    count += 1  # 思考节点数加一

    # 搜索到底或者已经胜利
    # 注意这里是小于 0, 而不是 1
    # 因为本次直接返回结果并没有下一步棋
    if (deep <= 0 or func.greatOrEqualThan(_e, S["FIVE"])
            or func.littleOrEqualThan(_e, -S["FIVE"])):
        return leaf

    best = {"score": MIN, "step": step, "steps": steps}

    # 获取需要评分的节点
    points = board.gen(role)

    # 如果没有需要评分的节点, 即当前节点是树叶, 直接返回
    if len(points) == 0:
        return leaf

    # 对需要评分的子节点进行循环遍历
    for item in points:
        board.AIput(item["p"], role)  # 在可能获胜的节点上落子
        _deep = deep - 1
        _spread = spread
        print("r", _spread)

        # if _spread < C["spreadLimit"]:
        #     #  冲四延伸
        #     if (role == R["com"] and item.get("scoreHum") >= S["FIVE"]) or (
        #             role == R["hum"] and item.get("scoreCom") >= S["FIVE"]):
        #         _deep += 2
        #         _spread += 1

        _steps = steps.copy()
        _steps.append(item)

        # 进行递归
        v = r(board, _deep, -beta, -alpha, func.reverse(role), step + 1,
              _steps, _spread)
        v["score"] = -1 * v["score"]

        board.AIremove(item["p"])  # 在棋盘上删除这个子

        #  注意, 这里决定剪枝时使用的值必须比 MAX 小
        if v["score"] > best["score"]:
            best = v

        # 将 alpha 值与子节点分数做比较, 选出最大的分数给 alpha
        alpha = max(best["score"], alpha)
        # alpha-beta 剪枝
        if func.greatOrEqualThan(v["score"], beta):
            ABcut += 1  # 剪枝数加一
            v["score"] = MAX - 1  # 被剪枝的用极大值来记录, 但是必须比 MAX 小
            v["abcut"] = 1  # 剪枝标记
            return v

    cache(board, deep, best)

    return best


def cache(board, deep, score):
    '''
    分数缓存
    '''
    global cacheCount
    if not C["cache"]:
        # 不开启缓存
        return
    if score.get("abcut"):
        # 被剪枝的, 不是所有都有 abcut, 因此要用 get
        return

    Cache[board._zobrist.code] = {
        "deep": deep,
        "score": {
            "score": score["score"],
            "steps": score["steps"],
            "step": score["step"]
        }
    }

    global cacheCount
    cacheCount += 1


def negamax(board, candidates, role, deep, alpha, beta):
    '''
    负极大值搜索
    :param {list} candidates
    :param {int} role: 落子方
    :param {int} deep: 搜索深度
    :param {int} alpha
    :param {int} beta
    :return {int} alpha
    '''
    # 每次搜索时重置
    global count, ABcut
    count = 0
    ABcut = 0
    board.currentSteps = []

    for item in candidates:
        # 在棋盘上落子
        board.AIput(item["p"], role)
        v = r(board, deep - 1, -beta, -alpha, func.reverse(role), 1, [item], 0)
        v["score"] = -1 * v["score"]
        alpha = max(alpha, v["score"])
        # 从棋盘上移除这个子
        board.AIremove(item["p"])
        item["v"] = v
    return alpha


def deeping(board, candidates, role, deep):
    '''
    迭代加深
    Alpha-beta 剪枝能够找到最优解
    比如在第四层找到了一个双三, 但因为评分一致 AI 随机走一条
    导致在第六层才找到双三, 虽然都可能赢, 但多走了几步
    通过迭代加深找到最短路径
    :param {list} candidates
    :param {int} role
    :param {int} deep: 搜索深度
    :return {list} 落子坐标
    '''
    global Cache
    Cache = {}

    # 每次仅尝试偶数层
    for i in range(2, deep, 2):
        '''
        传入 candidates 进行迭代
        同时修改 candidates 里的 step、score 等值
        一开始是没有 v 的, 只有 p, 经过 negamax 后才有
        candidate = [{
            "p": [x, y],
            "v": {
                "score": xxx,
                "step": xxx,
                "steps": [{
                    "p": [x, y],
                    "step": xxx,
                    "steps": xxx
                }, {{
                    "p": [x, y],
                    "step": xxx,
                    "steps": xxx
                }}]
            }
        },{...}]
        '''
        bestScore = negamax(board, candidates, role, i, MIN, MAX)
        if func.greatOrEqualThan(bestScore, S["FIVE"]):
            # 能赢了就不用再循环了
            break

    # 结果重排
    def rearrange(d):
        r = {
            "p": [d["p"][0], d["p"][1]],
            "score": d["v"]["score"],
            "step": d["v"]["step"],
            "steps": d["v"]["steps"]
        }
        return r

    candidates = list(map(rearrange, candidates))

    # 先找到分数高的, 在找步骤少的
    candidates.sort(key=lambda x: (x["score"], -x["step"]), reverse=True)

    result = candidates[0]["p"]

    return result


def deepAll(board, deep, role=R["rival"]):
    # 获取启发式搜索返回的优先搜搜列表
    candidates = board.gen(role)
    return deeping(board, candidates, role, deep)
