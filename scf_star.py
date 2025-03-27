#!/usr/bin/env python3

import os
import sys
from lib.scf import SCFstar
from metadata import MetaData
import argparse
from argparse import RawTextHelpFormatter


class SCFstarCalc:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Calculates the SCF* (Sampling Compensation Factor) for particle orientation distribution in STAR file.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--fourier_radius', type=int, default=50,
            help="Fourier radius (int) of the shell on which sampling is evaluated (Default: 50).")
        add('--samples', type=int, default=0,
            help="The number of random particle orientations from input to use (Default 0 => all particles).")
        add('--tilt_angle', type=int, default=0, help="Tilt angle.")
        add('--sym', type=str, default="C1", help="Symmetry applied to the input particles (Default: C1).")

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

    def get_records(self, md, dataTable):
        records = []
        for record in getattr(md, dataTable):
            records.append(record)
        return records

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        md = MetaData(args.i)

        dataTable = "data_particles"

        records = self.get_records(md, dataTable)

        scfCalculation = SCFstar(records, fourierRadius=args.fourier_radius, numberToUse=args.samples, tiltAngle=args.tilt_angle, sym=args.sym)

        print(f"SCF = {scfCalculation.scf:0.3f}")
        print(f"SCF* = {scfCalculation.scfStar:0.3f}")

        print("An SCF* (Sampling Compensation Factor) value of 0.81 corresponds to the case where we have one ‘band’ of viewing directions. As a result, the original authors of SCF (Baldwin and Lyumkis, 2021) argue that values above 0.81 generally indicate good sampling (though not necessarily isotropic signal content).")

if __name__ == "__main__":
    SCFstarCalc().main()
