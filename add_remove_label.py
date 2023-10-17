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
        add('--i', help="Input STAR filename.")
        add('--o', help="Output STAR filename.")
        add('--add', action='store_true',
            help="Adds new label to the star file.")
        add('--rm', action='store_true',
            help="Remove label from the star file.")
        add('--lb', type=str, default="",
            help="Label to be added or removed Default: None")
        add('--val', type=str, default="0",
            help="Value filled for added label. Default: 0")
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
            self.error("Input file '%s' not found." % args.i)

        if args.add and args.rm:
            self.error("Use only one of the --add or --remove")

        if args.lb == "":
            self.error("Please specify the label (--lb) to be added or removed.")

        if args.lb not in LABELS:
            self.error("Label %s not recognized as RELION label." % args.lb)

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print("Selecting particles from star file...")

        md = MetaData(args.i)

        if args.add:
            dataTable = args.data
            dic = {args.lb: args.val}
            md.setLabels(dataTable, **dic)

        if args.rm:
            md.removeLabels(args.data, args.lb)

        md.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    AddRemoveLabel().main()
