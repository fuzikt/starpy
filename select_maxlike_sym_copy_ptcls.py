#!/usr/bin/env python

import os
import sys
import random
from metadata import MetaData
import argparse


class RandSymStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Select random orientation from symmetry expanded star files. One orientation per particle.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")

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

    def maxLikeParticle(self, symCopies):
        maxLikeParticle = symCopies[0]
        for particle in symCopies:
            if particle.rlnMaxValueProbDistribution > maxLikeParticle.rlnMaxValueProbDistribution:
                maxLikeParticle.rlnMaxValueProbDistribution = particle.rlnMaxValueProbDistribution
        return maxLikeParticle

    def randParticles(self, particles):
        i = 1
        newParticles = []
        symmCopies = []
        firstRound = 1
        # read in symmetry copies of particle
        while len(particles) > 0:
            symmCopies.append(particles.pop(0))
            if len(particles) != 0:
                while symmCopies[0].rlnImageName == particles[0].rlnImageName:
                    symmCopies.append(particles.pop(0))
                    if len(particles) == 0: break
            if firstRound == 1:
                print("Detected " + str(len(symmCopies)) + "-fold symmetry.")
                firstRound = 0
            newParticles.append(self.maxLikeParticle(symmCopies))
            symmCopies = []
        print("Selected " + str(len(newParticles)) + " random particles from their symmetry copies.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)

        new_particles = []

        print("Reading in input star file.....")

        particles = self.get_particles(md)

        print("Total %s particles in input star file. \nSelecting random particles from their symmetry copies." % str(
            len(particles)))

        new_particles.extend(self.randParticles(particles))

        mdOut = MetaData()
        if md.version == "3.1":
            mdOut.version = "3.1"
            mdOut.addDataTable("data_optics")
            mdOut.addLabels("data_optics", md.getLabels("data_optics"))
            mdOut.addData("data_optics", getattr(md, "data_optics"))
            particleTableName = "data_particles"
        else:
            particleTableName = "data_"

        mdOut.addDataTable(particleTableName)
        mdOut.addLabels(particleTableName, md.getLabels(particleTableName))
        mdOut.addData(particleTableName, new_particles)

        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    RandSymStar().main()