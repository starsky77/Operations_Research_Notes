# 输入格式:
# n m
# c_1 c_2 ... c_n
# a_11 a_12 ... a_1n b1 d1
# a_21 a_22 ... a_2n b2 d2
# ...
# a_m1 a_m2 ... a_mn bm dm
# e_1 e_2 ... e_n
#
# n 决策变量数
# m 约束数
# c_i 决策变量 x_i 系数
# a_ij 第 i 条约束的第 j 个系数
# b_i 第 i 条约束右侧系数
# d_i 第 i 条约束类型 -1（小于） 0（等于） 1（大于）
# e_i x_i 约束 -1（小等0） 0（无约束） 1（大等0）

# 将输入化为标准型：
# min z = cx
# Ax = b
# x >= 0, b>=0

import numpy as np
from standardization import Standardizer
from utils import read_data
import time


class SimplexOptimizer:
    def __init__(self, A, b, d, c, e):
        self.Q = Standardizer(A, b, d, c, e)
        self.more_count  =self.Q.more_count
        self.var_num = self.Q.originV_num                       # 非松弛/人工变量的数目
        self.artiV_num = self.Q.equal_count+self.Q.more_count   # 人工变量数目
        l = [i for i in range(self.var_num+self.Q.more_count,
                              self.Q.A.shape[1])]
        self.sign = list(l)                                     # 基变量序号
        self.con_num = self.Q.A.shape[0]                        # 约束总数
        # 单纯形表
        self.T = np.zeros([self.Q.A.shape[0]+1, self.Q.A.shape[1]+1], dtype='float')
        self.T[:self.Q.A.shape[0], :self.Q.A.shape[1]] = self.Q.A
        self.T[:-1, -1]=self.Q.b
        self.F = 1  # 判断迭代进行的情况：
                    # 1——继续迭代
                    # 0——无界解，停止迭代

        # 预先进行第一阶段的准备
        # 第一阶段：求人工变量之和的min，T矩阵最后一行为-c，最优解条件为z-c<=0
        self.T[-1, self.var_num+self.more_count:self.var_num+self.more_count+ self.artiV_num] = -1 * np.ones(self.artiV_num)
        # 第一阶段:显然，检验数所在的行先加上人工变量所在的行
        for i in range(0, self.artiV_num):
            self.T[-1] += self.T[i]

        #DEBUG
        # print("T origin:")
        # print(self.T)
        # print("###########")


    def solve(self):  # 判断是否到达最优解
        flag = True
        #输出迭代次数：
        count=0
        while flag:
            # 直至所有非基变量检验数小于等于0
            # 合并多个解的情况，即使非基变量检验数等于0也停止迭代
            # print(max(list(self.T[-1][:-1])))
            count+=1
            if max(list(self.T[-1][:-1])) <= 0.0:
                flag = False
            # 迭代，直至某个非基变量检验数等于0
            else:
                self.F = self.calculate()
            # 判断无界解
            if self.F == 0:
                break

    # 进行迭代运算
    def calculate(self):
        H = list(self.T[-1, :-1])
        #选择入基变量
        j_num = H.index(max(H))
        D = []
        noMoreThanZero=True
        #选择出基变量
        for i in range(0, self.con_num):
            if self.T[i][j_num] <= 0:
                D.append(float("inf"))
            else:
                noMoreThanZero=False
                D.append(self.T[i][-1] / self.T[i][j_num])
        # 判断无界解
        if noMoreThanZero : 
            return 0
        # 找出最小比值所在行、列—i_num,j_num
        i_num = D.index(min([x for x in D if x >= 0]))
        self.sign[i_num] = j_num
        t = self.T[i_num][j_num]
        if t==0:
            return 0
        # 换基迭代
        self.T[i_num] /= t
        for i in [x for x in range(0, self.con_num + 1) if x != i_num]:
            self.T[i] -= self.T[i_num] * self.T[i][j_num]
        return 1

    def change(self):  # 准备进入第二阶段
        for i in range(self.var_num,self.var_num+self.artiV_num):
            #检查所有基变量中是否有人工变量，若有，则是否为0，若不为0则无解
            for i in range(0,self.con_num):
                if self.sign[i] in range(self.var_num+self.more_count,self.var_num+self.more_count+self.artiV_num):
                    if self.T[i][-1]!=0:
                        return 0
          
        # 人工变量消去
        self.T[:, self.var_num + self.more_count:self.var_num + self.more_count+self.artiV_num] = 0
        # 更换检验数
        self.T[-1, 0:self.var_num] = -self.Q.c[0:self.var_num]
        # 构造z-c
        for i in range(0, self.con_num):
            self.T[-1] -= self.T[i] * self.T[-1][int(self.sign[i])]
        return 1

    def Main(self):  # 主函数
        OptValue=0
        solve=0

        # 第一阶段求解
        print("phase 1")
        self.solve()
        # 消去人工变量列
        # DEBUG
        # print("T after phase 1")
        # print(self.T)
        flag = self.change()
        if flag == 0:
            solve=-1
            print("-1")
            return -1
        # DEBUG
        # print("T before phase 1")
        # print(self.T)

        # 第二阶段求解
        print("phase 2")
        self.solve()
        # print(self.T)

        #输出结果，非基变量的结果为0，基变量结果为位于其所在行的最后一列
        if self.F==1:
            print("1")
            solve=1
            print(self.T[-1][-1])
            OptValue=self.T[-1][-1]
            #print("Optimal solution:")
            j = 0
            result = np.array([])
            for i in range(0, self.var_num):
                if i not in self.sign:
                    result=np.append(result, 0)
                else:
                    result=np.append(result, self.T[j][-1])
                    j+=1
        else:
            print("0")
            solve=0
            return 0
        if self.Q.x_no_cons.size==0:
            print(result)
        else:
            for i in range(0,int(self.Q.x_no_cons.size/2)):
                new_x=result[int(self.Q.x_no_cons[2*i])]-result[int(self.Q.x_no_cons[2*i+1])]
                result[int(self.Q.x_no_cons[2*i])]=new_x
            print(result[:int(-self.Q.x_no_cons.size/2)])
            result=result[:int(-self.Q.x_no_cons.size/2)]

        return (solve,OptValue,result)
        
# 输出；
# k 为-1 表示线性规划无解，k 为0 表示无有限最优解，k=1 表示存在有限最优解。
if __name__ == "__main__":
    input='agg3'
    #share1b.txt
    #example.txt
    #unbounded.txt
    #infeasible.txt
    #agg3.txt
    A, b, d, c, e = read_data(f'./testdata/{input}.txt')

    time.perf_counter()

    simplex = SimplexOptimizer(A, b, d, c, e)
    print(simplex.Q.A, simplex.Q.b.reshape(
        (-1, 1)), simplex.Q.check_number, sep='\n')

    output=simplex.Main()
    print('Running time: %s Seconds', time.perf_counter())

    with open(f'./testResult/{input}_simplex.out', 'w') as f:
        if not isinstance(output, tuple):
            f.write(f"{str(output)}\n")
        else:
            f.write(f"{str(output[0])}\n")
            if output[0] == 1:
                f.write(str(round(output[1], 8)))
                f.write('\n')
                f.write(str([round(i, 8) for i in output[2]]))
    

    doc = open('./testResult/'+input,'w')
    #print(output.solve,output.OptValue,output.result,file=doc,sep='\n')
    doc.close()
