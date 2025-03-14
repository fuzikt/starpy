#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class SelOrientStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Limit orientations of particles in star file. Select particles that are in the defined range of rlnTilt, rlnRot, rlnPsi.")
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--rot_min', type=float, default=-180, help="Minimum rot angle")
        add('--rot_max', type=float, default=180, help="Maximum rot angle")
        add('--tilt_min', type=float, default=0, help="Minimum tilt angle")
        add('--tilt_max', type=float, default=180, help="Maximum tilt angle")
        add('--psi_min', type=float, default=-180, help="Minimum psi angle")
        add('--psi_max', type=float, default=180, help="Maximum psi angle")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Error: Input file '%s' not found."
                       % args.i)

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def selParticles(self, particles, rotMin, rotMax, tiltMin, tiltMax, psiMin, psiMax):
        newParticles = []
        while len(particles) > 0:
            selectedParticle = particles.pop(0)
            if (selectedParticle.rlnAngleRot >= rotMin and selectedParticle.rlnAngleRot <= rotMax) and (
                    selectedParticle.rlnAngleTilt >= tiltMin and selectedParticle.rlnAngleTilt <= tiltMax) and (
                    selectedParticle.rlnAnglePsi >= psiMin and selectedParticle.rlnAnglePsi <= psiMax):
                newParticles.append(selectedParticle)
        self.mprint(str(len(newParticles)) + " particles included in selection.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        self.mprint("Selecting particles from star file...")

        md = MetaData(args.i)

        new_particles = []

        particles = self.get_particles(md)

        new_particles.extend(
            self.selParticles(particles, args.rot_min, args.rot_max, args.tilt_min, args.tilt_max, args.psi_min,
                              args.psi_max))

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

        mdOut.write(args.o)

        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    SelOrientStar().main()
