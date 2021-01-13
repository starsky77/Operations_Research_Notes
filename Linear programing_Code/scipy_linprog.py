import numpy as np
from scipy.optimize import linprog
from standardization import Standardizer
from utils import read_data

out_Path = 'testAnswer/'
input_path = 'testdata/'
inputfile = 'agg3'

if __name__ == "__main__":
    A, b, d, c, e = read_data(f'{input_path}{inputfile}.txt')
    np_c = np.array(c)
    A_le = []
    b_le = []
    A_eq = []
    b_eq = []
    bounds = []
    for i in range(len(d)):
        if d[i] == -1:
            A_le.append(A[i].copy())
            b_le.append(b[i])
        elif d[i] == 0:
            A_eq.append(A[i].copy())
            b_eq.append(b[i])
        elif d[i] == 1:
            A_le.append([-k for k in A[i]])
            b_le.append(-b[i])

    for i in range(len(e)):
        if e[i] == -1:
            bounds.append((None,0))
        elif e[i] == 0:
            bounds.append((None,None))
        elif e[i] == 1:
            bounds.append((0, None))

    c = np.array(c)
    A_le = np.array(A_le)
    b_le = np.array(b_le)
    A_eq = np.array(A_eq)
    b_eq = np.array(b_eq)

    try:
        if len(b_le) == 0:
            res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
        elif len(b_eq) == 0:
            res = linprog(c, A_ub=A_le, b_ub=b_le, bounds=bounds)
        else:
            res = linprog(c, A_ub=A_le, b_ub=b_le, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
    except ValueError as e:
        with open(f"{out_Path}{inputfile}.txt","w") as f:
            f.write("0\n")
        # print(0)
    else:
        if res.success:
            with open(f"{out_Path}{inputfile}.txt", "w") as f:
                f.write("1\n")
                f.write(str(round(res.fun,8)))
                f.write('\n')
                f.write(str([round(i, 8) for i in res.x]))

            # print(1)
            # print(round(res.fun,8))
            # print([round(i, 8) for i in res.x])
        else:
            with open(f"{out_Path}{inputfile}.txt", "w") as f:
                f.write("-1\n")