#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class ParticlesToCoordsStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Extracts coordinates from particles STAR file and saves as per micrograph coords star files.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output directory where the coords files will be stored.")

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

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print("Extracting coordinates of particles per micrograph and storing as coords star files.")

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
            self.writeCoordsFile(partCoords, args.o)
            partCoords = []

        print("Star-files written out. Have fun!")


if __name__ == "__main__":
    ParticlesToCoordsStar().main()
