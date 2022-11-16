# 启发式评估

对整个棋盘空位进行评分, 判断是否能够成五、活四等等
优先对这些可能会获胜的点进行递归, 能够提高搜索速度/剪枝效率

```python
def gen(self, role, onlyThrees):
        if len(self.allSteps) == 0:
            return [7, 7]

        fives = []  # 连五
        com_fours = []  # AI 活四
        hum_fours = []  # 玩家活四
        com_blocked_fours = []  # AI 眠四
        hum_blocked_fours = []  # 玩家眠四
        com_double_threes = []  # AI 双三
        hum_double_threes = []  # 玩家双三
        com_threes = []  # AI 活三
        hum_threes = []  # 玩家活三
        com_twos = []  # AI 活二
        hum_twos = []  # 玩家活二
        neighbors = []  # 附近点

        board = self._board

        for i, item in enumerate(board):
            for j, item_ in enumerate(item):
                if item_ == R["empty"]:
                    if len(self.allSteps) < 6:
                        if not self.hasNeighbor(i, j, 1, 1):
                            # 以 [i, j] 为中心的边长为 3 格的方形范围内
                            # 不存在棋子, 不用考虑这个点了
                            continue
                    elif not self.hasNeighbor(i, j, 2, 2):
                        continue

                    scoreHum = self.humScore[i, j]
                    scoreCom = self.comScore[i, j]
                    # 比较 (i,j) 位置 AI 和人谁的评分更高
                    maxScore = max(scoreCom, scoreHum)

                    if onlyThrees and maxScore < S["THREE"]:
                        continue

                    p = {"p": [i, j], "score": maxScore}

                    if scoreCom >= S["FIVE"] or scoreHum >= S["FIVE"]:
                        # 先看 AI 能不能“连五”, 再看玩家能不能“连五”
                        fives.append(p)
                    elif scoreCom >= S["FOUR"]:
                        # AI 有没有活四
                        com_fours.append(p)
                    elif scoreHum >= S["FOUR"]:
                        # 玩家有没有活四
                        hum_fours.append(p)
                    elif scoreCom >= S["BLOCKED_FOUR"]:
                        # AI 有没有眠四
                        com_blocked_fours.append(p)
                    elif scoreHum >= S["BLOCKED_FOUR"]:
                        # 玩家有没有眠四
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
                        # 什么都没有的就落子在附近
                        neighbors.append(p)

        # 成五
        if len(fives):
            return fives

        # 活四
        if role == R["rival"] and len(com_fours):
            return com_fours
        if role == R["oneself"] and len(hum_fours):
            return hum_fours

        # AI 无冲四玩家有活四
        if role == R["rival"] and len(hum_fours) and len(com_blocked_fours) == 0:
            return hum_fours
        # 玩家不能冲四但 AI 有活四
        if role == R["oneself"] and len(com_fours) and len(hum_blocked_fours) == 0:
            return com_fours

        # 冲四/活四
        if role == R["rival"]:
            # 将 AI 活四排在前面
            fours = com_fours + hum_fours
        else:
            # 将玩家活四排在前面
            fours = hum_fours + com_fours
        
        if role == R["rival"]:
            blockedfours = com_blocked_fours + hum_blocked_fours
        else:
            blockedfours = hum_blocked_fours + com_blocked_fours
        
        if len(fours):
            return fours + blockedfours

        # 双三/活三/眠三等情况
        result = []
        if role == R["rival"]:
            result = (com_double_threes + hum_double_threes +
                      com_blocked_fours + result + hum_blocked_fours +
                      com_threes + hum_threes)
        if role == R["oneself"]:
            result = (hum_double_threes + com_double_threes +
                      hum_blocked_fours + com_blocked_fours + hum_threes +
                      com_threes)

        if len(com_double_threes) or len(hum_double_threes):
            return result

        # 如果只考虑双三的话...
        # 可以直接退出了
        if onlyThrees:
            return result

        # 有活二等情况
        if role == R["rival"]:
            # AI 活二排前面
            twos = com_twos + hum_twos
        else:
            twos = hum_twos + com_twos

        # i
        twos.sort(key=lambda x: x["score"], reverse=True)

        # 如果没有活二就找附近点...
        result.extend(twos if len(twos) else neighbors)

        # 分数低的不用全部计算了
        # 即 gen 返回的节点数不能超过给定值 C["countLimit"]
        if len(result) > C["countLimit"]:
            return result[0:C["countLimit"]]

        return result
```

