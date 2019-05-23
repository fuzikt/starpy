#!/usr/bin/env python

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter


class StatsStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Print basic statistics on numerical labels present in STAR file",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', help="Input STAR filename.")
        add('--o', help="Output STAR filename.")
        add('--lb', type=str, default="ALL",
            help="Labels used for statistics (Default: ALL). Multiple labels can be used enclosed in double quotes. (e.g. \"rlnAngleTilt rlnAngleRot\")")

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
            self.error("Input file '%s' not found."
                       % args.i)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def statsOnParticles(self, particles, iLabels):

        def average(values):
            return sum(values) / len(values)

        labelStats = [["Label", "Min", "Max", "Average"]]

        nonNumLabel = 0

        for iLabel in iLabels:
            if iLabel not in LABELS:
                print("WARNING: Label %s not recognized as RELION label!" % iLabel)
            else:
                if (LABELS[iLabel] == float) or (LABELS[iLabel] == int):
                    labelValues = [getattr(x, iLabel) for x in particles]
                    if LABELS[iLabel] == float:
                        labelStats.append([iLabel, '%.2f' % (min(labelValues),), '%.2f' % (max(labelValues),),
                                           '%.2f' % (average(labelValues),)])
                    if LABELS[iLabel] == int:
                        labelStats.append([iLabel, '%.d' % (min(labelValues)), '%.d' % (max(labelValues)),
                                           '%.d' % (average(labelValues))])
                else:
                    # non numerical label
                    nonNumLabel += 1

        widths = [max(map(len, col)) for col in zip(*labelStats)]
        for row in labelStats:
            print("  ".join((val.ljust(width) for val, width in zip(row, widths))))
        print("------------------------------------------------------")
        print("%s records in star file." % str(len(particles)))
        print("%s numerical labels and %s non-numerical labels found." % (len(iLabels) - nonNumLabel, nonNumLabel))

        return

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        md = MetaData(args.i)

        if args.lb == "ALL":
            iLabels = md.getLabels()
        else:
            iLabels = args.lb.split(" ")

        particles = self.get_particles(md)

        self.statsOnParticles(particles, iLabels)


if __name__ == "__main__":
    StatsStar().main()
