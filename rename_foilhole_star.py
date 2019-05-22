#!/usr/bin/env python

import os
import sys
import copy
import random
from math import *
from metadata import MetaData
import argparse
from collections import OrderedDict


class RenameStar():
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
        print "Error: " + '\n'.join(msgs)
        print " "
        sys.exit(2)


    def validate(self, args):
        if len(sys.argv) == 1:
            self.error("Error: No input file given.")

        if not os.path.exists(args.i):
            self.error("Error: Input file '%s' not found."
                       % args.i)

    def get_micrographs(self, md):
        micrographs = []
        for micrograph in md:
                micrographs.append(micrograph)
        return micrographs

    def renameMicrographs(self, micrographs, mic_dir):
        i=0
        newNames = []
        for micrograph in micrographs:
            newName = micrograph.rlnMicrographName[len(micrograph.rlnMicrographName)-17:len(micrograph.rlnMicrographName)-9]+micrograph.rlnMicrographName[len(micrograph.rlnMicrographName)-8:len(micrograph.rlnMicrographName)-4]
            while (newName+str(i)) in newNames:
                i += 1
            newNames.append(newName+str(i))
            micrograph.rlnMicrographName=mic_dir+"/mic"+newName+str(i)+".mrc"
            micrograph.rlnCtfImage=mic_dir+"/mic"+newName+str(i)+".ctf:mrc"
            i = 0
        return micrographs

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)
        mdOut = MetaData()
        mdOut.addLabels(md.getLabels())

        print "Reading in input star file....."

        micrographs=self.get_micrographs(md)

        print "Total "+str(len(micrographs))+" micrographs in input star file. \nRenaming to micXXX convention."

        self.renameMicrographs(micrographs,args.mic_dir)

        mdOut.addData(micrographs)
        mdOut.write(args.o)

        print "New star file "+args.o+" created. Have fun!"


if __name__ == "__main__":

    RenameStar().main()
