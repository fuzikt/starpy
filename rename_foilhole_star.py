#!/usr/bin/env python

import os
import sys
from metadata import MetaData
import argparse


class RenameStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Rename FoilholeXXX file naming pattern to micXXXX pattern.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename.")
        add('--o', help="Output STAR filename.")
        add('--mic_dir', type=str, default="Micrographs", help="Micrographs directory. Default: Micrographs")

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

    def get_micrographs(self, md):
        micrographs = []
        for micrograph in md:
            micrographs.append(micrograph)
        return micrographs

    def renameMicrographs(self, micrographs, mic_dir):
        i = 0
        newNames = []
        for micrograph in micrographs:
            newName = micrograph.rlnMicrographName[len(micrograph.rlnMicrographName) - 17:len(
                micrograph.rlnMicrographName) - 9] + micrograph.rlnMicrographName[
                                                     len(micrograph.rlnMicrographName) - 8:len(
                                                         micrograph.rlnMicrographName) - 4]
            while (newName + str(i)) in newNames:
                i += 1
            newNames.append(newName + str(i))
            micrograph.rlnMicrographName = mic_dir + "/mic" + newName + str(i) + ".mrc"
            micrograph.rlnCtfImage = mic_dir + "/mic" + newName + str(i) + ".ctf:mrc"
            i = 0
        return micrographs

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)

        print("Reading in input star file.....")

        micrographs = self.get_micrographs(md)

        print("Total %s micrographs in input star file. \nRenaming to micXXX convention." % str(len(micrographs)))

        self.renameMicrographs(micrographs, args.mic_dir)

        mdOut = MetaData()
        if md.version == "3.1":
            mdOut.version = "3.1"
            mdOut.addDataTable("data_optics")
            mdOut.addLabels("data_optics", md.getLabels("data_optics"))
            mdOut.addData("data_optics", getattr(md, "data_optics"))
            particleTableName = "data_particles"
        else:
            particleTableName = "data_"

        mdOut.addDataTable(particleTableName)
        mdOut.addLabels(particleTableName, md.getLabels(particleTableName))
        mdOut.addData(particleTableName, micrographs)

        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    RenameStar().main()
