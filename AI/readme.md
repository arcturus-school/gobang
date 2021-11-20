# 关于 AI 文件的说明

1. opening.py, evaluate_point.py 需要 python >= 3.10.0,因为使用了 match/case

2. zobrist.py, opening.py 需要 numpy

3. 所有的 board 均是 numpy 的数组, 因此存在 [i, j] 这种用法, 普通 python 列表应该不存在这种用法
