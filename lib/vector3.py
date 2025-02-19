# **************************************************************************
# *
# * Authors:  Serban Ilca
# *           Juha T. Huiskonen (juha@strubi.ox.ac.uk)
# *
# * Oxford Particle Imaging Centre,
# * Division of Structural Biology, University of Oxford
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# **************************************************************************

import re
from math import *
from .euler import euler_from_vector
from .matrix3 import matrix_from_euler


class Vector3:
    """ Define Vector3 class and method to obtain individual vectors from
    lists with 3 values.
    """

    def __init__(self, v):
        if v == None:
            self.v = [0, 0, 1]
        else:
            self.v = v

        # Initialize the vector distance to zero and matrix to None
        self._distance = 0.0
        self._matrix = None

    def set_vector(self, v):
        self.v = v

    def set_distance(self, d):
        self._distance = float(d)

    def compute_distance(self):
        self.set_distance(self.length())

    def compute_matrix(self):
        """ Compute rotation matrix to align Z axis to this vector. """
        rot, tilt, psi = euler_from_vector(self)
        self._matrix = matrix_from_euler(rot, tilt, psi)

    def matrix(self):
        return self._matrix

    def data(self):
        return self.v

    def print_vector(self):
        x, y, z = self.v
        print("[%.3f,%.3f,%.3f]" % (x, y, z)),

    def distance(self):
        return self._distance

    def length(self):
        x, y, z = self.v
        return sqrt(x ** 2 + y ** 2 + z ** 2)

    def normalize(self):
        try:
            self.scale(1. / self.length())
        except ZeroDivisionError:
            self.v[0] = 0
            self.v[1] = 0
            self.v[2] = 0

    def scale(self, distance):
        """ Multiply the vector elements by the distance """
        self.v[0] *= distance
        self.v[1] *= distance
        self.v[2] *= distance

    def x(self):
        return self.v[0]

    def y(self):
        return self.v[1]

    def z(self):
        return self.v[2]

    def __getitem__(self, i):
        """ Allow v[i] syntax with the vector. """
        return self.v[i]

    def clone(self):
        return Vector3(list(self.v))


def dot_product(v1, v2):
    """returns the dot product of two vectors"""

    x1, y1, z1 = v1.v
    x2, y2, z2 = v2.v

    return x1 * x2 + y1 * y2 + z1 * z2


def cross_product(v1, v2):
    """returns the cross product of two vectors"""

    x1, y1, z1 = v1.v
    x2, y2, z2 = v2.v

    x = y1 * z2 - y2 * z1
    y = z1 * x2 - z2 * x1
    z = x1 * y2 - x2 * y1

    return Vector3([x, y, z])


def matrix_product(M, v):
    """ Multiply matrix M by vector v.
    Return resulting vector: M * v. """
    return Vector3([dot_product(Vector3(row), v) for row in M.m])


def vector_from_two_eulers(rot, tilt):
    """function that obtains a vector from the first two Euler angles"""

    x = sin(tilt) * cos(rot)
    y = sin(tilt) * sin(rot)
    z = cos(tilt)
    return Vector3([x, y, z])


def vectors_from_cmm(input_cmm, angpix):
    """function that obtains the input vector from a cmm file"""

    # coordinates in the CMM file need to be in Angstrom

    file_cmm = open(input_cmm, "r")
    vector_list = []
    counter = 0

    for line in file_cmm.readlines():
        if 'marker id=' in line:
            line_values = line.split()
            for i in range(len(line_values)):
                if 'x=' in line_values[i]:
                    a = re.search('"(.*)"', line_values[i]).group(0)
                    x = float(a.translate(str.maketrans({'"': ''}))) / angpix
                if 'y=' in line_values[i]:
                    b = re.search('"(.*)"', line_values[i]).group(0)
                    y = float(b.translate(str.maketrans({'"': ''}))) / angpix
                if 'z=' in line_values[i]:
                    c = re.search('"(.*)"', line_values[i]).group(0)
                    z = float(c.translate(str.maketrans({'"': ''}))) / angpix

            if counter != 0:
                vector = Vector3(None)
                x = x - x0
                y = y - y0
                z = z - z0
                vector.set_vector([x, y, z])
                vector_list.append(vector)
                counter = counter + 1
                continue
            else:
                x0 = x
                y0 = y
                z0 = z
                counter = counter + 1
                continue
        else:
            continue

    return vector_list


def vectors_from_string(input_str):
    """ Function to parse vectors from an string.
    Our (arbitrary) convention is:
    x1,y1,z1; x2,y2,z2 ... etc
    """
    vectors = []

    for vectorStr in input_str.split(';'):
        v = Vector3(None)
        v.set_vector([float(x) for x in vectorStr.split(',')])
        vectors.append(v)

    return vectors