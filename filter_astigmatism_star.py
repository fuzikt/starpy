#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class SelAstgStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Limit astigmatism of particles or micrographs in star file.")
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--astg', type=float, default=1000,
            help="Max astigmatism in Angstroms. (Default: 1000)")
        add('--res', type=float, default=0,
            help="Minimum resolution in Angstroms. (Default: 0 (off)")
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
        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Input file '%s' not found." % args.i)

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)

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
        self.mprint(str(len(newParticles))+" particles included in selection.")
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)
        
        self.mprint("Selecting particles/micrographs from star file...")

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
            self.mprint("No label rlnFinalResolution found in input file. Switching off resolution filtering...")
            args.res = 0

        new_particles = []

        particles = self.get_particles(md, dataTableName)

        new_particles.extend(self.selParticles(particles, args.astg, args.res,))

        if md.version == "3.1":
            mdOut = md.clone()
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

    SelAstgStar().main()
