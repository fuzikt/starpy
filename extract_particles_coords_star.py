#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
from argparse import RawTextHelpFormatter


class ExtractParticlesCoordsStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Remove other columns than particle coords.", formatter_class=RawTextHelpFormatter)
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
        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Input file '%s' not found." % args.i)

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)
    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        self.mprint("Removing columns from star file....")

        md = MetaData(args.i)
        md.removeLabels("data_particles", "rlnImageName", "rlnMicrographName", "rlnMagnification", "rlnDetectorPixelSize",
                        "rlnCtfFigureOfMerit", "rlnVoltage", "rlnDefocusU", "rlnDefocusV", "rlnDefocusAngle",
                        "rlnSphericalAberration", "rlnCtfBfactor", "rlnCtfScalefactor", "rlnPhaseShift",
                        "rlnAmplitudeContrast")

        md.write(args.o)

        self.mprint("New star file " + args.o + " created. Have fun!")


if __name__ == "__main__":
    ExtractParticlesCoordsStar().main()
