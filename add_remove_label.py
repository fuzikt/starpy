#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter


class AddRemoveLabel:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Adds or removes labels from star file.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--add', action='store_true',
            help="Add new label to the star file.")
        add('--rm', action='store_true',
            help="Remove label from the star file.")
        add('--lb', type=str, default="",
            help="Label to be added or removed. Use comma separated label values to add or remove multiple labels. Default: None")
        add('--val', type=str, default="0",
            help="Value filled for added labels. Use comma separated values if adding multiple labels. To copy values from existing label into the new one use the label name as value (e.g. rlnCoordinateX). Default: 0")
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

        if args.add and args.rm:
            self.error("Use only one of the --add or --rm")

        if args.lb == "":
            self.error("Please specify the label (--lb) to be added or removed.")

        if (len(args.lb.split(",")) != len(args.val.split(","))) and args.add:
            self.error("Same number of values (--val) has to be specified as the number of newly added labels (--lb).")

        for lb in args.lb.split(","):
            if lb not in LABELS:
                self.error("Label %s not recognized as RELION label." % args.lb)

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        self.mprint("Selecting particles from star file...")

        md = MetaData(args.i)

        if args.add:
            dataTable = args.data

            lbs = args.lb.split(",")
            vals = args.val.split(",")

            # check for the first particle if any of the new labels already exist
            particle = getattr(md,dataTable)[0]
            for lb in lbs:
                if hasattr(particle, lb):
                    self.error(
                        f"Label {lb} already exists in the star file. Please choose another label name or use --rm to remove it first.")

            for particle in getattr(md,dataTable):
                for lb, val in zip(lbs, vals):
                    if val.startswith("rln"):
                        if hasattr(particle, val):
                            setattr(particle, lb, getattr(particle, val))
                        else:
                            self.mprint(
                                f"Warning: Label {val} not found in particle. Skipping copying its value to {lb}.")
                    else:
                        setattr(particle, lb, LABELS[lb](val))

            md.addLabels(dataTable, *lbs)


        if args.rm:
            md.removeLabels(args.data, args.lb.split(","))

        md.write(args.o)

        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    AddRemoveLabel().main()
