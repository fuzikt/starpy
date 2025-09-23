#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter


class StarToCsv:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Converts STAR file values to CSV file",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output CSV filename (Default: STDOUT).")
        add('--lb', type=str, default="ALL",
            help="Labels exported in the CSV file (Default: ALL). Multiple labels can be used enclosed in double quotes. (e.g. \"rlnAngleTilt rlnAngleRot\")")
        add('--data', type=str, default="data_particles",
            help="Data table from star file to be used (Default: data_particles).")
        add("--delim", type=str, default=",",
            help="Delimiter used in the CSV file (Default: \",\"). For space separated use \" \". ")

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

    def generateCSVlines(self, records, iLabels, delimiter):
        header = delimiter.join(iLabels)
        lines = []
        lines.append(header)
        for record in records:
            line = []
            for iLabel in iLabels:
                if iLabel in LABELS:
                    val = getattr(record, iLabel)
                    line.append(str(val))
                else:
                    line.append("NA")
            lines.append(delimiter.join(line))
        return lines

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
            iLabels = args.lb.replace(","," ").split(" ")

        records = self.get_records(md, dataTable)

        csvLines = self.generateCSVlines(records, iLabels, args.delim)

        if args.o == "STDOUT":
            for line in csvLines:
                print(line)
        else:
            with open(args.o, "w") as outFile:
                for line in csvLines:
                    outFile.write(line + "\n")
            print("CSV file written to %s" % args.o)


if __name__ == "__main__":
    StarToCsv().main()
