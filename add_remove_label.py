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
            help="Value filled for added labels. Use comma separated values if adding multiple labels. Default: 0")
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
            dic = dict(map(lambda i, j: (i, j), lbs, vals))
            md.setLabels(dataTable, **dic)

        if args.rm:
            md.removeLabels(args.data, args.lb.split(","))

        md.write(args.o)

        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    AddRemoveLabel().main()
