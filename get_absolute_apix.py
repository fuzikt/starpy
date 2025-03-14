#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
from argparse import RawTextHelpFormatter
from math import pi


class AbsoluteApixStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Calculates the absolute apix for the optics groups according to https://www3.mrc-lmb.cam.ac.uk/relion/index.php/Pixel_size_issues",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")


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

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        md = MetaData(args.i)

        if md.version == "3.1":
            iLabels = md.getLabels("data_optics")
        else:
            self.error("Relion 3.1 star file is needed as input.")

        if "rlnEvenZernike" not in iLabels:
            self.error("Zernike 4th order polynomials are not present in the STAR file. Please do a 4th order aberration CTF refinement first.")

        # create output header
        print("| Optics group | Apparent Cs [mm] | realApix [A] |")
        print("|------------------------------------------------|")

        apixSum = 0.0
        csSum = 0.0
        opticsGroupNr = 0

        for optic_group in md.data_optics:
            z40 = float(optic_group.rlnEvenZernike.split(",")[6])
            csTrue = optic_group.rlnSphericalAberration
            nomPixSize = optic_group.rlnImagePixelSize

            # note wavelength is for relativistically corrected accelerating voltage (i.e. 388.06 kV, 239.14 kV and 109.78 kV)
            if optic_group.rlnVoltage == 300:
                waveLength = 0.019687
            elif optic_group.rlnVoltage == 200:
                waveLength = 0.025079
            elif optic_group.rlnVoltage == 100:
                waveLength = 0.037014
            else:
                self.error("Only 100, 200 and 300 kV acceleration voltages are supported.")

            csApparent = csTrue + (12*z40*1e-7)/(pi*waveLength**3)

            realPixSize = nomPixSize * (csTrue/csApparent)**0.25

            print("| %2d           |             %0.2f |        %0.3f |" %(optic_group.rlnOpticsGroup, csApparent, realPixSize))

            opticsGroupNr += 1
            apixSum += realPixSize
            csSum += csApparent

        # Show average values
        print("|------------------------------------------------|")
        print("| Average      |             %0.2f |        %0.3f |" % (csSum/opticsGroupNr, apixSum/opticsGroupNr))
        print("|------------------------------------------------|")

if __name__ == "__main__":
    AbsoluteApixStar().main()