#!/usr/bin/env python

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter


class AssignLabelStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Add label (col_lb) to Input1 and assigns values to it from Input2 where the label (comp_lb) of Input2 matches Input1",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i1', help="Input1 STAR filename.")
        add('--i2', help="Input2 STAR filename.")
        add('--o', help="Output STAR filename.")
        add('--col_lb', type=str, default="rlnDefocusU",
            help="Label of the new column assigned to Input1; Default: rlnDefocusU")
        add('--comp_lb', type=str, default="rlnMicrographName",
            help="Compare label used for Input1 and Input2 for value assignment. Default:rlnMicrographName")

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
            self.error("Input1 file '%s' not found." % args.i)

        if args.col_lb not in LABELS:
            self.error("Label %s not recognized as RELION label." % args.lb)
        if args.comp_lb not in LABELS:
            self.error("Label %s not recognized as RELION label." % args.lb)

        if not os.path.exists(args.i2):
            self.error("Input2 file '%s' not found." % args.i)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def assign_column(self, particles1, particles2, col_lb, comp_lb):
        outParticles = []

        for particle in particles1:
            for comp_particle in particles2:
                if getattr(particle, comp_lb) == getattr(comp_particle, comp_lb):
                    setattr(particle, col_lb, getattr(comp_particle, col_lb))
                    break
            outParticles.append(particle)
        return outParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print("Selecting particles from star file...")

        md1 = MetaData(args.i1)
        md2 = MetaData(args.i2)

        if md1.version == "3.1":
            i1labels = md1.getLabels("data_particles")
            i2labels = md2.getLabels("data_particles")
        else:
            i1labels = md1.getLabels("data_")
            i2labels = md2.getLabels("data_")

        if args.col_lb in i1labels:
            self.error("Column %s is already in Input1 star file. Please remove it first..." % args.col_lb)
        if args.col_lb not in i2labels:
            self.error("Column %s is not present in Input2 star file." % args.col_lb)
        if args.comp_lb not in i1labels:
            self.error("Column %s is not present in Input1 star file." % args.comp_lb)
        if args.comp_lb not in i2labels:
            self.error("Column %s is not present in Input2 star file." % args.comp_lb)

        if LABELS[args.col_lb] == float:
            # add label with default values 0.0
            print("Adding label %s to Input1 data with default value 0.0." % args.col_lb)
            dic = {args.col_lb: 0.0}
        if LABELS[args.col_lb] == int:
            # add label with default values 0
            print("Adding label %s to Input1 data with default value 0." % args.col_lb)
            dic = {args.col_lb: 0}
        if LABELS[args.col_lb] == str:
            # add label with default values "dummy"
            print("Adding label %s to Input1 data with default value \"dummy\"" % args.col_lb)
            dic = {args.col_lb: "dummy"}

        if md1.version == "3.1":
            md1.setLabels("data_particles", **dic)
        else:
            md1.setLabels("data_", **dic)

        particles1 = self.get_particles(md1)
        particles2 = self.get_particles(md2)

        print(
            "Assigning values for Input1 label %s where the %s of Input2 matches Input1" % (args.col_lb, args.comp_lb))

        mdOut = MetaData()

        if md1.version == "3.1":
            mdOut.version = "3.1"
            mdOut.addDataTable("data_optics")
            mdOut.addLabels("data_optics", md1.getLabels("data_optics"))
            mdOut.addData("data_optics", getattr(md1, "data_optics"))
            particleTableName = "data_particles"
        else:
            particleTableName = "data_"

        mdOut.addDataTable(particleTableName)
        mdOut.addLabels(particleTableName, md1.getLabels(particleTableName))
        mdOut.addData(particleTableName, self.assign_column(particles1, particles2, args.col_lb, args.comp_lb))

        print("%s particles were processed..." % str((len(particles1) + len(particles2))))

        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    AssignLabelStar().main()
