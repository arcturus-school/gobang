#########################
#         角色          #
#########################

R = {"empty": 0, "rival": 1, "oneself": 2}  # 角色表
r = {1: "black", 2: "white"}  # 执子颜色
tr = {1: "黑", 2: "白"}  # 执子方
NO = [x for x in range(1, 20)]  # 1 到 20 列表, 用于生成棋盘标识

#########################
#        评分标准        #
#########################

S = {
    "ONE": 10,  # 活一
    "TWO": 100,  # 活二
    "THREE": 1000,  # 活三
    "FOUR": 100000,  # 活四
    "FIVE": 10000000,  # 连五

    # 当一侧被封死
    "BLOCKED_ONE": 1,  # 眠一
    "BLOCKED_TWO": 10,  # 眠二
    "BLOCKED_THREE": 100,  # 眠三
    "BLOCKED_FOUR": 10000  # 眠四
}

#########################
#          阈值         #
#########################
threshold = 1.15

#########################
#         配置项         #
#########################
C = {
    "countLimit": 20,  # gen 函数返回的节点数量上限
    "cache": True
}
