#!/usr/bin/env python

import os
import sys
import copy
from math import *
from metadata import MetaData
import argparse
from collections import OrderedDict


class BinCorrectStar():
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Binning correct original star file according to the binning factor. Correcting rlnOriginX, rlnOriginY, pixel size, and particle suffix.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--bin_factor', type=float, default=1,
              help="Binning factor.")
        add('--suf_orig', type=str, default="mrcs",
              help="Original suffix to replace (e.g. _512.mrcs).")
        add('--suf_new', type=str, default="mrcs",
              help="New suffix to use for replacment (e.g. _256.mrcs).")


    def usage(self):
        self.parser.print_help()


    def error(self, *msgs):
        self.usage()
        print "Error: " + '\n'.join(msgs)
        print " "
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

    def binParticles(self, particles, binFactor, correctOrigin, correctApix, suf_orig, suf_new):
        newParticles = []
        for particle in copy.deepcopy(particles):
            if correctOrigin == True:
                particle.rlnOriginX = particle.rlnOriginX / binFactor
                particle.rlnOriginY = particle.rlnOriginY / binFactor
            if correctApix == True:
                particle.rlnDetectorPixelSize = particle.rlnDetectorPixelSize * binFactor
            particle.rlnImageName=particle.rlnImageName.replace(suf_orig, suf_new)
            newParticles.append(particle)
        print("Processed "+str(len(newParticles))+" particles.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print "Binning correct input star file. Using binning factor "+str(args.bin_factor)+"."

        md = MetaData(args.i)
        mdOut = MetaData()
        mdOut.addLabels(md.getLabels())

        new_particles = []

        particles=self.get_particles(md)

        if (hasattr(particles[0], 'rlnOriginX')) and (hasattr(particles[0], 'rlnOriginY')):
            correctOrigin = True
        else:
            print("Note: rlnOriginX or rlnOriginY not found in input star file. Not correcting for particle shift.")
            correctOrigin = False

        if hasattr(particles[0], 'rlnDetectorPixelSize'):
            correctApix = True
        else:
            print("Note: rlnDetectorPixelSize not found in input star file. Not correcting for pixel size.")
            correctApix = False

        new_particles.extend(self.binParticles(particles, args.bin_factor, correctOrigin, correctApix, args.suf_orig, args.suf_new))

        mdOut.addData(new_particles)
        mdOut.write(args.o)

        print "New star file "+args.o+" created. Have fun!"


if __name__ == "__main__":

    BinCorrectStar().main()
