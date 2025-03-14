#!/usr/bin/env python3

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
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--lb', type=str, default="ALL",
            help="Labels used for statistics (Default: ALL). Multiple labels can be used enclosed in double quotes. (e.g. \"rlnAngleTilt rlnAngleRot\")")
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
            self.error("Input file '%s' not found."
                       % args.i)

    def get_records(self, md, dataTable):
        records = []
        for record in getattr(md, dataTable):
            records.append(record)
        return records

    def statsOnRecords(self, records, iLabels):

        def average(values):
            return sum(values) / len(values)

        labelStats = [["#", "Label", "Min", "Max", "Average"]]

        nonNumLabel = 0

        for labelbNr, iLabel in enumerate(iLabels, start=1):
            if iLabel not in LABELS:
                print("WARNING: Label %s not recognized as RELION label!" % iLabel)
            else:
                if (LABELS[iLabel] == float) or (LABELS[iLabel] == int):
                    labelValues = [getattr(x, iLabel) for x in records]
                    if LABELS[iLabel] == float:
                        labelStats.append(
                            ['%s' % labelbNr, iLabel, '%.2f' % (min(labelValues),), '%.2f' % (max(labelValues),),
                             '%.2f' % (average(labelValues),)])
                    if LABELS[iLabel] == int:
                        labelStats.append(
                            ['%s' % labelbNr, iLabel, '%.d' % (min(labelValues)), '%.d' % (max(labelValues)),
                             '%.d' % (average(labelValues))])
                else:
                    # non numerical label
                    nonNumLabel += 1

        widths = [max(map(len, col)) for col in zip(*labelStats)]
        for row in labelStats:
            print("  ".join((val.ljust(width) for val, width in zip(row, widths))))
        print("------------------------------------------------------")
        print("%s records in star file." % str(len(records)))
        print("%s numerical labels and %s non-numerical labels found." % (len(iLabels) - nonNumLabel, nonNumLabel))

        return

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        md = MetaData(args.i)

        dataTable = args.data

        if args.lb == "ALL":
            if md.version == "3.1":
                iLabels = md.getLabels(dataTable)
            else:
                iLabels = md.getLabels("data_")
        else:
            iLabels = args.lb.split(" ")

        records = self.get_records(md, dataTable)

        self.statsOnRecords(records, iLabels)


if __name__ == "__main__":
    StatsStar().main()
