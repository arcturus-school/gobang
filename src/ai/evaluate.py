"""
评分函数
"""
from ..constants import R, S
from .. import boards


def s(
    b: boards.AI_board,
    px: int,
    py: int,
    role: int,
    dir: int | None = None,
) -> int:
    """
    给棋盘上某个位置打分, 表示如果下这里会得多少分
    b: 棋盘对象
    px: 评分位置的行坐标
    py: 评分位置的列坐标
    role: 需要评分的角色
    dir: 需要评分的方向
        - None:全部方向
        - 0: 横向
        - 1: 纵向
        - 2: 斜向
        - 3: 斜向
    return: result 评分结果
    """

    board = b.BOARD

    # 注: 四子棋的行数不等于列数
    rlen = board.shape[0]  # 棋盘行数
    clen = board.shape[1]  # 棋盘列数

    result = 0  # 最后分数
    empty = -1
    count = 1  # 一侧的连子数(因为包括当前要走的棋子,所以初始为 1)
    secondCount = 0  # 另一侧的连子数
    block = 0  # 被封死数

    def reset():
        nonlocal count, secondCount, block, empty
        count = 1
        secondCount = 0
        block = 0
        empty = -1

    # 横向 ——
    if dir is None or dir == 0:
        j = py + 1
        while True:
            if j >= clen:
                # 该位置在棋盘边缘,如果下这里,一侧会被封死
                block += 1
                break

            t = board[px, j]
            """
            从想要落子的位置一直往右
            如果一直未被封死
            遇到己方棋子则连子数加一
            遇到对方就退出,不再继续
            碰到空格,那就看它下一个位置是不是己方的
            如果是,那就将 empty 置为 count
            表示该空格到欲落子处有 count 距离
            再继续循环,直到下一次遇到空格或对方棋子时退出
            也就是说空格必须被己方的子给包住
            如果下一个位置不是己方,退出循环
            """
            if t == R["empty"]:
                if empty == -1 and j < clen - 1 and board[px, j + 1] == role:
                    empty = count
                else:
                    break
            # 棋子右侧是己方时
            elif t == role:
                count += 1
            # 棋子右侧是对手时
            else:
                # 右侧被封死
                block += 1
                break
            j += 1

        j = py - 1
        while True:
            if j < 0:
                block += 1
                break

            t = board[px, j]
            """
            从想要落子处一直向左
            遇到己方棋子, 如果之前右边存在空格, empty 就加一
            因为左边多一个棋子,那么起始点到右边空格距离就要加一
            遇到空格, 如果之前右边遍历时不存在空格(即 empty 还是-1)
            那就看下一个位置是不是己方的
            如果是, 那么空格位就在起始位(empty=0)
            继续循环, 遇到己方棋子就让空格往右走一位(empty+=1)
            遇到对方棋子就退出
            如果下一位不是己方棋子, 直接退出, 并且空格位还是之前右边的(如果有的话)
            """
            if t == R["empty"]:
                if empty == -1 and j > 0 and board[px, j - 1] == role:
                    empty = 0
                else:
                    break
            elif t == role:
                secondCount += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break
            j -= 1

        # 落子在这个位置后左右两边的连子数
        count += secondCount

        # 将落子在这个位置后横向分数放入 AI 或玩家的 scoreCache 数组对应位置
        b.SCORECACHE[role][0][px, py] = countToScore(count, block, empty)

    result += b.SCORECACHE[role][0][px, py]

    # 纵向 |
    if dir is None or dir == 1:
        reset()
        i = px + 1

        while True:
            if i >= rlen:
                block += 1
                break

            t = board[i, py]

            if t == R["empty"]:
                if empty == -1 and i < rlen - 1 and board[i + 1, py] == role:
                    empty = count
                else:
                    break
            elif t == role:
                count += 1
            else:
                block += 1
                break
            i += 1

        i = px - 1
        while True:
            if i < 0:
                block += 1
                break

            t = board[i, py]

            if t == R["empty"]:
                if empty == -1 and i > 0 and board[i - 1, py] == role:
                    empty = 0
                else:
                    break
            elif t == role:
                secondCount += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break
            i -= 1

        count += secondCount

        b.SCORECACHE[role][1][px][py] = countToScore(count, block, empty)

    result += b.SCORECACHE[role][1][px][py]

    # 斜向 \
    if dir is None or dir == 2:
        reset()
        i = 1
        while True:
            x = px + i
            y = py + i
            if x >= rlen or y >= clen:
                block += 1
                break

            t = board[x, y]
            if t == R["empty"]:
                if (
                    empty == -1
                    and x < rlen - 1
                    and y < clen - 1
                    and board[x + 1, y + 1] == role
                ):
                    empty = count
                else:
                    break
            elif t == role:
                count += 1
            else:
                block += 1
                break
            i += 1

        i = 1
        while True:
            x = px - i
            y = py - i
            if x < 0 or y < 0:
                block += 1
                break

            t = board[x, y]
            if t == R["empty"]:
                if (
                    empty == -1
                    and x > 0
                    and y > 0
                    and board[x - 1, y - 1] == role  # noqa E501
                ):
                    empty = 0
                else:
                    break
            elif t == role:
                secondCount += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break
            i += 1

        count += secondCount

        b.SCORECACHE[role][2][px][py] = countToScore(count, block, empty)

    result += b.SCORECACHE[role][2][px][py]

    # 斜向 /
    if dir is None or dir == 3:
        reset()
        i = 1
        while True:
            x = px + i
            y = py - i

            if y < 0 or x >= rlen:
                block += 1
                break

            t = board[x, y]
            if t == R["empty"]:
                if (
                    empty == -1
                    and x < rlen - 1
                    and y > 0
                    and board[x + 1, y - 1] == role
                ):
                    empty = count
                else:
                    break
            elif t == role:
                count += 1
            else:
                block += 1
                break
            i += 1

        i = 1
        while True:
            x = px - i
            y = py + i
            if x < 0 or y >= clen:
                block += 1
                break
            t = board[x, y]
            if t == R["empty"]:
                if (
                    empty == -1
                    and x > 0
                    and y < clen - 1
                    and board[x - 1, y + 1] == role
                ):
                    empty = 0
                else:
                    break
            elif t == role:
                secondCount += 1
                if empty != -1:
                    empty += 1
            else:
                block += 1
                break
            i += 1

        count += secondCount

        b.SCORECACHE[role][3][px][py] = countToScore(count, block, empty)

    result += b.SCORECACHE[role][3][px][py]

    return result


def countToScore(count: int, block: int, empty: int) -> int:
    """
    description: 分数计算
    pcount: 连子数
    block: 被封死数
    empty: 空格位置
    return 分数
    """

    if empty <= 0:
        """
        empty = -1: 没有空格
        empty = 0: 不存在这种情况
        """
        if count >= 5:
            # 出现“连五”
            return S["FIVE"]
        if block == 0:
            # 活棋
            match count:
                case 1:
                    return S["ONE"]
                case 2:
                    return S["TWO"]
                case 3:
                    return S["THREE"]
                case 4:
                    return S["FOUR"]
        elif block == 1:
            # 一侧被堵
            match count:
                case 1:
                    return S["BLOCKED_ONE"]
                case 2:
                    return S["BLOCKED_TWO"]
                case 3:
                    return S["BLOCKED_THREE"]
                case 4:
                    return S["BLOCKED_FOUR"]
    elif empty == 1 or empty == count - 1:
        # 表示空格在第二个或者倒数第二个 ●◻●●● 或 ●●◻●
        if count >= 6:
            return S["FIVE"]
        if block == 0:
            match count:
                case 2:
                    return S["TWO"] / 2
                case 3:
                    return S["THREE"]
                case 4:
                    return S["BLOCKED_FOUR"]
                case 5:
                    return S["FOUR"]
        elif block == 1:
            match count:
                case 2:
                    return S["BLOCKED_TWO"]
                case 3:
                    return S["BLOCKED_THREE"]
                case 4:
                    return S["BLOCKED_FOUR"]
                case 5:
                    return S["BLOCKED_FOUR"]
    elif empty == 2 or empty == count - 2:
        # 表示空格在第三个或者倒数第二个 ●●◻●●● 或 ●●●◻●●
        if count >= 7:
            return S["FIVE"]
        if block == 0:
            match count:
                case 3:
                    return S["THREE"]
                case 5:
                    return S["BLOCKED_FOUR"]
                case 6:
                    return S["FOUR"]
        elif block == 1:
            match count:
                case 3:
                    return S["BLOCKED_THREE"]
                case 4:
                    return S["BLOCKED_FOUR"]
                case 5:
                    return S["BLOCKED_FOUR"]
                case 6:
                    return S["FOUR"]
        elif block == 2:
            match count:
                case 6:
                    return S["BLOCKED_FOUR"]
    elif empty == 3 or empty == count - 3:
        if count >= 8:
            return S["FIVE"]
        if block == 0:
            match count:
                case 5:
                    return S["THREE"]
                case 6:
                    return S["BLOCKED_FOUR"]
                case 7:
                    return S["FOUR"]

        elif block == 1:
            match count:
                case 6:
                    return S["BLOCKED_FOUR"]
                case 7:
                    return S["FOUR"]
        elif block == 2:
            match count:
                case 7:
                    return S["BLOCKED_FOUR"]
    elif empty == 4 or empty == count - 4:
        if count >= 9:
            return S["FIVE"]
        if block == 0:
            match count:
                case 8:
                    return S["FOUR"]
        elif block == 1:
            match count:
                case 7:
                    return S["BLOCKED_FOUR"]
                case 8:
                    return S["FOUR"]
        elif block == 2:
            match count:
                case 8:
                    return S["BLOCKED_FOUR"]
    elif empty == 5 or empty == count - 5:
        # empty 最多为五
        # 表示落一子后空格前可连五(empty=count)
        return S["FIVE"]
    return 0
