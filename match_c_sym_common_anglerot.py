#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
from argparse import RawTextHelpFormatter


class MatchRotAngles:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Find the closest common rotation angles of particles of two reconstructions made under different symmetry. Useful, to match symmetry mismatched parts to be matched in C1.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i1', help="Input1 STAR filename with particles.")
        add('--i2', help="Input2 STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--sym1', type=str, default="C5",
            help="Symmetry applied on --i1")
        add('--sym2', type=str, default="C12",
            help="Symmetry applied on --i2")


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

        if not os.path.exists(args.i1):
            self.error("Input1 file '%s' not found." % args.i1)

        if not os.path.exists(args.i2):
            self.error("Input2 file '%s' not found." % args.i2)

    def get_particles(self, md, dataTableName):
        particles = []
        for particle in getattr(md, dataTableName):
            particles.append(particle)
        return particles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print(f"Matching the closest rlnAngleRot between symmetries {args.sym1} and {args.sym2} from the two star files.")

        md1 = MetaData(args.i1)
        md2 = MetaData(args.i2)

        sym1 = int(args.sym1.strip("cC"))
        sym2 = int(args.sym2.strip("cC"))

        # generate list of symmetry shifts
        sym1inc = 360.0 / sym1
        sym2inc = 360.0 / sym2
        sym1list = [i * sym1inc for i in range(sym1)]
        sym2list = [i * sym2inc for i in range(sym2)]

        sym1particles = self.get_particles(md1,"data_particles")
        sym2particles = self.get_particles(md2, "data_particles")

        if len(sym1particles) != len(sym2particles):
            self.error("Number of particles in the two star files do not match. %d != %d" % (len(sym1particles), len(sym2particles)))

        for index, sym1particle in enumerate(sym1particles):
            sym1rot = sym1particle.rlnAngleRot % sym1inc
            sym2rot = sym2particles[index].rlnAngleRot % sym2inc

            sym1Vals = [b + sym1rot for b in sym1list]
            sym2Vals = [b + sym2rot for b in sym2list]

            # choose the sym1Val whose closest distance to any sym2Val is minimal
            best = min(sym1Vals, key=lambda v: min(abs(v - x) for x in sym2Vals))

            #write as normalized angle between -180 and 180
            sym1particle.rlnAngleRot = ((best + 180.0) % 360.0) - 180.0


        md1.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    MatchRotAngles().main()
