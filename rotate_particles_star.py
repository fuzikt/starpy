#!/usr/bin/env python

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


class RotateParticlesStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Perform rotation of particles according to given euler angles. \n Example: rotate_particles_star.py --i input.star --o output.star --rot 15 --tilt 20 --psi 150",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--rot', type=str, default="0",
            help="Rotattion Euler angle. Default 0")
        add('--tilt', type=str, default="0",
            help="Tilt Euler angle. Default 0")
        add('--psi', type=str, default="0",
            help="Psi Euler angle. Default 0")
        add('--x', type=str, default="0",
            help="Shift along X axis. Default 0 (in px for Relion 3.0; in Angstrom for Relion 3.1)")
        add('--y', type=str, default="0",
            help="Shift along Y axis. Default 0 (in px for Relion 3.0; in Angstrom for Relion 3.1)")
        add('--z', type=str, default="0",
            help="Shift along Z axis. Default 0 (in px for Relion 3.0; in Angstrom for Relion 3.1)")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if len(sys.argv) == 1:
            self.error("No input file given.")

        if not os.path.exists(args.i):
            self.error("Input file '%s' not found."
                       % args.i)

        self.rotValue = 0.0
        self.tiltValue = 0.0
        self.psiValue = 0.0
        self.xValue = 0.0
        self.yValue = 0.0
        self.zValue = 0.0

        try:
            self.rotValue = float(args.rot)
        except ValueError:
            self.error("Attribute '%s' requires FLOAT value for operation." % args.rot)

        try:
            self.tiltValue = float(args.tilt)
        except ValueError:
            self.error("Attribute '%s' requires FLOAT value for operation." % args.tilt)

        try:
            self.psiValue = float(args.psi)
        except ValueError:
            self.error("Attribute '%s' requires FLOAT value for operation." % args.psi)

        try:
            self.xValue = float(args.x)
        except ValueError:
            self.error("Attribute '%s' requires FLOAT value for operation." % args.x)

        try:
            self.yValue = float(args.y)
        except ValueError:
            self.error("Attribute '%s' requires FLOAT value for operation." % args.y)

        try:
            self.zValue = float(args.z)
        except ValueError:
            self.error("Attribute '%s' requires FLOAT value for operation." % args.z)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def rotateParticles(self, particles, rot, tilt, psi, x, y, z, version):

        newParticles = []
        for particle in copy.deepcopy(particles):
            matrix_particle = matrix_from_euler(radians(particle.rlnAngleRot), radians(particle.rlnAngleTilt),
                                                radians(particle.rlnAnglePsi))
            matrix_rotation = matrix_from_euler(radians(rot), radians(tilt), radians(psi))

            shiftRot, shiftTilt, shiftPsi = euler_from_vector([x, y, z])
            matrix_shift = matrix_from_euler(shiftRot, shiftTilt, shiftPsi)

            m_shift = matrix_multiply(matrix_particle, matrix_transpose(matrix_shift))
            m_rot = matrix_multiply(matrix_particle, matrix_transpose(matrix_rotation))

            rotNew, tiltNew, psiNew = euler_from_matrix(m_rot)
            particle.rlnAngleRot = degrees(rotNew)
            particle.rlnAngleTilt = degrees(tiltNew)
            particle.rlnAnglePsi = degrees(psiNew)

            d = sqrt(x ** 2 + y ** 2 + z ** 2)
            if version == "3.1":
                particle.rlnOriginXAngst = -m_shift.m[0][2] * d + particle.rlnOriginXAngst
                particle.rlnOriginYAngst = -m_shift.m[1][2] * d + particle.rlnOriginYAngst
                if hasattr(particle, 'rlnOriginZAngst'):
                    particle.rlnOriginZAngst = -m_shift.m[2][2] * d + particle.rlnOriginZAngst
            else:
                particle.rlnOriginX = -m_shift.m[0][2] * d + particle.rlnOriginX
                particle.rlnOriginY = -m_shift.m[1][2] * d + particle.rlnOriginY
                if hasattr(particle, 'rlnOriginZ'):
                    particle.rlnOriginZ = -m_shift.m[2][2] * d + particle.rlnOriginZ

            newParticles.append(particle)
        print("Processed " + str(len(newParticles)) + " particles.")

        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print("Performing rotation of particles from star file...")

        md = MetaData(args.i)

        new_particles = []

        particles = self.get_particles(md)

        new_particles.extend(self.rotateParticles(particles, self.rotValue, self.tiltValue, self.psiValue, self.xValue, self.yValue, self.zValue, md.version))
        mdOut = MetaData()

        if md.version == "3.1":
            mdOut.version = "3.1"
            mdOut.addDataTable("data_optics")
            mdOut.addLabels("data_optics", md.getLabels("data_optics"))
            mdOut.addData("data_optics", getattr(md, "data_optics"))
            particleTableName = "data_particles"
        else:
            particleTableName = "data_"

        mdOut.addDataTable(particleTableName)
        mdOut.addLabels(particleTableName, md.getLabels(particleTableName))
        mdOut.addData(particleTableName, new_particles)

        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    RotateParticlesStar().main()