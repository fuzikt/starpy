#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
from argparse import RawTextHelpFormatter
import math
from lib.vector3 import dot_product, Vector3
from lib.matrix3 import matrix_from_euler


class analyzeSpatialAngularDistanceStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Calculates the spatial distance and angular distance between corresponding particles in --i1 and --i2. Output contains the particles from --i1 with additional columns for the spatial (rlnSpatDist), angular distances (rlnAngDist), rlnOriginXAngstDiff, rlnOriginYAngstDiff, rlnAngleRotDiff , rlnAngleTiltDiff, and rlnAnglePsiDiff.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i1', help="Input1 STAR filename.")
        add('--i2', help="Input2 STAR filename.")
        add('--o', help="Output STAR filename.")

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

        if not os.path.exists(args.i1):
            self.error("Input1 file '%s' not found." % args.i)

        if not os.path.exists(args.i2):
            self.error("Input2 file '%s' not found." % args.i)

    def get_particles(self, md, dataTableName):
        particles = []
        for particle in getattr(md, dataTableName):
            particles.append(particle)
        return particles

    def rotateVector(self, X, Y, Z, rot, tilt, psi):
        rotation_matrix = matrix_from_euler(rot, tilt, psi)
        Xrot = (rotation_matrix.m[0][0] * X + rotation_matrix.m[0][1] * Y + rotation_matrix.m[0][2] * Z)
        Yrot = (rotation_matrix.m[1][0] * X + rotation_matrix.m[1][1] * Y + rotation_matrix.m[1][2] * Z)
        Zrot = (rotation_matrix.m[2][0] * X + rotation_matrix.m[2][1] * Y + rotation_matrix.m[2][2] * Z)

        return Xrot, Yrot, Zrot

    def angDistance(self, p1, p2):
        v1 = Vector3(self.rotateVector(0, 0, 1, math.radians(p1.rlnAngleRot), math.radians(p1.rlnAngleTilt),
                                       math.radians(p1.rlnAnglePsi)))
        v2 = Vector3(self.rotateVector(0, 0, 1, math.radians(p2.rlnAngleRot), math.radians(p2.rlnAngleTilt),
                                       math.radians(p2.rlnAnglePsi)))
        dp = dot_product(v1, v2) / (v1.length() * v2.length())
        dp = max(min(dp, 1.0), -1.0)
        angle = math.acos(dp)
        return math.degrees(angle)

    def calculateSpatialDistance(self, particle1, particle2):
        if hasattr(particle1, "rlnOriginZAngst") and hasattr(particle2, "rlnOriginXAngst"):
            return ((particle1.rlnOriginXAngst - particle2.rlnOriginXAngst) ** 2 + (
                        particle1.rlnOriginYAngst - particle2.rlnOriginYAngst) ** 2 + (
                                particle1.rlnOriginZAngst - particle2.rlnOriginZAngst) ** 2) ** 0.5
        else:
            return ((particle1.rlnOriginXAngst - particle2.rlnOriginXAngst) ** 2 + (
                        particle1.rlnOriginYAngst - particle2.rlnOriginYAngst) ** 2) ** 0.5

    def normalizedAngleDiff(self, angle1, angle2):
        diff = (angle1 - angle2) % 360.0
        if diff > 180.0:
            diff -= 360.0
        return diff

    def getSpatialAngularDistances(self, particles1, particles2):
        # progress bar initialization
        progress_step = max(int(len(particles1) / 20), 1)
        i = 0

        # Create a dictionary for faster lookup of particles2
        particles2_dict = {p.rlnImageName: p for p in particles2}

        # Process only matching particles
        for particle in particles1:
            if particle.rlnImageName in particles2_dict:
                comp_particle = particles2_dict[particle.rlnImageName]

                # Calculate all distances
                particle.rlnSpatDist = self.calculateSpatialDistance(particle, comp_particle)
                particle.rlnAngDist = self.angDistance(particle, comp_particle)

                particle.rlnAngleRotDiff = self.normalizedAngleDiff(particle.rlnAngleRot, comp_particle.rlnAngleRot)
                particle.rlnAngleTiltDiff = self.normalizedAngleDiff(particle.rlnAngleTilt, comp_particle.rlnAngleTilt)
                particle.rlnAnglePsiDiff = self.normalizedAngleDiff(particle.rlnAnglePsi, comp_particle.rlnAnglePsi)

                # Calculate origin differences
                particle.rlnOriginXAngstDiff = particle.rlnOriginXAngst - comp_particle.rlnOriginXAngst
                particle.rlnOriginYAngstDiff = particle.rlnOriginYAngst - comp_particle.rlnOriginYAngst

            i += 1
            # a simple progress bar
            sys.stdout.write('\r')
            progress = int(i / progress_step)
            sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
            sys.stdout.flush()
        sys.stdout.write('\n')

        return particles1

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print(f"Reading in input star file {args.i1}")
        md1 = MetaData(args.i1)

        print(f"Reading in input star file {args.i2}")
        md2 = MetaData(args.i2)

        print("Analyzing orientational distances...")

        dataTableName = "data_particles"

        if md1.version == "3.1":
            i1labels = md1.getLabels(dataTableName)
        else:
            i1labels = md1.getLabels("data_")
            dataTableName = "data_"

        particles1 = self.get_particles(md1, dataTableName)
        particles2 = self.get_particles(md2, dataTableName)

        if md1.version == "3.1":
            mdOut = md1.clone()
            mdOut.removeDataTable(dataTableName)
        else:
            mdOut = MetaData()
            dataTableName = "data_"

        mdOut.addDataTable(dataTableName, md1.isLoop(dataTableName))
        mdOut.addLabels(dataTableName, i1labels)
        mdOut.addLabels(dataTableName,
                        ["rlnOriginXAngstDiff", "rlnOriginYAngstDiff", "rlnAngleRotDiff", "rlnAngleTiltDiff",
                         "rlnAnglePsiDiff", "rlnSpatDist", "rlnAngDist"])

        mdOut.addData(dataTableName, self.getSpatialAngularDistances(particles1, particles2))

        print("%s particles were processed..." % str((len(particles1))))

        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)
        print(
            f"To plot the histograms of changes, use the following command:\n plot_star.py --i {args.o} --lby rlnOriginXAngstDiff,rlnOriginYAngstDiff,rlnAngleRotDiff,rlnAngleTiltDiff,rlnAnglePsiDiff,rlnAngDist,rlnSpatDist --hist_bin 50 --multiplotY 4,2")


if __name__ == "__main__":
    analyzeSpatialAngularDistanceStar().main()
