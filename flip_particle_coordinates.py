#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class FlipParticleCoordinates:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Flip (mirror) X/Y coordinates of particles in particles star file or coordinates star files in a directory.")
        add = self.parser.add_argument
        add('--i', type=str, default="", help="Input particles STAR file.")
        add('--o', type=str, default="", help="Output particles STAR file.")
        add('--i_dir', type=str, default="", help="Input directory with coordinates STAR files.")
        add('--o_dir', type=str, default="", help="Output directory.")
        add('--flipX', action='store_true', help="Flip coordinates along X-axis")
        add('--flipY', action='store_true', help="Flip coordinates along Y-axis")
        add('--axis_size', type=float, default=0, help="Size of micrograph in pixels along the flipping axis.")

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

        if args.i != "":
            if args.i_dir != "":
                self.error("You cannot use --i and --i_dir simultaneously")
            if not os.path.exists(args.i):
                self.error("Input star file '%s' not found."
                           % args.i)
            if args.o =="":
                self.error("No --o given. Please set the desired output particle star file when using --i")

        if args.i_dir != "":
            if not os.path.exists(args.i_dir):
                self.error("Input directory '%s' not found."
                           % args.i_dir)
            if args.o_dir =="":
                self.error("No --o_dir given. Please set the desired output direcotry of the coordinate star files when using --i_dir")

        if not args.flipX and not args.flipY:
            self.error("You must define --flipX or --flipY.")

        if args.flipX and args.flipY:
            self.error("Please use only one of: --flipX, --flipY. Simultaneous X/Y flipping not supported (yet).")

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def flipCoordinates(self, particles, axis, axisSize):
        newParticles = []
        for particle in particles:
            coordinateForFlipping = getattr(particle,"rlnCoordinate"+axis)
            particleDistanceFromFlipAxis = abs(coordinateForFlipping - axisSize / 2)
            if coordinateForFlipping >= axisSize/2 :
                setattr(particle, "rlnCoordinate"+axis, coordinateForFlipping - 2*particleDistanceFromFlipAxis)
            else:
                setattr(particle, "rlnCoordinate" + axis,
                        coordinateForFlipping + 2*particleDistanceFromFlipAxis)
            newParticles.append(particle)
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        if args.flipX:
            flipAxis = "X"
        elif args.flipY:
            flipAxis = "Y"

        print("Flipping coordinates along %s axis." % flipAxis)

        if args.i != "":
            md = MetaData(args.i)
            new_particles = []
            particles = self.get_particles(md)
            new_particles.extend(self.flipCoordinates(particles, flipAxis, args.axis_size))
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
            mdOut.write(os.path.join(args.o))

        if args.i_dir != "":
            if not os.path.exists(args.o):
                os.makedirs(args.o)
                print("%s output directory created!" % args.o)

            counter = 0
            nrOfStarFiles = len(os.listdir(args.i))
            for filename in os.listdir(args.i):
                f = os.path.join(args.i, filename)
                # checking if it is a file with extension star
                if os.path.isfile(f) and f.split(".")[-1] == "star":
                    md = MetaData(f)
                    new_particles = []
                    particles = self.get_particles(md)
                    new_particles.extend(self.flipCoordinates(particles, flipAxis, args.axis_size ))
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
                    mdOut.write(os.path.join(args.o_dir, filename))
                    # a simple progress bar
                    sys.stdout.write('\r')
                    progress = int(counter / nrOfStarFiles * 20)
                    sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
                    sys.stdout.flush()

                    counter += 1
            print("\n %s star files processed. Have fun!" % counter)

if __name__ == "__main__":
    FlipParticleCoordinates().main()
