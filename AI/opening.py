'''
26种开局
中心点开局
棋盘生成
'''
import numpy as np


# 创建一个 n × m 的全 0 棋盘
# 默认五子棋棋盘
def create_zeros_board(m=15, n=15):
    b = np.zeros([m, n], dtype=int)

    return b


# 中心点开局
def board_open_center(n=15, m=15):
    b = np.zeros([n, m], dtype=int)
    # 中心落一子
    x = np.floor(n)
    y = np.floor(m)
    b[x, y] = 1

    return b

########################################
#           以下仅五子棋                #
########################################


# 花月开局
def huayue_open(s):
    # 根据玩家不同的落子点选择不同的花月开局
    match s:
        case [6, 7]:
            return [6, 8]
        case [7, 6]:
            return [6, 6]
        case [8, 7]:
            return [8, 6]
        case [7, 8]:
            return [8, 8]
    # 因为必匹配,因此不需要 case _:


# 浦月开局
def puyue_open(s):
    match s:
        case [6, 6]:
            return [6, 8]
        case [8, 6]:
            return [6, 6]
        case [8, 8]:
            return [8, 6]
        case [6, 8]:
            return [8, 8]


# AI 根据情况走第二个子
def open_match(board):
    # 获取棋路
    s = board.allSteps

    # 判断第一步是否是 AI 下的,不是就退出
    if board.board[s[0][0], s[0][1]] != 1:
        return False

    # 判断走了多少步,超过两步不能用花月和浦月了
    if len(s) > 2:
        return False

    # 若 AI 先手,则 s[0] 是 AI 下的
    # s[1] 是玩家下的

    # 玩家棋子落在中心点旁边上、下、左、右的其中一个位置
    a1 = [[6, 7], [7, 6], [8, 7], [7, 8]]
    # 玩家棋子落在中心点旁边左上、右上、左下、右下的其中一个位置
    a2 = [[6, 6], [8, 8], [8, 6], [6, 8]]
    if s[1] in a1:
        # 使用花月开局
        return huayue_open(s[1])
    elif s[1] in a2:
        # 使用浦月开局
        return puyue_open(s[1])
    return False


# 以下是五子棋的一些开局
# AI 先手,AI 已走两步,玩家已走一步

def create_zhizhi_board(n=15, m=15):
    b = np.zeros([n, m], dtype=int)
    b[7, 7] = 1
    b[6, 7] = 2

    return b


def create_xiezhi_board(n=15, m=15):
    b = np.zeros([n, m], dtype=int)
    b[7, 7] = 1
    b[6, 8] = 2

    return b


open26 = dict()

# 直止打法
shuxing = {"name": "疏星", "board": create_zhizhi_board()}
shuxing["board"][5][5] = 1

xiyue = {"name": "溪月", "board": create_zhizhi_board()}
xiyue["board"][5][6] = 1

hanxing = {"name": "寒星", "board": create_zhizhi_board()}
hanxing["board"][5][7] = 1

canyue = {"name": "残月", "board": create_zhizhi_board()}
canyue["board"][6][5] = 1

huayue = {"name": "花月", "board": create_zhizhi_board()}
huayue["board"][6][6] = 1

jinyue = {"name": "金星", "board": create_zhizhi_board()}
jinyue["board"][7][5] = 1

yuyue = {"name": "雨月", "board": create_zhizhi_board()}
yuyue["board"][7][6] = 1

xinyue = {"name": "新月", "board": create_zhizhi_board()}
xinyue["board"][8][5] = 1

qiuyue = {"name": "丘月", "board": create_zhizhi_board()}
qiuyue["board"][8][6] = 1

songyue = {"name": "松月", "board": create_zhizhi_board()}
songyue["board"][8][7] = 1

youxing = {"name": "游星", "board": create_zhizhi_board()}
youxing["board"][9][5] = 1

shanyue = {"name": "山月", "board": create_zhizhi_board()}
shanyue["board"][9][6] = 1

ruixing = {"name": "瑞星", "board": create_zhizhi_board()}
ruixing["board"][9][7] = 1


# 斜止打法
liuxing = {"name": "流星", "board": create_xiezhi_board()}
liuxing["board"][5][5] = 1

shuiyue = {"name": "水月", "board": create_xiezhi_board()}
shuiyue["board"][5][6] = 1

hengxing = {"name": "恒星", "board": create_xiezhi_board()}
hengxing["board"][5][7] = 1

xiayue = {"name": "峡月", "board": create_xiezhi_board()}
xiayue["board"][5][8] = 1

changyue = {"name": "长月", "board": create_xiezhi_board()}
changyue["board"][5][9] = 1

lanyue = {"name": "岚月", "board": create_xiezhi_board()}
lanyue["board"][6][5] = 1

puyue = {"name": "浦月", "board": create_xiezhi_board()}
puyue["board"][6][6] = 1

yunyue = {"name": "云月", "board": create_xiezhi_board()}
yunyue["board"][6][7] = 1

mingxing = {"name": "明星", "board": create_xiezhi_board()}
mingxing["board"][7][5] = 1

yinyue = {"name": "银月", "board": create_xiezhi_board()}
yinyue["board"][7][6] = 1

ming2yue = {"name": "名月", "board": create_xiezhi_board()}
ming2yue["board"][8][5] = 1

xieyue = {"name": "斜月", "board": create_xiezhi_board()}
xieyue["board"][8][6] = 1

huixing = {"name": "慧星", "board": create_xiezhi_board()}
huixing["board"][9][5] = 1

open26.update({
    "shuxing": shuxing,
    "xiyue": xiyue,
    "hanxing": hanxing,
    "canyue": canyue,
    "huayue": huayue,
    "jinyue": jinyue,
    "yuyue": yuyue,
    "xinyue": xinyue,
    "qiuyue": qiuyue,
    "songyue": songyue,
    "youxing": youxing,
    "shanyue": shanyue,
    "ruixing": ruixing,
    "liuxing": liuxing,
    "shuiyue": shuiyue,
    "hengxing": hengxing,
    "xiayue": xiayue,
    "changyue": changyue,
    "lanyue": lanyue,
    "puyue": puyue,
    "yunyue": yunyue,
    "mingxing": mingxing,
    "yinyue": yinyue,
    "ming2yue": ming2yue,
    "xieyue": xieyue,
    "huixing": huixing
})
