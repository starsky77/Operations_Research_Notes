## 关于Integrality gap的问题

对于Integrality gap不能过大的解释：

考虑利用LP rounding的近似算法，在最小化问题中：对于线性规划的最优解$M_{fract}$总是会通过舍入（rounding）的方式获取整数最优解$M_{int}$，即$M_{int}=M_{fract}*RR$；其中$RR$是舍入比例，且$RR$作为近似比的上限。根据Integrality gap的定义，

上面这里还没有搞得太清楚，主要是这里不清楚$RR$到底是什么含义。



考虑老师PPT的内容，实际上当Integrality gap较大时，会导致近似比的上界大大增加（因为Integrality gap是近似比上界的下界），这将导致近似比更有可能偏大，这里之所以说更有可能，是因为理论上这不是一个严格的约束，可以从不等关系中看到，近似比还是有可能比Integrality gap小的，但是按照维基上的说法，这一点很难证明，而且在实践结果中，当Integrality gap较大时往往会得出一个很差的近似比。



顺带一提，在某校lecture notes中的说法，Integrality gap较大意味着利用rounding的策略时，产生的偏差会更大，从而可能导致更差的近似比。

