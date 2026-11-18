#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter


class FindReplaceStringInLabel:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Find and replace string (parts) in a label in a STAR file.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--lb', type=str, default="",
            help="Label to be which string values (substring) should be modified. Default: None")
        add('--f_str', type=str, default="",
            help="Find this substring value for replacement (e.g. mrc). Default: None")
        add('--r_str', type=str, default="",
            help="Replace by this string value (e.g. star). Default: None")
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

        if args.lb == "":
            self.error("Please specify the label (--lb) no which the find/replace should be performed.")

        for lb in args.lb.split(","):
            if lb not in LABELS:
                self.error("Label %s not recognized as RELION label." % args.lb)

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)

    def findReplaceStrValues(self, particles, label, find_str, replace_str):
        for particle in particles:
            if not hasattr(particle, label):
                print(f"Warning: Label {label} not found in particle. Skipping find/replace operation.")
                return

            current_value = getattr(particle, label)
            current_value = str.replace(current_value, find_str, replace_str)
            setattr(particle, label, current_value)


    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        self.mprint("Replacing values in star file...")

        md = MetaData(args.i)
        dataTable = args.data
        particles = getattr(md, dataTable)

        self.findReplaceStrValues(particles, args.lb, args.f_str, args.r_str)

        md.write(args.o)

        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    FindReplaceStringInLabel().main()
