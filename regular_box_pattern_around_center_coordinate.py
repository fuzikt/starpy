#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
from copy import deepcopy
from math import sqrt


class ParticlesToCoordsStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Creates a regular pattern of small boxes around the center coordinate of the particle")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output directory where the coords files will be stored.")
        add('--orig_box', type=int, default=512,
            help="Size of the box in pixels around the center coordinate of the original particles. (Default: 512)")
        add('--pattern_box', type=int, default=128,
            help="Size of the box in the regular pattern. (Default: 128)")
        add('--overlap', type=int, default=30,
            help="Overlap in percents between the neighboring boxes in pattern. (Default: 30)")
        add('--sph_mask', action='store_true',
            help="If set then only boxes inside a spherical mask touching the orig_box are included.")

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

    def writeCoordsFile(self, partCoords, outDir):
        mdOut = MetaData()
        particleTableName = "data_"

        mdOut.addDataTable(particleTableName, True)
        mdOut.addLabels(particleTableName, "rlnCoordinateX", "rlnCoordinateY")
        mdOut.addData(particleTableName, partCoords)
        micName = partCoords[0].rlnMicrographName.split("/")[-1]
        starFileName = ("%s%s" % (micName[:-3], "star"))
        mdOut.write(outDir + "/" + starFileName)

    def createRegularPatternAroundCoordinates(self, partCoords, origBoxSize, patternBoxSize, overlap, sphMask):
        patternCoords = []

        patternBoxSize = patternBoxSize * (1 - overlap / 100)

        # progress bar initialization
        progress_step = max(int(len(partCoords) / 20), 1)
        i = 0

        for coord in partCoords:
            row = 0

            ycoord = coord.rlnCoordinateY - origBoxSize / 2 + row * patternBoxSize / 2

            while ycoord + patternBoxSize / 2 <= coord.rlnCoordinateY + origBoxSize / 2:
                column = 0
                xcoord = coord.rlnCoordinateX - origBoxSize / 2 + column * patternBoxSize / 2
                while xcoord + patternBoxSize / 2 <= coord.rlnCoordinateX + origBoxSize / 2:
                    if (sphMask and (sqrt((coord.rlnCoordinateX - xcoord) ** 2 + (
                            coord.rlnCoordinateY - ycoord) ** 2) < origBoxSize / 2)) or not sphMask:
                        patternCoord = deepcopy(coord)
                        patternCoord.rlnCoordinateX = xcoord
                        patternCoord.rlnCoordinateY = ycoord
                        patternCoords.append(patternCoord)

                    column += 1
                    xcoord = coord.rlnCoordinateX - origBoxSize / 2 + column * patternBoxSize

                row += 1
                ycoord = coord.rlnCoordinateY - origBoxSize / 2 + row * patternBoxSize

            # a simple progress bar
            sys.stdout.write('\r')
            progress = int(i / progress_step)
            sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
            sys.stdout.flush()
            i += 1

        sys.stdout.write('\r\n')
        return patternCoords

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        if not os.path.exists(args.o):
            print("Creating output directory: %s" % args.o)
            os.makedirs(args.o)

        print("Creating regular pattern around particle coordinates listed in input file....")

        md = MetaData(args.i)

        particles = self.get_particles(md)

        partCoords = []

        while len(particles) > 0:
            partCoords.append(particles.pop(0))
            if len(particles) != 0:
                particlePos = 0
                while particlePos < len(particles):
                    if partCoords[0].rlnMicrographName == particles[particlePos].rlnMicrographName:
                        partCoords.append(particles.pop(particlePos))
                        particlePos -= 1
                    particlePos += 1

            patternCoords = self.createRegularPatternAroundCoordinates(partCoords, args.orig_box, args.pattern_box,
                                                                       args.overlap, args.sph_mask)
            self.writeCoordsFile(patternCoords, args.o)
            partCoords = []

        print("Star-files written out. Have fun!")


if __name__ == "__main__":
    ParticlesToCoordsStar().main()
