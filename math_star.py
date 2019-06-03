#!/usr/bin/env python

import os
import sys
import operator
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter


class MathStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Perform basic math operations on star file values. \n Example1: Add 15 deg to rlnAngleTilt. \n math_star.py --i input.star --o output.star --lb rlnAngleTilt --op \"+\" --val 15 \n\n Example2: Multiply rlnOriginX by 2\n math_star.py --i input.star --o output.star --lb rlnOriginX --op \"*\" --val 2\n\n Example3: Compute remainder of rlnAngleRot where rlnGroupNumber is 2.\n math_star.py --i input.star --o output.star --lb rlnAnlgeRot --op \"remainder\" --sellb rlnGroupNumber --selval 2",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--lb', type=str, default="rlnMicrographName",
            help="Label used for math operation. e.g. rlnAngleTilt, rlnDefocusU...")
        add('--op', type=str, default="=",
            help="Operator used for comparison. Allowed: \"+\", \"-\", \"*\", \"/\",\"^\",\"abs\",\"=\",\"mod\",\"remainder\"")
        add('--val', type=str, default="0",
            help="Value used for math operation.")
        add('--sellb', type=str, default="None",
            help="Label used for selection. e.g. rlnAngleTilt, rlnDefocusU... Default: None")
        add('--selop', type=str, default="=",
            help="Operator used for comparison. Allowed: \"=\", \"!=\", \">=\", \"<=\", \"<\"")
        add('--selval', type=str, default="-0",
            help="Value used for comparison. Used together with --selop parameter.")
        add('--rh', type=str, default="-0",
            help="Selection range Hi (upper bound). Default: Disabled")
        add('--rl', type=str, default="-0",
            help="Selection range Lo (lower bound). Default: Disabled")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        rangeSel = False

        if len(sys.argv) == 1:
            self.error("No input file given.")

        if not os.path.exists(args.i):
            self.error("Input file '%s' not found."
                       % args.i)

        if args.lb not in LABELS:
            self.error("Label " + args.lb + " not recognized as RELION label.")

        if LABELS[args.lb] == float:
            try:
                compValue = float(args.val)
            except ValueError:
                self.error("Attribute '%s' requires FLOAT value for operation." % args.lb)

        if LABELS[args.lb] == int:
            try:
                compValue = int(args.val)
            except ValueError:
                self.error("Attribute '%s' requires INT value for operation." % args.lb)

        if LABELS[args.lb] == str:
            self.error("Attribute '%s' has STR value. Cannot perform math operation on STR values." % args.lb)

        if args.sellb == "None":
            selValue = 0
            rangeHi = 0
            rangeLo = 0

        if (args.rh == "-0") and (args.rl == "-0") and (args.sellb !="None"):
            if args.selop not in ["=", "!=", ">=", "<=", "<"]:
                self.error(
                    "Selection operator '%s' not allowed. Allowed operators are: \"=\", \"!=\", \">=\", \"<=\", \"<\"" % args.op)
            if args.selval == "-0":
                self.error("No value provided for selection. Please, provide a value.")

        if args.sellb != "None":
            if LABELS[args.sellb] == float:
                try:
                    if (args.rh == "-0") and (args.rl == "-0"):
                        selValue = float(args.selval)
                    else:
                        rangeHi = float(args.rh)
                        rangeLo = float(args.rl)
                        selValue = 0
                        rangeSel = True
                except ValueError:
                    self.error("Label '%s' requires FLOAT value for comparison." % args.sellb)

            if LABELS[args.sellb] == int:
                try:
                    if (args.rh == "-0") and (args.rl == "-0"):
                        rangeHi = 0
                        rangeLo = 0
                        selValue = int(args.selval)
                    else:
                        rangeHi = int(args.rh)
                        rangeLo = int(args.rl)
                        selValue = 0
                        rangeSel = True
                except ValueError:
                    self.error("Label '%s' requires INT value for comparison." % args.sellb)

            if LABELS[args.sellb] == str:
                try:
                    if (args.rh == "-0") and (args.rl == "-0"):
                        rangeHi = 0
                        rangeLo = 0
                        selValue = str(args.selval)
                    else:
                        self.error(
                            "Cannot do range comparison for label '%s'. It requires STR value for comparison." % args.lb)
                except ValueError:
                    self.error("Attribute '%s' requires STR value for comparison." % args.sellb)
        return compValue, selValue, rangeHi, rangeLo, rangeSel

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def mathParticles(self, particles, atr, op_char, value, sel_op_char, sel_atr, sel_value, rangeHi, rangeLo,
                      rangeSel):
        ops = {"+": operator.add,
               "-": operator.sub,
               "*": operator.mul,
               "/": operator.div,
               "^": operator.pow,
               "abs": operator.abs,
               "mod": operator.mod}

        sel_ops = {"=": operator.eq,
                   "!=": operator.ne,
                   ">": operator.gt,
                   ">=": operator.ge,
                   "<": operator.lt,
                   "<=": operator.le}

        if (op_char != "=") and (op_char != "remainder"): op_func = ops[op_char]

        sel_op_func = sel_ops[sel_op_char]

        newParticles = []
        mathCounter = 0

        def doMathOnParticle(selectedParticle, atr, value):
            if op_char == "abs":
                setattr(selectedParticle, atr, op_func(getattr(selectedParticle, atr)))
            elif op_char == "=":
                setattr(selectedParticle, atr, value)
            elif op_char == "remainder":
                setattr(selectedParticle, atr,
                        getattr(selectedParticle, atr) - value * int(float(getattr(selectedParticle, atr)) / value))
            else:
                setattr(selectedParticle, atr, op_func(getattr(selectedParticle, atr), value))
            newParticles.append(selectedParticle)

        while len(particles) > 0:
            selectedParticle = particles.pop(0)
            if sel_atr != "None":
                if not rangeSel:
                    if sel_op_func(getattr(selectedParticle, sel_atr), sel_value):
                        mathCounter += 1
                        doMathOnParticle(selectedParticle, atr, value)
                    else:
                        newParticles.append(selectedParticle)
                else:
                    if ((getattr(selectedParticle, sel_atr) >= rangeLo) and (
                            getattr(selectedParticle, sel_atr) <= rangeHi)):
                        mathCounter += 1
                        doMathOnParticle(selectedParticle, atr, value)
                    else:
                        newParticles.append(selectedParticle)
            else:
                mathCounter += 1
                doMathOnParticle(selectedParticle, atr, value)

        print("%s particles out of %s were affected by math operation." % (mathCounter, str(len(newParticles))))

        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        compValue, selValue, rangeHi, rangeLo, rangeSel = self.validate(args)

        if args.sellb == "None":
            print("Performing math on all particles from star file...")
        else:
            if rangeSel:
                print("Performing math on particles where %s is in range <%s, %s>." % (args.sellb, rangeLo, rangeHi))
            else:
                print("Performing math on particles where %s is %s %s." % (args.sellb, args.selop, selValue))

        md = MetaData(args.i)

        ilabels = md.getLabels()
        if args.lb not in ilabels:
            self.error("No label " + args.lb + " found in Input file.")

        mdOut = MetaData()
        mdOut.addLabels(md.getLabels())

        new_particles = []

        particles = self.get_particles(md)
        new_particles.extend(
            self.mathParticles(particles, args.lb, args.op, compValue, args.selop, args.sellb, selValue, rangeHi,
                               rangeLo, rangeSel))
        mdOut.addData(new_particles)
        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    MathStar().main()
