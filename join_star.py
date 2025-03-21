#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter
import time


class JoinStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Join two star files. Joining options:UNION, INTERSECT, EXCEPT. \n Example1: Include all line from Input1 and Input2 in the Output star file.\n join_star.py --i1 input1.star --i2 input2.star --o output.star \n\n Example2: Select all lines from Input1 where micrographs DO match micrographs in Input2.\n join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"intersect\"\n\n Example3: Select all lines from Input1 where micrographs DO NOT match micrographs in Input2.\n join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"except\"",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i1', default="STDIN", help="Input1 STAR filename (Default: STDIN).")
        add('--i2', default="STDIN", help="Input2 STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
        add('--data', type=str, default="data_particles",
            help="Data table from star file to be used (Default: data_particles).")
        add('--lb', type=str, default="rlnMicrographName",
            help="Label used for intersect/except joining. e.g. rlnAngleTilt, rlnDefocusU...; Default: rlnMicrographName")
        add('--op', type=str, default="=",
            help="Operator used for comparison. Allowed: \"union\", \"intersect\", \"except\" ")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if not os.path.exists(args.i1) and not args.i1 == "STDIN":
            self.error("Input1 file '%s' not found." % args.i1)

        if not os.path.exists(args.i2) and not args.i2 == "STDIN":
            self.error("Input2 file '%s' not found." % args.i2)

        if args.lb not in LABELS:
            self.error("Label %s not recognized as RELION label." % args.lb)

        if not os.path.exists(args.i2):
            self.error("Input2 file '%s' not found." % args.i)

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

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)
        start_total = time.time()
        self.mprint("Selecting particles from star file...")

        md1 = MetaData(args.i1)
        md2 = MetaData(args.i2)

        dataTableName = args.data

        # UNION
        if args.op == "union":
            # check if both stars contains same labels
            if md1.version == "3.1":
                i1labels = md1.getLabels(dataTableName)
                i2labels = md2.getLabels(dataTableName)
            else:
                i1labels = md1.getLabels("data_")
                i2labels = md2.getLabels("data_")
                dataTableName = "data_"
            if len(i1labels) != len(i2labels):
                if len(i1labels) > len(i2labels):
                    self.mprint("WARNING: Input2 does not contain all the labels of Input1.")
                    missingLabels = [Labels for Labels in i1labels if Labels not in i2labels]
                    for label in missingLabels:
                        if LABELS[label] == float:
                            # add label with default values 0.0
                            self.mprint("Adding label %s to Input2 data with default value 0.0." % label)
                            dic = {label: 0.0}
                            md2.setLabels(dataTableName, **dic)
                        if LABELS[label] == int:
                            # add label with default values 0
                            self.mprint("Adding label %s to Input2 data with default value 0." % label)
                            dic = {label: 0}
                            md2.setLabels(dataTableName, **dic)
                        if LABELS[label] == str:
                            # add label with default values "dummy"
                            self.mprint("Adding label %s to Input2 data with default value \"dummy\"" % label)
                            dic = {label: "dummy"}
                            md2.setLabels(dataTableName, **dic)
                if len(i1labels) < len(i2labels):
                    self.mprint("WARNING: Input1 does not contain all the labels of Input2.")
                    missingLabels = [Labels for Labels in i2labels if Labels not in i1labels]
                    for label in missingLabels:
                        if LABELS[label] == float:
                            # add label with default values 0.0
                            self.mprint("Adding label %s to Input1 data with default value 0.0." % label)
                            dic = {label: 0.0}
                            md1.setLabels(dataTableName, **dic)
                        if LABELS[label] == int:
                            # add label with default values 0
                            self.mprint("Adding label %s to Input1 data with default value 0." % label)
                            dic = {label: 0}
                            md1.setLabels(dataTableName, **dic)
                        if LABELS[label] == str:
                            # add label with default values "dummy"
                            self.mprint("Adding label %s to Input1 data with default value \"dummy\"" % label)
                            dic = {label: "dummy"}
                            md1.setLabels(dataTableName, **dic)

            if md1.version == "3.1":
                mdOut = md1.clone()
                mdOut.removeDataTable(dataTableName)
            else:
                mdOut = MetaData()
                dataTableName = "data_"

            mdOut.addDataTable(dataTableName, md1.isLoop(dataTableName))
            mdOut.addLabels(dataTableName, md1.getLabels(dataTableName))
            particles1 = self.get_particles(md1, dataTableName)
            particles2 = self.get_particles(md2, dataTableName)
            mdOut.addData(dataTableName, particles1)
            mdOut.addData(dataTableName, particles2)
            self.mprint("%s particles were selected..." % str((len(particles1) + len(particles2))))

        # INTERSECT and EXCEPT
        if args.op == "intersect" or args.op == "except":
            if md1.version == "3.1":
                i1labels = md1.getLabels(dataTableName)
                i2labels = md2.getLabels(dataTableName)
            else:
                i1labels = md1.getLabels("data_")
                i2labels = md2.getLabels("data_")
                dataTableName = "data_"
            if (args.lb not in i1labels) or (args.lb not in i2labels):
                self.error("No label %s found in Input1 or Input2 file." % args.lb)

            particles1 = self.get_particles(md1, dataTableName)

            selectedValues = {getattr(p, args.lb) for p in getattr(md2, dataTableName)}

            if args.op == "intersect":
                selectedParticles = [p for p in particles1 if getattr(p, args.lb) in selectedValues]
            else:
                selectedParticles = [p for p in particles1 if getattr(p, args.lb) not in selectedValues]

            if md1.version == "3.1":
                mdOut = md1.clone()
                mdOut.removeDataTable(dataTableName)
            else:
                mdOut = MetaData()
                dataTableName = "data_"

            mdOut.addDataTable(dataTableName, md1.isLoop(dataTableName))
            mdOut.addLabels(dataTableName, md1.getLabels(dataTableName))
            mdOut.addData(dataTableName, selectedParticles)

            self.mprint("%s particles were selected..." % str(len(selectedParticles)))

        mdOut.write(args.o)
        self.mprint(f"Total execution time: {time.time() - start_total:.2f} seconds")
        self.mprint("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    JoinStar().main()
