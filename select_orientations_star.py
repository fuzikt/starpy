#!/usr/bin/env python

import os
import sys
import copy
from math import *
from metadata import MetaData
import argparse
from collections import OrderedDict


class SelOrientStar():
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Limit orientations of particles in star file. Select particles depending on their rlnTilt, rlnRot, rlnPsi.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--rot_min', type=float, default=-180,
              help="Minimum rot angle.")
        add('--rot_max', type=float, default=180,
              help="Minimum rot angle.")
        add('--tilt_min', type=float, default=0,
              help="Minimum tilt angle.")
        add('--tilt_max', type=float, default=180,
              help="Minimum tilt angle.")
        add('--psi_min', type=float, default=-180,
              help="Minimum psi angle.")
        add('--psi_max', type=float, default=180,
              help="Minimum psi angle.")


    def usage(self):
        self.parser.print_help()


    def error(self, *msgs):
        self.usage()
        print "Error: " + '\n'.join(msgs)
        print " "
        sys.exit(2)


    def validate(self, args):
        if len(sys.argv) == 1:
            self.error("Error: No input file given.")

        if not os.path.exists(args.i):
            self.error("Error: Input file '%s' not found."
                       % args.i)

    def get_particles(self, md):
        particles = []
        for particle in md:
                particles.append(particle)
        return particles

    def selParticles(self, particles, rotMin, rotMax, tiltMin, tiltMax, psiMin, psiMax):
        newParticles = []
        while len(particles)>0:
            selectedParticle=particles.pop(0)
            if (selectedParticle.rlnAngleRot>=rotMin and selectedParticle.rlnAngleRot<=rotMax) and (selectedParticle.rlnAngleTilt>=tiltMin and selectedParticle.rlnAngleTilt<=tiltMax) and (selectedParticle.rlnAnglePsi>=psiMin and selectedParticle.rlnAnglePsi<=psiMax):
                newParticles.append(selectedParticle)
        print(str(len(newParticles))+" particles included in selection.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print "Selecting particles from star file..."

        md = MetaData(args.i)
        mdOut = MetaData()
        mdOut.addLabels(md.getLabels())

        new_particles = []

        particles=self.get_particles(md)

        new_particles.extend(self.selParticles(particles, args.rot_min, args.rot_max, args.tilt_min, args.tilt_max, args.psi_min, args.psi_max))
        mdOut.addData(new_particles)
        mdOut.write(args.o)

        print "New star file "+args.o+" created. Have fun!"


if __name__ == "__main__":

    SelOrientStar().main()
