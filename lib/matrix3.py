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

import os
import sys
from math import *


class Matrix3:
    """define Matrix3 class and method to obtain individual matrices from lists with 9 values"""

    def __init__(self, m):
        if m == None:
            self.m = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        else:
            self.m = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            self.m[0][0] = m[0]
            self.m[0][1] = m[1]
            self.m[0][2] = m[2]
            self.m[1][0] = m[3]
            self.m[1][1] = m[4]
            self.m[1][2] = m[5]
            self.m[2][0] = m[6]
            self.m[2][1] = m[7]
            self.m[2][2] = m[8]

    def set_matrix(self, m):
        self.m[0][0] = m[0]
        self.m[0][1] = m[1]
        self.m[0][2] = m[2]
        self.m[1][0] = m[3]
        self.m[1][1] = m[4]
        self.m[1][2] = m[5]
        self.m[2][0] = m[6]
        self.m[2][1] = m[7]
        self.m[2][2] = m[8]

    def print_matrix(self):
        m = self.m
        print("%.6f\t" % (m[0][0])),
        print("%.6f\t" % (m[0][1])),
        print("%.6f\t" % (m[0][2]))
        print("%.6f\t" % (m[1][0])),
        print("%.6f\t" % (m[1][1])),
        print("%.6f\t" % (m[1][2]))
        print("%.6f\t" % (m[2][0])),
        print("%.6f\t" % (m[2][1])),
        print("%.6f\t" % (m[2][2]))


def run_command(command, output, library_path):
    import subprocess

    env = os.environ.copy()
    try:
        env['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH'] + ":" + library_path
    except:
        env['LD_LIBRARY_PATH'] = library_path

    if not output:
        print("+++ " + command)
        sys.stdout.flush()
        proc = subprocess.Popen(command, shell=True, env=env)
        proc.wait()
    else:
        print("+++ " + command)
        sys.stdout.flush()
        with open(output, "wb", 0) as out:
            proc = subprocess.Popen(command, shell=True, stdout=out, env=env)
            proc.wait()


def matrix_from_euler(rot, tilt, psi):
    """create a rotation matrix from three Euler anges in ZYZ convention"""
    a = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    a[0] = cos(psi) * cos(tilt) * cos(rot) - sin(psi) * sin(rot)
    a[1] = cos(psi) * cos(tilt) * sin(rot) + sin(psi) * cos(rot)
    a[2] = -cos(psi) * sin(tilt)
    a[3] = -sin(psi) * cos(tilt) * cos(rot) - cos(psi) * sin(rot)
    a[4] = -sin(psi) * cos(tilt) * sin(rot) + cos(psi) * cos(rot)
    a[5] = sin(psi) * sin(tilt)
    a[6] = sin(tilt) * cos(rot)
    a[7] = sin(tilt) * sin(rot)
    a[8] = cos(tilt)

    return Matrix3(a)


def matrix_from_euler_zxz(rot, tilt, psi):
    """create a rotation matrix from three Euler anges in ZXZ convention"""
    a = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    a[0] = cos(psi) * cos(rot) - sin(psi) * cos(tilt) * sin(rot)
    a[1] = -cos(psi) * sin(rot) - sin(psi) * cos(tilt) * cos(rot)
    a[2] = sin(psi) * sin(tilt)
    a[3] = sin(psi) * cos(rot) + cos(psi) * cos(tilt) * sin(rot)
    a[4] = -sin(psi) * sin(rot) + cos(psi) * cos(tilt) * cos(rot)
    a[5] = -cos(psi) * sin(tilt)
    a[6] = sin(tilt) * sin(rot)
    a[7] = sin(tilt) * cos(rot)
    a[8] = cos(tilt)

    return Matrix3(a)


def matrix_from_euler_zyx(rot, tilt, psi):
    #   """create a rotation matrix from three Euler anges in ZYX convention"""
    a = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    a[0] = cos(rot) * cos(tilt)
    a[1] = cos(rot) * sin(tilt) * sin(psi) - sin(rot) * cos(psi)
    a[2] = cos(rot) * sin(tilt) * cos(psi) + sin(rot) * sin(psi)
    a[3] = sin(rot) * cos(tilt)
    a[4] = sin(rot) * sin(tilt) * sin(psi) + cos(rot) * cos(psi)
    a[5] = sin(rot) * sin(tilt) * cos(psi) - cos(rot) * sin(psi)
    a[6] = -sin(tilt)
    a[7] = cos(tilt) * sin(psi)
    a[8] = cos(tilt) * cos(psi)

    return Matrix3(a)


def matrix_from_euler_xyz(rot, tilt, psi):
    #   """create a rotation matrix from three Euler anges in XYZ convention"""
    a = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    a[0] = cos(tilt) * cos(psi)
    a[1] = -cos(tilt) * sin(psi)
    a[2] = sin(tilt)
    a[3] = cos(rot) * sin(psi) + sin(rot) * sin(tilt) * cos(psi)
    a[4] = cos(rot) * cos(psi) - sin(rot) * sin(tilt) * sin(psi)
    a[5] = -sin(rot) * cos(tilt)
    a[6] = sin(rot) * sin(psi) - cos(rot) * sin(tilt) * cos(psi)
    a[7] = sin(rot) * cos(psi) + cos(rot) * sin(tilt) * sin(psi)
    a[8] = cos(rot) * cos(tilt)

    return Matrix3(a)


def matrix_multiply(m1, m2):
    a = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    a[0] = m1.m[0][0] * m2.m[0][0] + m1.m[0][1] * m2.m[1][0] + m1.m[0][2] * m2.m[2][0]
    a[1] = m1.m[0][0] * m2.m[0][1] + m1.m[0][1] * m2.m[1][1] + m1.m[0][2] * m2.m[2][1]
    a[2] = m1.m[0][0] * m2.m[0][2] + m1.m[0][1] * m2.m[1][2] + m1.m[0][2] * m2.m[2][2]
    a[3] = m1.m[1][0] * m2.m[0][0] + m1.m[1][1] * m2.m[1][0] + m1.m[1][2] * m2.m[2][0]
    a[4] = m1.m[1][0] * m2.m[0][1] + m1.m[1][1] * m2.m[1][1] + m1.m[1][2] * m2.m[2][1]
    a[5] = m1.m[1][0] * m2.m[0][2] + m1.m[1][1] * m2.m[1][2] + m1.m[1][2] * m2.m[2][2]
    a[6] = m1.m[2][0] * m2.m[0][0] + m1.m[2][1] * m2.m[1][0] + m1.m[2][2] * m2.m[2][0]
    a[7] = m1.m[2][0] * m2.m[0][1] + m1.m[2][1] * m2.m[1][1] + m1.m[2][2] * m2.m[2][1]
    a[8] = m1.m[2][0] * m2.m[0][2] + m1.m[2][1] * m2.m[1][2] + m1.m[2][2] * m2.m[2][2]
    return Matrix3(a)


def matrix_transpose(m1):
    m2 = Matrix3(None)
    m2.m[0][0] = m1.m[0][0]
    m2.m[0][1] = m1.m[1][0]
    m2.m[0][2] = m1.m[2][0]
    m2.m[1][0] = m1.m[0][1]
    m2.m[1][1] = m1.m[1][1]
    m2.m[1][2] = m1.m[2][1]
    m2.m[2][0] = m1.m[0][2]
    m2.m[2][1] = m1.m[1][2]
    m2.m[2][2] = m1.m[2][2]
    return m2


def matrix_from_symmetry(symString, library_path):
    """ Create the symmetry matrices from a given string using Relion convention.
    We use use 'relion_refine --sym' to generate the symmetry file and
    then parse it to load the matrices. """
    tmpSymFile = "relion_symops.tmp"
    relion_create_symmetry_ops_file(symString, tmpSymFile, library_path)
    matrices = matrix_from_symmetry_ops_file(tmpSymFile)
    try:
        os.remove(tmpSymFile)
    except OSError:
        pass

    return matrices


def relion_create_symmetry_ops_file(symString, filename, library_path):
    """ Create a symmetry operator file
    by running relion_refine --print_symmetry_ops."""
    run_command('relion_refine --sym %s --print_symmetry_ops --o ./ > %s' % (symString, filename), "", library_path)


def matrix_from_symmetry_ops_file(filename):
    """ Obtain the lists with 9 values for the set_matrix method
    by a symmetry operator file. """

    f = open(filename, 'r')

    allMatrices = []
    matrixLine = 0
    matrixFound = False

    for line in f:
        values = line.split()

        if " R(" in line:
            matrixFound = True
            matrixLine = 0
            a = []
            continue

        if matrixFound:
            a.extend(map(float, values[:3]))
            matrixLine += 1

            if matrixLine == 3:
                allMatrices.append(Matrix3(a))
                matrixFound = False

    f.close()

    return allMatrices
