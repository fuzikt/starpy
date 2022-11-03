#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class HelixCorrectStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Modify star file to be compatible with helix refinement.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
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

    def helixParticles(self, particles):
        i = 1
        for particle in particles:
            particle.rlnHelicalTubeID = i
            particle.rlnAnglePsiFlipRatio = 0.5
            particle.rlnHelicalTrackLength = 200
            i += 1
        return particles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print("Modifying star file to be compatible with helix refinement.")

        md = MetaData(args.i)

        if md.version == "3.1":
            ilabels = md.getLabels("data_particles")
        else:
            ilabels = md.getLabels("data_")

        if 'rlnAnglePsiFlipRatio' not in ilabels:
            md.addLabels(['rlnAnglePsiFlipRatio'])
        if 'rlnHelicalTubeID' not in ilabels:
            md.addLabels(['rlnHelicalTubeID'])
        if 'rlnHelicalTrackLength' not in ilabels:
            md.addLabels(['rlnHelicalTrackLength'])

        if md.version == "3.1":
            mdOut = md.clone()
            dataTableName = "data_particles"
            mdOut.removeDataTable(dataTableName)
        else:
            mdOut = MetaData()
            dataTableName = "data_"
            
        mdOut.addDataTable(dataTableName)
        mdOut.addLabels(dataTableName, md.getLabels(dataTableName))

        particles = self.get_particles(md)

        self.helixParticles(particles)

        mdOut.addData(dataTableName, particles)
        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    HelixCorrectStar().main()
