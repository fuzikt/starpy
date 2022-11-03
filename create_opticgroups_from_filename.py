#!/usr/bin/env python3

import os
import sys
from copy import deepcopy
from metadata import MetaData
import argparse


class CreateOpticGroupsFromFilenameStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Add opticsGroups to the particles from micrograph file name.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename.")
        add('--o', help="Output STAR filename.")
        add('--word_count', type=int, default="4", help="Position of the acquisition position identifier in the FoilHole_XXX_Data_YYY_ZZZ.mrc filename. Default: 4 (th word).")

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

    def addOpticGroupsToParticles(self, particles, wordCount):
        newParticles = []
        listOfOpticGroupNames = []
        for particle in particles:
            micrographFileName = particle.rlnMicrographName.split("/")[-1]
            if micrographFileName.split("_")[wordCount-1] in listOfOpticGroupNames:
                particle.rlnOpticsGroup = listOfOpticGroupNames.index(micrographFileName.split("_")[wordCount-1]) + 1
            else:
                listOfOpticGroupNames.append(micrographFileName.split("_")[wordCount-1])
                particle.rlnOpticsGroup = len(listOfOpticGroupNames)
            newParticles.append(particle)
        return newParticles, listOfOpticGroupNames

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)

        # create output star file
        mdOut = MetaData()
        mdOut.version = "3.1"
        mdOut.addDataTable("data_optics", True)
        mdOut.addLabels("data_optics", md.getLabels("data_optics"))
        mdOut.addDataTable("data_particles", True)
        mdOut.addLabels("data_particles", md.getLabels("data_particles"))

        if "rlnOpticsGroup" not in md.getLabels("data_particles"):
            mdOut.addLabels("data_particles",  "rlnOpticsGroup")

        print("Reading in input star file.....")
        particles = self.get_particles(md)
        print("Total %s particles in input star file. \nAdding rlnOpticsGroup." % str(len(particles)))

        new_particles, opticsGroupsNames = self.addOpticGroupsToParticles(particles, args.word_count)

        # create new optics groups
        opticGroup = md.data_optics[0]
        opticsGroups = []

        for opticGroupNr, opticGroupName in enumerate(opticsGroupsNames):
            newOpticGroup = deepcopy(opticGroup)
            newOpticGroup.rlnOpticsGroup = opticGroupNr + 1
            newOpticGroup.rlnOpticsGroupName = "opticsGroup_" + str(opticGroupName)
            opticsGroups.append(newOpticGroup)

        mdOut.addData("data_optics", opticsGroups)

        mdOut.addData("data_particles", new_particles)

        mdOut.write(args.o)

        print("New star file %s created. Have fun!" % args.o)


if __name__ == "__main__":
    CreateOpticGroupsFromFilenameStar().main()
