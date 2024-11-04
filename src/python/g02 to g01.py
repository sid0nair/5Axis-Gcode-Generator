import math
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

def circular_interpolation(
    start_point,
    end_point,
    center_of_curvature,
    step
) :

    if np.allclose( start_point,  end_point):
        raise ValueError("Start and end points cannot be identical")

    if step <= 0:
        raise ValueError("Step size must be positive")

    radius = math.hypot(start_point[0] - center_of_curvature[0], start_point[1] - center_of_curvature[1])

    start_angle = math.atan2(start_point[1] - center_of_curvature[1], start_point[0] - center_of_curvature[0])
    end_angle = math.atan2(end_point[1] - center_of_curvature[1], end_point[0] - center_of_curvature[0])

    points = []
    angle = start_angle
    while angle < end_angle:
        x = center_of_curvature[0] + radius * math.cos(angle)
        y = center_of_curvature[1] + radius * math.sin(angle)
        points.append((x, y))
        angle += step

    points.append(end_point)

    return points

def translate(g1,g2,step):
    p1=np.array((g1[1],g1[2],g1[3]))
    p2=np.array((g2[1],g2[2],g2[3]))
    c=np.array((g1[1]+g2[4],g1[2]+g2[5],g1[3]+g2[6]))
    n=np.cross(c-p1,c-p2)
    unit=n/(np.linalg.norm(n))
    if g2[0]=='G03': un=unit
    else: un=-unit
    u = np.arccos(np.sqrt(un[0]**2 + un[1]**2 + un[2]**2))
    v = np.arctan2(un[0], un[1])
    R = rotmat(np.array([np.sin(u), 0, np.cos(u)]), v) @ rotmat(np.array([0, 1, 0]), u)
    r1=R@p1
    r2=R@p2
    c1=R@c
    return circular_interpolation(r1[:2],r2[:2],c1[:2],step)


print(translate(('G00',1,0,0),('G03',0,1,0,-1,0,0),0.1))

