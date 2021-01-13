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
#
# 将输入化为标准型：
# min z = cx
# Ax = b
# x >= 0, b>=0


import numpy as np


class Standardizer:
    def __init__(self, A, b, d, c, e):
        self.A = A.copy()
        self.b = b.copy()
        self.c = c.copy()
        self.cons_type = d.copy()
        self.x_cons_type = e.copy()
        self.x_no_cons = np.array([])  # 无约束的 x 加入 tuple(x的idx, x'的idx)
        self.x_cons_le = np.array([])  # 约束为小于等于 0 的 x 的 idx
        self.less_count = 0
        self.equal_count = 0
        self.more_count = 0
        self.originV_num=0
        self.standardize()
        self.check_number = self.c.copy()

    def standardize(self):
        # step1:
        # 对于无约束变量 x_i 替换为 x_i = x_i‘ - x_i” (x_i',x_i" >= 0)
        # x_cons_type 加一列 1 代表新增的变量
        # 保留原本的 x_i 不变
        # 将A中的所有 x_i 进行替换
        # 第 j 行加一个 -a_ji
        # 将c中的 x_i 替换
        # c 加一列 -c_i
        #
        # 对于约束小于等于的变量 x_i
        # 在 A 中将其系数取反
        # 在 c 中将其系数取反
        x_num = self.x_cons_type.shape[0]
        for i in range(x_num):
            if self.x_cons_type[i] == -1:
                self.x_cons_le = np.append(self.x_cons_le, i)
                self.c[i] = -self.c[i]
                self.A[:, i] = -self.A[:, i]
            elif self.x_cons_type[i] == 0:
                self.x_no_cons = np.append(
                    self.x_no_cons, (i, len(self.x_cons_type)))
                self.x_cons_type = np.append(self.x_cons_type, 1)
                self.A = np.c_[self.A, -self.A[:,i]]
                self.c = np.append(self.c, -self.c[i])
      
        # New step2:
        # 首先将三种情况的约束单独放入三个矩阵中
        # 约束大于等于的情况（cons_type[i] == 1）加入-x将其标准化 同时c中加一个0
        # 将三个矩阵合并，约束为大于（标准化后）和等于的放置于上方，约束为小于等于的放置于下方
        # 向该矩阵添加人工变量和松弛变量，约束为等于(以及标准化后的大于)的添加的是人工变量，约束为小于等于的添加的是松弛变量
        self.originV_num = self.c.size
        A_les = np.array([])
        A_more = np.array([])
        A_equal = np.array([])
        b_les = np.array([])
        b_more = np.array([])
        b_equal = np.array([])
        cons_num = self.cons_type.shape[0]
        for i in range(cons_num):
            if self.b[i] < 0:
                self.A[i] = -self.A[i]
                self.b[i] = -self.b[i]
            if self.cons_type[i] == 1:
                if A_more.size==0:
                    A_more=self.A[i]
                    b_more=self.b[i]
                else:
                    A_more=np.r_[A_more, self.A[i]]
                    b_more=np.c_[b_more, self.b[i]]
                self.more_count += 1
            elif self.cons_type[i] == -1:
                if A_les.size==0:
                    A_les=self.A[i]
                    b_les=self.b[i]
                else:
                    A_les=np.r_[A_les, self.A[i]]
                    b_les=np.c_[b_les, self.b[i]]
                self.less_count += 1
            elif self.cons_type[i] == 0:
                if A_equal.size==0:
                    A_equal=self.A[i]
                    b_equal=self.b[i]
                else:
                    A_equal=np.r_[A_equal, self.A[i]]
                    b_equal=np.c_[b_equal, self.b[i]]
                self.equal_count += 1

        if A_more.size!=0 and A_equal.size!=0:
            tmp = np.r_[A_more, A_equal]
            tmpb=np.c_[b_more, b_equal]
        elif A_more.size==0:
            tmp=A_equal
            tmpb=b_equal
        elif A_equal.size==0:
            tmp=A_more
            tmpb=b_more
        
        if tmp.size!=0 and A_les.size!=0:
            result = np.r_[tmp, A_les]
            resultb = np.c_[tmpb, b_les]
        elif tmp.size==0:
            result =A_les
            resultb =b_les
        elif A_les.size==0:
            result =tmp
            resultb =tmpb
        else:
            print("输入为空！")
            return -1

        # 由松弛变量和人工变量结合成的约束矩阵
        add_mat = np.zeros(
            [cons_num, cons_num+self.more_count], dtype='float')
        # 大于等于的约束中增加-x
        if self.more_count!=0:
            np.fill_diagonal(add_mat[:self.more_count, :self.more_count], -1)
        # 再增加+x,其中一部分是人工变量，一部分是松弛变量
        np.fill_diagonal(add_mat[:, self.more_count:], 1)
        # 更新A矩阵
        result=result.reshape(cons_num,self.c.size)
        self.A = np.c_[result, add_mat]
        self.b=resultb
        # 更新c
        add_mat_c = np.zeros([cons_num+self.more_count], dtype='float')
        self.c=np.append(self.c,add_mat_c)
        #self.c = np.c_[self.c, add_mat_c]
