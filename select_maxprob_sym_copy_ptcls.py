#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
import time


class selMaxProbSymStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Select one orientation per particle from symmetry expanded star files according to the greatest value of rlnMaxValueProbDistribution.")
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--lb', type=str, default="rlnImageName",
            help="Label used for comparison considering that the record is a sym copy. (default: rlnImageName)")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Input file '%s' not found."
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

    def maxProbParticle(self, symCopies):
        maxLikeParticle = symCopies[0]
        for particle in symCopies:
            if particle.rlnMaxValueProbDistribution > maxLikeParticle.rlnMaxValueProbDistribution:
                maxLikeParticle = particle
        return maxLikeParticle

    def selMostProbableParticles(self, particles, symCopyLabel):
        # Group particles by their symCopyLabel
        particleGroups = {}

        for particle in particles:
            key = getattr(particle, symCopyLabel)
            if key not in particleGroups:
                particleGroups[key] = []
            particleGroups[key].append(particle)

        # Find max probability particle for each group
        newParticles = []
        for group in particleGroups.values():
            maxParticle = max(group, key=lambda p: p.rlnMaxValueProbDistribution)
            newParticles.append(maxParticle)

        self.mprint(f"Selected {len(newParticles)} particles from the original star file.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)
        start_total = time.time()

        md = MetaData(args.i)

        new_particles = []

        self.mprint("Reading in input star file.....")

        particles = self.get_particles(md)

        self.mprint(
            "Total %s particles in input star file. \nSelecting one orientation per particle according to the greatest value of rlnMaxValueProbDistribution." % str(
                len(particles)))

        new_particles.extend(self.selMostProbableParticles(particles, args.lb))

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
        self.mprint(f"Total execution time: {time.time() - start_total:.2f} seconds")
        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    selMaxProbSymStar().main()
