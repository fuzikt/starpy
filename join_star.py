#!/usr/bin/env python

import os
import sys
import copy
from math import *
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter
from collections import OrderedDict


class JoinStar():
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Join two star files. Joining options:UNION, INTERSECT, EXCEPT. \n Example1: Include all line from Input1 and Input2 in the Output star file.\n join_star.py --i1 input1.star --i2 input2.star --o output.star \n\n Example2: Select all lines from Input1 where micrographs DO match micrographs in Input2.\n join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"intersect\"\n\n Example3: Select all lines from Input1 where micrographs DO NOT match micrographs in Input2.\n join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"except\"",  formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i1', help="Input1 STAR filename with particles.")
        add('--i2', help="Input2 STAR filename with particles.")
        add('--o', help="Output STAR filename.")
        add('--lb', type=str, default="rlnMicrographName",
              help="Label used for intersect/except joining. e.g. rlnAngleTilt, rlnDefocusU...; Default: rlnMicrographName")
        add('--op', type=str, default="=",
              help="Operator used for comparison. Allowed: \"union\", \"interect\", \"except\" ")

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

        if not os.path.exists(args.i1):
            self.error("Input1 file '%s' not found."
                       % args.i)

        if (args.lb not in LABELS):
            self.error("Label "+args.lb+" not recognized as RELION label.")

        if not os.path.exists(args.i2):
            self.error("Input2 file '%s' not found."
                       % args.i)



    def get_particles(self, md):
        particles = []
        for particle in md:
                particles.append(particle)
        return particles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        print "Selecting particles from star file..."

        md1 = MetaData(args.i1)
        md2 = MetaData(args.i2)
#UNION
        if args.op == "union":
            # check if both stars contains same labels
            i1labels = md1.getLabels()
            i2labels = md2.getLabels()
            if len(i1labels) != len(i2labels):
                if len(i1labels) > len(i2labels):
                    print("WARNING: Input2 does not contain all the labels of Input1.")
                    missingLabels=[Labels for Labels in i1labels if Labels not in i2labels]
                    for label in missingLabels:
                        if LABELS[label] == float:
                            #add label with default values 0.0
                            print("Adding label "+label+" to Input2 data with default value 0.0.")
                            dic={label:0.0}
                            md2.setLabels(**dic)
                        if LABELS[label] == int:
                            #add label with default values 0
                            print("Adding label "+label+" to Input2 data with default value 0.")
                            dic={label:0}
                            md2.setLabels(**dic)
                        if LABELS[label] == str:
                            #add label with default values "dummy"
                            print("Adding label "+label+" to Input2 data with default value \"dummy\"")
                            dic={label:"dummy"}
                            md2.setLabels(**dic)
                if len(i1labels) < len(i2labels):
                    print("WARNING: Input1 does not contain all the labels of Input2.")
                    missingLabels=[Labels for Labels in i2labels if Labels not in i1labels]
                    for label in missingLabels:
                        if LABELS[label] == float:
                            #add label with default values 0.0
                            print("Adding label "+label+" to Input1 data with default value 0.0.")
                            dic={label:0.0}
                            md1.setLabels(**dic)
                        if LABELS[label] == int:
                            #add label with default values 0
                            print("Adding label "+label+" to Input1 data with default value 0.")
                            dic={label:0}
                            md1.setLabels(**dic)
                        if LABELS[label] == str:
                            #add label with default values "dummy"
                            print("Adding label "+label+" to Input1 data with default value \"dummy\"")
                            dic={label:"dummy"}
                            md1.setLabels(**dic)

            mdOut = MetaData()
            mdOut.addLabels(md1.getLabels())
            particles1 = self.get_particles(md1)
            particles2 = self.get_particles(md2)
            mdOut.addData(particles1)
            mdOut.addData(particles2)
       	    print(str((len(particles1)+len(particles2)))+" particles were selected...")
#INTERSECT
        if args.op == "intersect":
            #create intersect unique values
            ilabels1 = md1.getLabels()
            ilabels2 = md2.getLabels()
            if (args.lb not in ilabels1) or (args.lb not in ilabels2):
                self.error("No label "+args.lb+" found in Input1 or Input2 file.")

            particles1 = self.get_particles(md1)
            particles2 = self.get_particles(md2)
            intersectParticles = []
            selectedValues = []
            
            while len(particles2)>0:
                selectedParticle=particles2.pop(0)
                if getattr(selectedParticle,args.lb) not in selectedValues:
                    selectedValues.append(getattr(selectedParticle,args.lb))
            
            for particle in particles1:
                if getattr(particle,args.lb) in selectedValues:
                   intersectParticles.append(particle)
            mdOut = MetaData()
            mdOut.addLabels(md1.getLabels())
            mdOut.addData(intersectParticles)
       	    print(str(len(intersectParticles))+" particles were selected...")
#EXCEPT
        if args.op == "except":
            #create unique values for except
            ilabels1 = md1.getLabels()
            ilabels2 = md2.getLabels()
            if (args.lb not in ilabels1) or (args.lb not in ilabels2):
                self.error("No label "+args.lb+" found in Input1 or Input2 file.")

            particles1 = self.get_particles(md1)
            particles2 = self.get_particles(md2)
            exceptParticles = []
            selectedValues = []

            while len(particles2)>0:
                selectedParticle=particles2.pop(0)
                if getattr(selectedParticle,args.lb) not in selectedValues:
                    selectedValues.append(getattr(selectedParticle,args.lb))

            for particle in particles1:
                if getattr(particle,args.lb) not in selectedValues:
                  exceptParticles.append(particle)
            mdOut = MetaData()
            mdOut.addLabels(md1.getLabels())
            mdOut.addData(exceptParticles)
            print(str(len(exceptParticles))+" particles were selected...")


        mdOut.write(args.o)

        print("New star file "+args.o+" created. Have fun!")


if __name__ == "__main__":

    JoinStar().main()
