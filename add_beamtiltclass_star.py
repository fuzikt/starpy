#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class AddBeamTiltClass:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Add beamtilt class to the particles.")
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")

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

        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Input file '%s' not found."
                       % args.i)
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

        self.mprint("Reading in input star file.....")

        particles = self.get_particles(md)

        self.mprint("Total %s particles in input star file. \nAdding rlnBeamTiltClass." % str(len(particles)))

        self.addBeamTiltClass(particles)

        mdOut = MetaData()
        mdOut.addDataTable("data_", True)
        mdOut.addLabels("data_", md.getLabels("data_"))
        mdOut.addData("data_", particles)
        mdOut.write(args.o)

        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    AddBeamTiltClass().main()
