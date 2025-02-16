#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter


class CreateMicrographStarFile:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Create a micrographs star containing unique micrograph names file form input particles star file.",
            formatter_class=RawTextHelpFormatter)
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
            self.error("Input1 file '%s' not found." % args.i)

    def get_particles(self, md, dataTableName):
        particles = []
        for particle in getattr(md, dataTableName):
            particles.append(particle)
        return particles

    def filterUniqueMicrographs(self, particles):
        uniqueMicsMetadata = []
        uniqueMicsName = []

        for particle in particles:
            if particle.rlnMicrographName not in uniqueMicsName:
                uniqueMicsMetadata.append(particle)
                uniqueMicsName.append(particle.rlnMicrographName)
        return uniqueMicsMetadata

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print("Selecting unique micrographs from particles star file...")

        md = MetaData(args.i)

        particles = self.get_particles(md, "data_particles")

        opticGroups = self.get_particles(md, "data_optics")

        for opticGroup in opticGroups:
            opticGroup.rlnMicrographPixelSize = opticGroup.rlnMicrographOriginalPixelSize

        opticGroupLabels = md.getLabels("data_optics")
        opticGroupLabels.remove("rlnImagePixelSize")
        opticGroupLabels.append("rlnMicrographPixelSize")
        md.removeLabels("data_optics", "rlnImagePixelSize")
        md.addLabels("data_optics", "rlnMicrographPixelSize")

        uniqueMicrographs = self.filterUniqueMicrographs(particles)


        mdOut = md.clone()
        mdOut.removeDataTable("data_particles")

        ilabels = ["rlnMicrographName", "rlnDefocusU", "rlnDefocusV", "rlnDefocusAngle", "rlnPhaseShift", "rlnCtfBfactor", "rlnOpticsGroup"]

        mdOut.addDataTable("data_micrographs", True)
        mdOut.addLabels("data_micrographs", ilabels)

        mdOut.addData("data_micrographs", uniqueMicrographs)

        print("%s micrographs were processed..." % str((len(uniqueMicrographs))))

        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    CreateMicrographStarFile().main()