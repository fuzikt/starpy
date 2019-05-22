#!/usr/bin/env python

import os
import sys
import copy
from math import *
from metadata import MetaData
import argparse
from collections import OrderedDict


class HelixCorrectStar():
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Modify star file to be compatible with helix refinement")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")


    def usage(self):
        self.parser.print_help()


    def error(self, *msgs):
        self.usage()
        print "Error: " + '\n'.join(msgs)
        print " "
        sys.exit(2)


    def validate(self, args):
        if len(sys.argv) == 1:
            self.error("Error: No input file given.")

        if not os.path.exists(args.i):
            self.error("Error: Input file '%s' not found."
                       % args.i)

    def get_particles(self, md):
        particles = []
        for particle in md:
                particles.append(particle)
        return particles

    def helixParticles(self, particles):
        i=1
        for particle in particles:
            particle.rlnHelicalTubeID=i
            particle.rlnAnglePsiFlipRatio=0.5
            particle.rlnHelicalTrackLength=200
            i += 1
        return particles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print "Modifying star file to be compatible with helix refinement."

        md = MetaData(args.i)
        md._addLabel('rlnAnglePsiFlipRatio')
        md._addLabel('rlnHelicalTubeID')
        md._addLabel('rlnHelicalTrackLength')

        mdOut = MetaData()
        mdOut.addLabels(md.getLabels())

        new_particles = []

        particles=self.get_particles(md)

        self.helixParticles(particles)

        mdOut.addData(particles)
        mdOut.write(args.o)

        print "New star file "+args.o+" created. Have fun!"


if __name__ == "__main__":

    HelixCorrectStar().main()
