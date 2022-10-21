#!/usr/bin/env python

import os
import sys
from copy import deepcopy
from metadata import MetaData
import argparse


class SelAstgStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Limit astigmatism of particles or micrographs in star file.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--astg', type=float, default=1000,
            help="Max astigmatism in Angstroms. Default: 1000")
        add('--res', type=float, default=0,
            help="Minimum resolution in Angstroms. Default: 0 (off)")
        add('--data', type=str, default="data_particles",
            help="Data table from star file to be used (Default: data_particles).")

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

    def get_particles(self, md, dataTableName):
        particles = []
        for particle in getattr(md, dataTableName):
            particles.append(particle)
        return particles

    def selParticles(self, particles, astg, res):
        newParticles = []
        while len(particles) > 0:
            selectedParticle = particles.pop(0)
            if res == 0:
                if abs(selectedParticle.rlnDefocusU-selectedParticle.rlnDefocusV) <= astg:
                    newParticles.append(selectedParticle)
            else:
                if (abs(selectedParticle.rlnDefocusU-selectedParticle.rlnDefocusV) <= astg) and (selectedParticle.rlnFinalResolution <= res):
                    newParticles.append(selectedParticle)
        print(str(len(newParticles))+" particles included in selection.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)
        
        print("Selecting particles/micrographs from star file...")

        md = MetaData(args.i)

        dataTableName = args.data

        if md.version == "3.1":
            ilabels = md.getLabels(dataTableName)
        else:
            ilabels = md.getLabels("data_")
            dataTableName = "data_"

        if ("rlnDefocusU" not in ilabels) or ("rlnDefocusV" not in ilabels):
            self.error("No labels rlnDefocusU or rlnDefocusV found in Input file.")
        if ("rlnFinalResolution" not in ilabels) and (args.res > 0):
            print("No label rlnFinalResolution found in input file. Switching off resolution filtering...")
            args.res = 0

        new_particles = []

        particles = self.get_particles(md, dataTableName)

        new_particles.extend(self.selParticles(particles, args.astg, args.res,))

        if md.version == "3.1":
            mdOut = deepcopy(md)
            mdOut.removeDataTable(dataTableName)
        else:
            mdOut = MetaData()
            dataTableName = "data_"

        mdOut.addDataTable(dataTableName)
        mdOut.addLabels(dataTableName, md.getLabels(dataTableName))
        mdOut.addData(dataTableName, new_particles)
        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":

    SelAstgStar().main()
