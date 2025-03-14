#!/usr/bin/env python3
import math
import os
import sys
import operator
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter
import time


class SelValueStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Filter lines from star file upon comparison with given value. \n Example1: Select lines from input.star where source micrograph does not equals to mic123456789.mrc\n select_values_star.py --i input.star --o output.star --lb rlnMicrographName --op \"!=\" --val mic123456789.mrc \n\n Example2: Select lines from input.star where tilt angles are less than 15 deg.\n select_values_star.py --i input.star --o output.star --lb rlnAngleTilt --op \"<\" --val 15",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--data', type=str, default="data_particles",
            help="Data table from star file to be used (Default: data_particles).")
        add('--lb', type=str, default="rlnMicrographName",
            help="Label used for selection. e.g. rlnAngleTilt, rlnDefocusU...")
        add('--op', type=str, default="=",
            help="Operator used for comparison. Allowed: \"=\", \"!=\", \">=\", \"<=\", \"<\", \">\". Use double quotes!!!")
        add('--val', type=str, default="-0",
            help="Value used for comparison. Used together with --op parameter.")
        add('--rh', type=str, default="-0",
            help="Range Hi (upper bound). If defined --op and -val disabled.")
        add('--rl', type=str, default="-0",
            help="Range Lo (lower bound). If defined --op and -val disabled.")
        add('--prctl_h', type=str, default="-1",
            help="Select particles above defined percentile of values (e.g. 25, 50, 75). Used together with --lb parameter.")
        add('--prctl_l', type=str, default="-1",
            help="Select particles below defined percentile of values (e.g. 25, 50, 75). Used together with --lb parameter.")

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

        if args.lb not in LABELS:
            self.error("Label " + args.lb + " not recognized as RELION label.")

        if (args.rh == "-0") and (args.rl == "-0"):
            if args.op not in ["=", "!=", ">=", "<=", "<", ">"]:
                self.error(
                    "Operator '%s' not allowed. Allowed operators are: \"=\", \"!=\", \">=\", \"<=\", \"<\", \">\"" % args.op)
            if args.val == "-0" and args.prctl_l == "-1" and args.prctl_h == "-1":
                self.error("No value provided for comparison. Please, provide a value.")

        rangeSel = False

        if LABELS[args.lb] == float:
            try:
                if (args.rh == "-0") and (args.rl == "-0"):
                    compValue = float(args.val)
                    rangeHi = 0
                    rangeLo = 0
                else:
                    rangeHi = float(args.rh)
                    rangeLo = float(args.rl)
                    compValue = 0
                    rangeSel = True
            except ValueError:
                self.error("Label '%s' requires FLOAT value for comparison." % args.lb)

        if LABELS[args.lb] == int:
            try:
                if (args.rh == "-0") and (args.rl == "-0"):
                    compValue = int(args.val)
                    rangeHi = 0
                    rangeLo = 0
                else:
                    rangeHi = int(args.rh)
                    rangeLo = int(args.rl)
                    compValue = 0
                    rangeSel = True
            except ValueError:
                self.error("Label '%s' requires INT value for comparison." % args.lb)

        if LABELS[args.lb] == str:
            try:
                if (args.rh == "-0") and (args.rl == "-0"):
                    compValue = str(args.val)
                else:
                    self.error(
                        "Cannot do range comparison for label '%s'. It requires STR value for comparison." % args.lb)
            except ValueError:
                self.error("Attribute '%s' requires STR value for comparison." % args.lb)

        try:
            prctl_l = int(args.prctl_l)
            prctl_h = int(args.prctl_h)

            if (prctl_l > -1 or prctl_h > -1) and LABELS[args.lb] == str:
                self.error("Cannot do percentile selection on STR value label %s." % args.lb)
            if prctl_l > -1 and prctl_h > -1:
                self.error("--prctl_h and --prtcl_l cannot be used simultaneously. Use only one of them")

        except ValueError:
            self.error("Percentile requires integer value to be used")

        return compValue, rangeHi, rangeLo, rangeSel, prctl_l, prctl_h

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

    def percentile(self, N, percent, key=lambda x: x):
        """
        Find the percentile of a list of values.

        @parameter N - is a list of values. Note N MUST BE already sorted.
        @parameter percent - a float value from 0.0 to 1.0.
        @parameter key - optional key function to compute value from each element of N.

        @return - the percentile of the values
        """
        if not N:
            return None
        k = (len(N) - 1) * percent
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return key(N[int(k)])
        d0 = key(N[int(f)]) * (c - k)
        d1 = key(N[int(c)]) * (k - f)

        return d0 + d1

    def selParticles(self, particles, atr, op_char, value, rangeHi, rangeLo, rangeSel, prctl_l, prctl_h):
        ops = {
            "=": operator.eq,
            "!=": operator.ne,
            ">": operator.gt,
            ">=": operator.ge,
            "<": operator.lt,
            "<=": operator.le
        }

        # Process percentiles first if needed
        if prctl_h > -1 or prctl_l > -1:
            allValues = sorted(getattr(p, atr) for p in particles)
            prctl = max(prctl_l, prctl_h)
            value = self.percentile(allValues, prctl / 100.0)

            if prctl_l > -1:
                op_func = ops["<="]
                self.mprint(f"Selecting below {prctl}-th percentile of data. {atr} values less or equal {value}.")
            else:
                op_func = ops[">="]
                self.mprint(f"Selecting above {prctl}-th percentile of data. {atr} values more or equal {value}.")
        else:
            op_func = ops[op_char]

        if rangeSel:
            newParticles = [
                p for p in particles
                if rangeLo <= getattr(p, atr) <= rangeHi
            ]
        else:
            newParticles = [
                p for p in particles
                if op_func(getattr(p, atr), value)
            ]

        self.mprint(f"{len(newParticles)} particles included in selection.")
        return newParticles


    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        compValue, rangeHi, rangeLo, rangeSel, prctl_l, prctl_h = self.validate(args)

        if rangeSel:
            self.mprint("Selecting particles where %s is in range <%s, %s>." % (args.lb, rangeLo, rangeHi))
        elif args.prctl_l == "-1" and args.prctl_h == "-1":
            self.mprint("Selecting particles where %s is %s %s." % (args.lb, args.op, compValue))
        start_total = time.time()
        md = MetaData(args.i)

        dataTableName = args.data

        new_particles = []

        particles = self.get_particles(md, dataTableName)

        new_particles.extend(
            self.selParticles(particles, args.lb, args.op, compValue, rangeHi, rangeLo, rangeSel, prctl_l, prctl_h))

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
        self.mprint(f"Total execution time: {time.time() - start_total:.2f} seconds")
        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    SelValueStar().main()
