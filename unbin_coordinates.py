#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class BinCorrectStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Unbin particle coordinate star files.")
        add = self.parser.add_argument
        add('--i', help="Input directory with coordinates STAR files.")
        add('--o', help="Output directory.")
        add('--bin', type=float, default=1, help="Binning factor used (--bin 10 will multiply input coordinates by 10.")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if len(sys.argv) == 1:
            self.error("No directory given.")

        if not os.path.exists(args.i):
            self.error("Input directory '%s' not found."
                       % args.i)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def unBinCoordinates(self, particles, binnnig):
        newParticles = []
        for particle in particles:
            particle.rlnCoordinateX = particle.rlnCoordinateX * binnnig
            particle.rlnCoordinateY = particle.rlnCoordinateY * binnnig
            newParticles.append(particle)
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        if not os.path.exists(args.o):
            os.makedirs(args.o)
            print("%s output directory created!" % args.o)

        print("Binning correct input star files using binning factor %s." % str(args.bin))

        counter = 0
        nrOfStarFiles = len(os.listdir(args.i))
        for filename in os.listdir(args.i):
            f = os.path.join(args.i, filename)
            # checking if it is a file with extension star
            if os.path.isfile(f) and f.split(".")[-1] == "star":
                md = MetaData(f)
                new_particles = []
                particles = self.get_particles(md)
                new_particles.extend(self.unBinCoordinates(particles, args.bin))
                if md.version == "3.1":
                    mdOut = md.clone()
                    dataTableName = "data_particles"
                    mdOut.removeDataTable(dataTableName)
                else:
                    mdOut = MetaData()
                    dataTableName = "data_"
                mdOut.addDataTable(dataTableName, md.isLoop(dataTableName))
                mdOut.addLabels(dataTableName, md.getLabels(dataTableName))
                mdOut.addData(dataTableName, new_particles)
                mdOut.write(os.path.join(args.o, filename))
                # a simple progress bar
                sys.stdout.write('\r')
                progress = int(counter / nrOfStarFiles * 20)
                sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
                sys.stdout.flush()

                counter += 1
        print("\n %s star files processed. Have fun!" % counter)

if __name__ == "__main__":
    BinCorrectStar().main()
