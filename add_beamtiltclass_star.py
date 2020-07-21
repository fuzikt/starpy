#!/usr/bin/env python

import os
import sys
from metadata import MetaData
import argparse


class RenameStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Add beamtilt class to the particles.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename.")
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

        if not os.path.exists(args.i):
            self.error("Input file '%s' not found."
                       % args.i)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def addBeamTiltClass(self, particles):
        newParticles = []
        for particle in particles:
            bmtltClass = particle.rlnMicrographName.split("_")[3]
            particle.rlnBeamTiltClass = int(bmtltClass)
            newParticles.append(particle)
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)
        md.addLabels("data_particles", "rlnBeamTiltClass")

        print("Reading in input star file.....")

        particles = self.get_particles(md)

        print("Total %s particles in input star file. \nAdding rlnBeamTiltClass." % str(len(particles)))

        self.addBeamTiltClass(particles)

        mdOut = MetaData()
        mdOut.addDataTable("data_")
        mdOut.addLabels("data_", md.getLabels("data_"))
        mdOut.addData("data_", particles)
        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    RenameStar().main()
