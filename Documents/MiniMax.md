# 极大极小搜索

将[报数游戏](Game-Tree.md)中，将甲(自己)获胜用 1 代替，将乙(对手)获胜用 -1 代替

以根节点(树的最顶端)作为第一个极大层(Max)，极小层(Min)和极大层交替出现

极小层中选择子节点最小的数，极大层选择子节点最大的数

> 先手开始选择总是在偶数层(0、2、4...)，而第二个选手开始选择总是在奇数层(1、3、5...)，对应于先手位于极大层，第二个选手位于极小层，也就意味着，位于极大层的选手需要将自身利益最大化，会选择子节点中较大的那个，而位于极小层的选手会将对手的利益最小化，而选择子节点中最小的那个
>

![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/11/202111112147272.jpg)

> 根据上图可知，抽离博弈树的一部分后，这个子树的根节点是 -1，也就是说轮到乙选择了，局势变成这样的话，甲是不可能获胜的，因为乙肯定会选择对甲不利的 -1 这条路线

博弈树的最后结果

![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/11/202111112047620.jpg)

整个博弈树根节点的值所代表的就是先手在这场博弈中的结果(如果比赛双方都遵循最大最小值原则)

那些 -1 都是对甲不利的局面，也就代表了本场比赛的决胜权被对手掌握

# 井字游戏

![井字游戏中的打分](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/11/202111112227746.jpg)

## 打分函数

乙会尽力让评分降低，甲需要让评分更高，因此通过深度优先遍历，选择一条分值高的路径

> 打分函数根据日常经验来制定
>
> 令 α 为 -∞ 是为了让接下来任意一个比这个大的数可以替换掉 -∞

1. 根据给定深度进行遍历(图中仅仅遍历 5 层)

   首先将父节点的 α、β 值传递到子节点中

   ![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/12/202111121348693.jpg)

2. 进行回溯，节点处于 Max 层，因此 α 变成 5

   ![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/12/202111121352259.jpg)

3. 继续遍历兄弟树

   从子节点中 7、4、5 选一个最小的 4 作为 β 的值

   > 由于该兄弟节点的评分较小，回溯时不会改变 Max 层的 α 值

   ![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/12/202111121358688.jpg)

3. 继续回溯至第 1 层，由于是最小层，因此 β 改为 5(目前子节点最小只有 5)

   ![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/12/202111121443129.jpg)

5. 继续遍历第一层第一个节点的右子树

   ![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/12/202111121416220.jpg)

5. 以此类推，获得的最优选择是评分为 6 的路径

   > 这是全部遍历的情况，需要继续优化，参考[α-β剪枝](Alpha-Beta.md)
   
   ![](https://ice-berg.coding.net/p/Other/d/imgur/git/raw/master/2021/11/12/202111121109240.jpg)

## 代码实现

```python

```
