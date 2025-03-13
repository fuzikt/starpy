#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter
import time

class AssignLabelStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Add label (col_lb) to Input1 and assigns values to it from Input2 where the label (comp_lb) of Input2 matches Input1",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i1', help="Input1 STAR filename.")
        add('--i2', help="Input2 STAR filename.")
        add('--o', help="Output STAR filename.")
        add('--data', type=str, default="data_particles",
            help="Data table from star file to be used (Default: data_particles).")
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

    def get_particles(self, md, dataTableName):
        particles = []
        for particle in getattr(md, dataTableName):
            particles.append(particle)
        return particles

    def assign_column(self, particles1, particles2, col_lb, comp_lb):
        lookup = {
            getattr(p, comp_lb): getattr(p, col_lb)
            for p in particles2
        }

        for particle in particles1:
            key = getattr(particle, comp_lb)
            if key in lookup:
                setattr(particle, col_lb, lookup[key])

        return particles1

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)
        start_total = time.time()

        print("Reading particles from star file...")

        md1 = MetaData(args.i1)
        md2 = MetaData(args.i2)

        dataTableName = args.data

        if md1.version == "3.1":
            i1labels = md1.getLabels(dataTableName)
            i2labels = md2.getLabels(dataTableName)
        else:
            i1labels = md1.getLabels("data_")
            i2labels = md2.getLabels("data_")
            dataTableName = "data_"

        if args.col_lb not in i2labels:
            self.error("Column %s is not present in Input2 star file." % args.col_lb)
        if args.comp_lb not in i1labels:
            self.error("Column %s is not present in Input1 star file." % args.comp_lb)
        if args.comp_lb not in i2labels:
            self.error("Column %s is not present in Input2 star file." % args.comp_lb)

        particles1 = self.get_particles(md1, dataTableName)
        particles2 = self.get_particles(md2, dataTableName)

        print(
            "Assigning values for Input1 label %s where the %s of Input2 matches Input1" % (args.col_lb, args.comp_lb))

        if md1.version == "3.1":
            mdOut = md1.clone()
            mdOut.removeDataTable(dataTableName)
        else:
            mdOut = MetaData()
            dataTableName = "data_"

        mdOut.addDataTable(dataTableName, md1.isLoop(dataTableName))
        mdOut.addLabels(dataTableName, i1labels)
        if args.col_lb not in i1labels:
            mdOut.addLabels(dataTableName, args.col_lb)

        mdOut.addData(dataTableName, self.assign_column(particles1, particles2, args.col_lb, args.comp_lb))

        print("%s particles were processed..." % str((len(particles1))))

        mdOut.write(args.o)
        print(f"Total execution time: {time.time() - start_total:.2f} seconds")
        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    AssignLabelStar().main()
