import numpy as np

def read_data(path):
    with open(path, 'r') as f:
        data = f.readlines()
        line = 0
        n, m = list(map(int, data[line].split()))
        line += 1
        c = np.array(list(map(float, data[line].split())))
        line += 1
        b = []
        d = []
        A = []
        for i in range(m):
            input_line = list(map(float, data[line + i].split()))
            A.append(input_line[:-2].copy())
            b.append(input_line[-2])
            d.append(input_line[-1])
        line += m
        A = np.array(A)
        b = np.array(b)
        d = np.array(d)
        e = np.array(list(map(float, data[line].split())))
        return A, b, d, c, e