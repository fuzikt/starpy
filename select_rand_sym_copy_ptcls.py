#!/usr/bin/env python3

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
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")

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

    def randParticles(self, particles):
        # Group particles by image name in a dictionary
        particle_groups = {}
        for particle in particles:
            img_name = particle.rlnImageName
            if img_name not in particle_groups:
                particle_groups[img_name] = []
            particle_groups[img_name].append(particle)

        # Get symmetry fold from first group
        first_group = next(iter(particle_groups.values()))
        sym_fold = len(first_group)
        print(f"Detected {sym_fold}-fold symmetry.")

        newParticles = [
            random.choice(group)
            for group in particle_groups.values()
        ]

        self.mprint(f"Selected {len(newParticles)} random particles from their symmetry copies.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)

        new_particles = []

        self.mprint("Reading in input star file.....")

        particles = self.get_particles(md)

        self.mprint(
            "Total %s particles in input star file. \nSelecting random particles from their symmetry copies." % str(
                len(particles)))

        new_particles.extend(self.randParticles(particles))

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
    RandSymStar().main()
