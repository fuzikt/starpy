#!/usr/bin/env python3

import os
import sys
import copy
from math import *
from metadata import MetaData
import argparse
from argparse import RawTextHelpFormatter


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


def matrix_from_euler(rot, tilt, psi):
    """create a rotation matrix from three Euler angles in ZYZ convention"""
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


def euler_from_matrix(matrix):
    """converts a matrix to Eulers - as in Relion euler.cpp"""
    FLT_EPSILON = 1.19209e-07
    sign = lambda x: x and (1, -1)[x < 0]

    abs_sb = sqrt(matrix.m[0][2] * matrix.m[0][2] + matrix.m[1][2] * matrix.m[1][2])
    if abs_sb > 16 * FLT_EPSILON:
        psi = atan2(matrix.m[1][2], -matrix.m[0][2])
        rot = atan2(matrix.m[2][1], matrix.m[2][0])
        if abs(sin(psi)) < FLT_EPSILON:
            sign_sb = sign(-matrix.m[0][2] / cos(psi))
        else:
            sign_sb = sign(matrix.m[1][2]) if (sin(psi) > 0) else -sign(matrix.m[1][2])
        tilt = atan2(sign_sb * abs_sb, matrix.m[2][2])
    else:
        if sign(matrix.m[2][2]) > 0:
            rot = 0
            tilt = 0
            psi = atan2(-matrix.m[1][0], matrix.m[0][0])
        else:
            rot = 0
            tilt = pi
            psi = atan2(matrix.m[1][0], -matrix.m[0][0])
    return rot, tilt, psi


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


def euler_from_vector(vector):
    """converts a view vector to Eulers that describe a rotation taking the reference vector [0,0,1] on the vector"""
    x = vector[0]
    y = vector[1]
    z = vector[2]
    distance = sqrt(x ** 2 + y ** 2 + z ** 2)
    # normalize
    try:
        x *= 1 / distance
        y *= 1 / distance
        z *= 1 / distance
    except ZeroDivisionError:
        x = 0
        y = 0
        z = 0

    if abs(x < 0.00001 and abs(y) < 0.00001):
        rot = radians(0.00)
        tilt = acos(z)
    else:
        rot = atan2(y, x)
        tilt = acos(z)

    psi = 0

    return rot, tilt, psi


class xFlipParticlesStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Perform transformation of euler angles to produce X-flipped reconstruction (same as the result of --invert_hand in relion_image_handler on a map).",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--cls_nr', type=str, default="-1",
            help="Comma-separated list of class numbers to be flipped (Default: -1 => off).")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Input file '%s' not found."
                       % args.i)
        # Convert comma-separated string to list of integers
        try:
            self.classNumbers = [int(x.strip()) for x in args.cls_nr.split(',')]
        except ValueError:
            self.error("Class numbers must be comma-separated integers")

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def xflipParticles(self, particles, classNumbers):

        flippedParticleCounter = 0
        newParticles = []
        for particle in copy.deepcopy(particles):
            if (-1 in classNumbers) or (particle.rlnClassNumber in classNumbers):
                matrix_particle = matrix_from_euler(radians(particle.rlnAngleRot), radians(particle.rlnAngleTilt),
                                                    radians(particle.rlnAnglePsi))
                matrix_rotation = matrix_from_euler(radians(180), radians(180), radians(0))

                m_rot = matrix_multiply(matrix_particle, matrix_transpose(matrix_rotation))

                rotNew, tiltNew, psiNew = euler_from_matrix(m_rot)
                particle.rlnAngleRot = degrees(rotNew)
                particle.rlnAngleTilt = degrees(tiltNew)
                particle.rlnAnglePsi = degrees(psiNew) - 180
                particle.rlnOriginYAngst = -particle.rlnOriginYAngst
                flippedParticleCounter += 1

            newParticles.append(particle)
        self.mprint("Processed " + str(len(newParticles)) + " particles.")
        self.mprint("Flipped " + str(flippedParticleCounter) + " particles.")

        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        self.mprint("X-flipping particles from star file...")

        md = MetaData(args.i)

        new_particles = []

        particles = self.get_particles(md)

        new_particles.extend(self.xflipParticles(particles, self.classNumbers))

        if md.version == "3.1":
            mdOut = md.clone()
            dataTableName = "data_particles"
            mdOut.removeDataTable(dataTableName)
        else:
            mdOut = MetaData()
            dataTableName = "data_"

        mdOut.addDataTable(dataTableName, md.isLoop(dataTableName))
        mdOut.addLabels(dataTableName, md.getLabels(dataTableName))
        mdOut.addData(dataTableName, new_particles)

        mdOut.write(args.o)

        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    xFlipParticlesStar().main()
