#!/usr/bin/env python

import os
import sys
import argparse
from argparse import RawTextHelpFormatter

try:
    from EMAN2 import *
except ImportError:
    print("ERROR: Cannot import EMAN2. Please make sure that EMAN2 is installed and sourced properly!")
    exit()


class json2star:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Convert EMAN2 json type box files into RELION coordinate STAR file.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', help="input directory with json files (EMAN2 info directory location.)")
        add('--o', help="output directory to store STAR files.")
        add('--suffix', type=str, default="_box",
            help="Star file suffix (e.g. \"_box\" will produce micname123_box.star). Default: \"_box\"")
        add('--boxsize', type=int, default="256",
            help="Box size used to exclude boxes that violates micrograph boundaries). Default: 256")
        add('--binning', type=float, default="1",
            help="Binning factor correction. Use when particles we picked on binned micrographs. Default: 1")
        add('--maxX', type=int, default="4096",
            help="Max size of the micrograph in pixels in X dimension (used to exclude boxes from micrograph edges). Default: 4096")
        add('--maxY', type=int, default="4096",
            help="Max size of the micrograph in pixels in Y dimension (used to exclude boxes from micrograph edges). Default: 4096")

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

        if os.path.isdir(args.o) == False:
            os.makedirs(args.o)

        totalBoxesExported = 0
        totalOutsideBoxes = 0
        for fileName in os.listdir(args.i):
            if fileName.endswith(".json"):
                boxarray = []
                inputFile = js_open_dict(args.i + "/" + fileName)
                if "boxes" in inputFile.keys():
                    for box in inputFile["boxes"]:
                        if ((box[0] * args.binning + args.boxsize / 2) < args.maxX) and (
                                (box[1] * args.binning + args.boxsize / 2) < args.maxY) and (
                                (box[0] * args.binning - args.boxsize / 2) > -1) and (
                                (box[1] * args.binning - args.boxsize / 2) > -1):
                            boxarray.append(str(int(box[0] * args.binning)) + " " + str(int(box[1] * args.binning)))
                            totalBoxesExported += 1
                        else:
                            print("Box x: %s, y: %s found to be outside the micrograph boundaries." % (
                            str(int(box[0] * args.binning)), str(int(box[1] * args.binning))))
                            totalOutsideBoxes += 1
                else:
                    print("No boxes were found in %s." % fileName)
                outFileBaseName = os.path.splitext(fileName)[0]
                outFileBaseName = outFileBaseName.replace("_info", "")
                outputFile = open(args.o + "/" + outFileBaseName + args.suffix + ".star", "w")
                outputFile.write("\n")
                outputFile.write("data_\n\n")
                outputFile.write("loop_\n")
                outputFile.write("_rlnCoordinateX #1\n")
                outputFile.write("_rlnCoordinateY #2\n")
                outputFile.write("\n".join(boxarray))
                outputFile.close()
                print("Star file %s%s.star written succesfully." % (outFileBaseName, args.suffix))
        print("--------------------------------------------------------------------")
        print("Total %s boxes were exported to star files." % str(totalBoxesExported))
        print("%s boxes were found outside the micrograph boundaries and were not exported." % str(totalOutsideBoxes))
        print("You can find the generated star files in %s.\n Move them to the micrograph directory for particle extraction by RELION.\n Have fun... See you next time..." % args.o)


if __name__ == "__main__":
    json2star().main()
