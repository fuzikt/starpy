#!/usr/bin/env python

import os
import sys
import copy
import operator
from math import *
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter
from collections import OrderedDict


class SelValueStar():
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Filter lines from star file upon comaprison with given value. \n Example1: Select lines from input.star where source micrograph does not eqauls to mic123456789.mrc\n select_values_star.py --i input.star --o output.star --lb rlnMicrographName --op \"!=\" --val mic123456789.mrc \n\n Example2: Select lines from input.star where tilt angles are less than 15 deg. t\n select_values_star.py --i input.star --o output.star --lb rlnAngleTilt --op \"<\" --val 15", formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--lb', type=str, default="rlnMicrographName",
              help="Label used for selection. e.g. rlnAngleTilt, rlnDefocusU...")
        add('--op', type=str, default="=",
              help="Operator used for comparison. Allowed: \"=\", \"!=\", \">=\", \"<=\", \"<\"")
        add('--val', type=str, default="-0",
              help="Value used for comparison. Used together with --op parameter.")
        add('--rh', type=str, default="-0",
              help="Range Hi (upper bound). If defined --op and -val disabled.")
        add('--rl', type=str, default="-0",
              help="Range Lo (lower bound). If defined --op and -val disabled.")

    def usage(self):
        self.parser.print_help()


    def error(self, *msgs):
        self.usage()
        print "Error: " + '\n'.join(msgs)
        print " "
        sys.exit(2)


    def validate(self, args):
        if len(sys.argv) == 1:
            self.error("No input file given.")

        if not os.path.exists(args.i):
            self.error("Input file '%s' not found."
                       % args.i)

        if (args.lb not in LABELS):
            self.error("Label "+args.lb+" not recognized as RELION label.")

        if (args.rh == "-0") and (args.rl == "-0"):
            if args.op not in ["=", "!=", ">=", "<=", "<"]:
                self.error("Operator '%s' not allowed. Allowed operators are: \"=\", \"!=\", \">=\", \"<=\", \"<\"" % args.op)
            if args.val == "-0":
                self.error("No value provided for comparison. Please, provide a value.")

        range = False

        if LABELS[args.lb] == float:
            try:
                if (args.rh == "-0") and (args.rl == "-0"):
                    compValue = float(args.val)
                    rangeHi = 0
                    rangeLo = 0
                else:
                    rangeHi =  float(args.rh)
                    rangeLo =  float(args.rl)
                    compValue = 0
                    range = True
            except ValueError:
                self.error("Label '%s' requires FLOAT value for comparison." % args.lb) 

        if LABELS[args.lb] == int:
            try:
                if (args.rh == "-0") and (args.rl == "-0"):
                    compValue = int(args.val)
                    rangeHi = 0
                    rangeLo = 0
       	       	else:
       	       	    rangeHi =  int(args.rh)
       	       	    rangeLo =  int(args.rl)
                    compValue = 0
                    range = True
            except ValueError:
                self.error("Label '%s' requires INT value for comparison." % args.lb) 

        if LABELS[args.lb] == str:
            try:
                if (args.rh == "-0") and (args.rl == "-0"):
                    compValue = str(args.val)
       	       	else:
               	    self.error("Cannot do range comaprison for label '%s'. It requires STR value for comparison." % args.lb)
            except ValueError:
                self.error("Attribute '%s' requires STR value for comparison." % args.lb) 
        return compValue, rangeHi, rangeLo, range



    def get_particles(self, md):
        particles = []
        for particle in md:
                particles.append(particle)
        return particles

    def selParticles(self, particles, atr, op_char, value, rangeHi, rangeLo, range):
        ops = {"=": operator.eq,
               "!=": operator.ne,
               ">": operator.gt,
               ">=": operator.ge,
               "<": operator.lt,
               "<=": operator.le}

        op_func = ops[op_char]
        
        newParticles = []

        while len(particles)>0:
            selectedParticle=particles.pop(0)
            if range != True:
                if (op_func(getattr(selectedParticle,atr), value)):
                    newParticles.append(selectedParticle)
            else:
                if ((getattr(selectedParticle,atr) >= rangeLo) and (getattr(selectedParticle,atr) <= rangeHi)):
                    newParticles.append(selectedParticle)
        print(str(len(newParticles))+" particles included in selection.")

        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        compValue, rangeHi, rangeLo, range = self.validate(args)

        if range:
            print("Selecting particles particles where %s is in range <%s, %s>." % (args.lb, rangeLo, rangeHi))
        else:
            print("Selecting particles particles where %s is %s %s." % (args.lb, args.op, compValue))

        md = MetaData(args.i)
        mdOut = MetaData()
        mdOut.addLabels(md.getLabels())

        new_particles = []

        particles=self.get_particles(md)

        new_particles.extend(self.selParticles(particles, args.lb, args.op, compValue, rangeHi, rangeLo, range))
        mdOut.addData(new_particles)
        mdOut.write(args.o)

        print "New star file "+args.o+" created. Have fun!"


if __name__ == "__main__":

    SelValueStar().main()
