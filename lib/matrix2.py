from math import *


class Matrix2:
    """define Matrix2 class and method to obtain individual matrices from lists with 4 values"""

    def __init__(self, m):
        if m == None:
            self.m = [[0, 0], [0, 0]]
        else:
            self.m = [[0, 0], [0, 0]]
            self.m[0][0] = m[0]
            self.m[0][1] = m[1]
            self.m[1][0] = m[2]
            self.m[1][1] = m[3]

    def set_matrix(self, m):
        self.m[0][0] = m[0]
        self.m[0][1] = m[1]
        self.m[1][0] = m[2]
        self.m[1][1] = m[3]

    def print_matrix(self):
        m = self.m
        print("%.6f\t" % (m[0][0])),
        print("%.6f\t" % (m[0][1]))
        print("%.6f\t" % (m[1][0])),
        print("%.6f\t" % (m[1][1]))


def matrix_from_angle(alpha):
    """create a rotation matrix from given rotation angle (in radians)"""
    a = [0, 0, 0, 0]
    a[0] = cos(alpha)
    a[1] = -sin(alpha)
    a[2] = sin(alpha)
    a[3] = cos(alpha)

    return Matrix2(a)

def matrix_multiply(m1, m2):
    a = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    a[0] = m1.m[0][0] * m2.m[0][0] + m1.m[0][1] * m2.m[1][0]
    a[1] = m1.m[0][0] * m2.m[0][1] + m1.m[0][1] * m2.m[1][1]
    a[2] = m1.m[1][0] * m2.m[0][0] + m1.m[1][1] * m2.m[1][0]
    a[3] = m1.m[1][0] * m2.m[0][1] + m1.m[1][1] * m2.m[1][1]

    return Matrix2(a)


def matrix_transpose(m1):
    m2 = Matrix2(None)
    m2.m[0][0] = m1.m[0][0]
    m2.m[0][1] = m1.m[1][0]
    m2.m[1][0] = m1.m[0][1]
    m2.m[1][1] = m1.m[1][1]
    return m2