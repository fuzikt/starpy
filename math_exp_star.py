#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter
import cexprtk


class MathExpStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Performs complex math operations on star file values defined by user provided expression. \n Example1: Add 15 deg to rlnAngleTilt. \n math_exp_star.py --i input.star --o output.star --lb_res rlnAngleTilt --exp  \"rlnAngleTilt+15\" \n\n Example2: Multiply rlnOriginX by 2 if rlnOriginX+rlnOriginY is less than 50\n math_exp_star.py --i input.star --o output.star --lb_res rlnOriginX --exp \"rlnOriginX*2\" --sel_exp \"(rlnOriginX+rlnOriginY)<50\" \n\n Example3: Compute cosine of rlnAngleRot and store it under label rlnCosAngleRot.\n math_exp_star.py --i input.star --o output.star --lb_res rlnCosAngleRot --exp \"cos(deg2rad(rlnAngleRot))\" ",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--data', type=str, default="data_particles",
            help="Data table from star file to be used (Default: data_particles).")
        add('--res_lb', type=str, default="rlnResult",
            help="Label used for storing the result (e.g. rlnAngleTilt, rlnDefocusU...). If the label is not present in input file, it will be created. Default: rlnResult")
        add('--exp', type=str, default="",
            help="Expression to be evaluated. Enclose in double quotes!!! (e.g. \"(rlnDefocusU - rlnDefocusV)/2\")")
        add('--sel_exp', type=str, default="",
            help="Expression used for selection of particles on which the --exp will be evaluated. Enclose in double quotes!!!  (e.g.  \"(rlnDefocusU-1500)<20000\"), Default empty => all particles")
        add('--def_val', type=float, default=0.0,help="Default value of non-calculated results when --res_lb is not present in --i. (Default: 0.0)")

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

        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error(f"Input file '{args.i}' not found.")

        if not args.exp:
            self.error("No expression provided (--exp)")

        if args.res_lb and not args.res_lb.startswith('rln'):
            self.error("Result label must start with 'rln'")

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

    def extract_variables(self, expression):
        # Remove whitespace and common mathematical operators/symbols
        operators = {'+', '-', '*', '/', '^', '(', ')', ',', ' ', '\t', '\n'}

        # Split expression into tokens
        tokens = []
        current = []

        for char in expression:
            if char in operators:
                if current:
                    tokens.append(''.join(current))
                    current = []
            else:
                current.append(char)

        if current:
            tokens.append(''.join(current))

        # Filter for valid RELION labels (starting with 'rln')
        variables = {
            token for token in tokens
            if token.startswith('rln') and token in LABELS
        }

        return variables

    def validate_variables(self, expression_vars, selection_vars, ilabels):
        # Convert to sets for faster lookup
        all_vars = expression_vars | selection_vars
        ilabels_set = set(ilabels)

        # Find missing variables
        missing_vars = all_vars - ilabels_set

        if missing_vars:
            missing_list = ", ".join(sorted(missing_vars))
            self.error(f"Labels not found in input file: {missing_list}")

        # Check if variables are numerical types
        non_numeric = []
        for var in all_vars:
            label_type = LABELS.get(var)
            if label_type not in (float, int):
                non_numeric.append(var)

        if non_numeric:
            non_numeric_list = ", ".join(sorted(non_numeric))
            self.error(f"Labels must be numerical types: {non_numeric_list}")

        return True

    def validate_expressions(self, expression, sel_expression):
        try:
            if expression:
                cexprtk.check_expression(expression)
            if sel_expression and sel_expression != "1":
                cexprtk.check_expression(sel_expression)
            return True
        except Exception as e:
            self.error(f"Invalid expression syntax: {str(e)}")

    def mathParticles(self, particles, res_lb, expression, sel_expression, expression_vars, selection_vars, defalut_value):
        counter = 0
        for particle in particles:
            selection_variables = {}
            expression_variables = {}
            for selection_var in selection_vars:
                selection_variables[selection_var] = getattr(particle, selection_var)
            for expression_var in expression_vars:
                expression_variables[expression_var] = getattr(particle, expression_var)
            # Evaluate selection expression
            if cexprtk.evaluate_expression(sel_expression, selection_variables) > 0:
                setattr(particle,res_lb, cexprtk.evaluate_expression(expression, expression_variables))
                counter += 1
            else:
                if not hasattr(particle, res_lb):
                    setattr(particle, res_lb, defalut_value)

        self.mprint(f"{counter} particles fulfilled the selection criterion.")
        return particles


    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)

        dataTableName = args.data

        if md.version == "3.1":
            ilabels = md.getLabels(dataTableName)
        else:
            ilabels = md.getLabels("data_")
            dataTableName = "data_"

        if args.sel_exp == "":
            args.sel_exp = "1" # Default (empty) selection expression includes all particles

        # Validate expression syntax
        self.validate_expressions(args.exp, args.sel_exp)

        expression_vars = self.extract_variables(args.exp)
        selection_vars = self.extract_variables(args.sel_exp)

        self.validate_variables(expression_vars, selection_vars, ilabels)

        particles = self.get_particles(md, dataTableName)

        self.mprint(f"Processing {len(particles)} particles...")

        self.mathParticles(particles, args.res_lb, args.exp, args.sel_exp, expression_vars, selection_vars, args.def_val)
        if args.res_lb not in ilabels:
            ilabels.append(args.res_lb)

        md.addLabels(dataTableName, ilabels)
        md.write(args.o)

        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    MathExpStar().main()
