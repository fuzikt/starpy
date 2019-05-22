#!/usr/bin/env python

import os
import sys
from metadata import MetaData
import argparse
from argparse import RawTextHelpFormatter


class RemoveLabelsStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Remove other columns than particle coords.", formatter_class=RawTextHelpFormatter)
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

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print("Removing columns fromstar file....")

        md = MetaData(args.i)
        md.removeLabels("rlnImageName", "rlnMicrographName", "rlnMagnification", "rlnDetectorPixelSize",
                        "rlnCtfFigureOfMerit", "rlnVoltage", "rlnDefocusU", "rlnDefocusV", "rlnDefocusAngle",
                        "rlnSphericalAberration", "rlnCtfBfactor", "rlnCtfScalefactor", "rlnPhaseShift",
                        "rlnAmplitudeContrast")

        md.write(args.o)

        print("New star file " + args.o + " created. Have fun!")


if __name__ == "__main__":
    RemoveLabelsStar().main()
