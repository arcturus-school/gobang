# 迭代加深

每次尝试偶数层, 逐渐增加搜索深度

如果较低的深度能够获胜, 可以不必要增加深度, 提高效率

```python
def deeping(board, candidates, role, deep):

    # 每次仅尝试偶数层
    for i in range(2, deep, 2):
        bestScore = negamax(board, candidates, role, i, MIN, MAX)
        if func.greatOrEqualThan(bestScore, S["FIVE"]):
            # 能赢了就不用再循环了
            break

    # 结果重组
    def rearrange(d):
        r = {
            "p": [d["p"][0], d["p"][1]],
            "score": d["v"]["score"],
            "step": d["v"]["step"],
            "steps": d["v"]["steps"]
        }
        return r

    candidates = list(map(rearrange, candidates))

    # 先找到分数高的, 再找步骤少的
    candidates.sort(key=lambda x: (x["score"], -x["step"]), reverse=True)

    return candidates[0]
```

