#!/usr/bin/env python

import os
import sys
from metadata import MetaData
import argparse
import struct


class SplitStacks:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Split MRC stacks listed in STAR file into separate files, and writes a new STAR file with split files info.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename.")
        add('--o_dir', default="splitStacks", help="Output folder.")
        add('--o_pref', default="image", help="Output image prefix.")

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

    def splitMrcStack(self, stackFile, outFile):
        # extract filename, image index
        imageIndex, mrcsFilename = stackFile.split("@")
        imageIndex = int(imageIndex)

        # read in mrcs file, open mrc file for output
        mrcsFile = open(mrcsFilename, "rb")
        mrcFile = open(outFile, 'wb+')

        # get image size
        imageSize = int(struct.unpack('i', mrcsFile.read(4))[0])

        # write header
        mrcsFile.seek(0, 0)
        chunkSize = 1024
        mrcHeader = mrcsFile.read(chunkSize)
        mrcFile.write(mrcHeader)

        # change Z dimension to 1
        mrcFile.seek(8, 0)
        mrcFile.write(b"\x01")
        mrcFile.seek(1024, 0)

        # write mrc data file
        mrcsFile.seek(imageSize ** 2 * 4 * (imageIndex - 1) + 1024, 0)
        chunkSize = imageSize ** 2 * 4
        mrcImage = mrcsFile.read(chunkSize)
        mrcFile.write(mrcImage)

        mrcsFile.close()
        mrcFile.close()

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)

        print("Reading in input star file.....")

        if not os.path.exists(args.o_dir):
            os.makedirs(args.o_dir)

        for i, particle in enumerate(md, start=1):
            outputImageName = '%s/%s_%06d.mrc' % (args.o_dir, args.o_pref, i)
            self.splitMrcStack(particle.rlnImageName, outputImageName)
            particle.rlnImageName = outputImageName
            particle.rlnMicrographName = outputImageName

        md.write(args.o_pref + ".star")

        print("Total %s images created from MRC stacks." % str(i))

        print("New star file %s.star created. Have fun!" % args.o_pref)


if __name__ == "__main__":
    SplitStacks().main()
