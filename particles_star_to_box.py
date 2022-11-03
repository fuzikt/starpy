#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class ParticlesToBox:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Extracts coordinates from particles STAR file and saves as per micrograph box files.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output directory where the box files will be stored.")
        add('--box_size', type=int, default=256, help="Box size. Default: 256")

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

    def getBoxes(self, particles):
        boxesToSort = []

        def sortFirst(val):
            return val[0]

        for particle in particles:
            micName = particle.rlnMicrographName.split("/")[-1]
            boxFileName = ("%s%s" %(micName[:-3], "box"))
            boxesToSort.append([boxFileName, particle.rlnCoordinateX, particle.rlnCoordinateY])

        boxesToSort.sort(key=sortFirst, reverse=False)

        return boxesToSort

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print("Extracting coordinated of particles per micrograph and storing as box files.")

        md = MetaData(args.i)

        particles = self.get_particles(md)

        boxes = self.getBoxes(particles)

        if not os.path.exists(args.o):
            os.makedirs(args.o)

        micrographName = ""
        boxFile = open("%s/%s" % (args.o, "dummy"), 'w')

        for box in boxes:
            if not box[0] == micrographName:
                boxFile.close()
                boxFile = open("%s/%s" %(args.o, box[0]), 'w')
                micrographName = box[0]
                boxFile.write("%d %d %s %s\n" % (box[1] - int(args.box_size/2), box[2] - int(args.box_size/2), args.box_size, args.box_size))
            else:
                boxFile.write("%d %d %s %s\n" % (box[1] - int(args.box_size / 2), box[2] - int(args.box_size / 2), args.box_size, args.box_size))
        boxFile.close()

        os.remove("%s/%s" % (args.o, "dummy"))

        print("Box-files written out. Have fun!")


if __name__ == "__main__":
    ParticlesToBox().main()
