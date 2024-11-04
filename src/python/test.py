import numpy as np

def rotmat(vec: np.ndarray, ang: float) -> np.ndarray:

    k = np.array([[0, -vec[2], vec[1]], [vec[2], 0, -vec[0]], [-vec[1], vec[0], 0]])
    return np.eye(3) + np.sin(ang) * k + (1 - np.cos(ang)) * k @ k

def five(g: np.ndarray) -> tuple:
 
    u = np.arccos(np.sqrt(g[4]**2 + g[5]**2 + g[6]**2))
    v = np.arctan2(g[4], g[5])
    r = np.array([g[1], g[2], g[3]]).reshape((3, 1))
    R = rotmat(np.array([np.sin(u), 0, np.cos(u)]), v) @ rotmat(np.array([0, 1, 0]), u)
    r1 = R @ r
    return ('G01', r1[0, 0], r1[1, 0], r1[2, 0], u, v)

def cube(x: int, t: int) -> list:

    return [('G01', x/2, -x/2, i, 0, -1, 0) for i in range(0, x, t)] + \
           [('G01', x/2, x/2, i, 1, 0, 0) for i in range(0, x, t)] + \
           [('G01', -x/2, x/2, i, 0, 1, 0) for i in range(0, x, t)] + \
           [('G01', -x/2, -x/2, i, -1, 0, 0) for i in range(0, x, t)]

for i in cube(50, 10):
    print(five(i))  # Corrected typo: use 'i' from the loop
