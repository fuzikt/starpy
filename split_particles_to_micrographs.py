#!/usr/bin/env python3

import os
import sys
import struct
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter

class splitStacksToMics:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Converts particle MRC stacks into separate MRC files and generate micrograph star file for them.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename.")
        add('--o', help="Output preffix.")

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

    def splitMrcStack(self,stackFile, outFile):
        # extract filename, image index
        imageIndex, mrcsFilename = stackFile.split("@")
        imageIndex = int(imageIndex)

        # read in mrcs file, open mrc file for output
        mrcsFile = open(mrcsFilename, "rb")
        mrcFile = open(outFile, 'wb+')

        # get image size
        imageSize = int(struct.unpack('i', mrcsFile.read(4))[0])

        # write header
        mrcsFile.seek(0, 0)
        chunkSize = 1024
        mrcHeader = mrcsFile.read(chunkSize)
        mrcFile.write(mrcHeader)

        # change Z dimension to 1
        mrcFile.seek(8, 0)
        mrcFile.write(b"\x01\x00")

        mrcFile.seek(1024, 0)

        # write mrc data file
        mrcsFile.seek(imageSize ** 2 * 4 * (imageIndex - 1) + 1024, 0)
        chunkSize = imageSize ** 2 * 4
        mrcImage = mrcsFile.read(chunkSize)
        mrcFile.write(mrcImage)

        mrcsFile.close()
        mrcFile.close()

    def splitParticlesToMicrographs(self,particles, outPrefix):
        newParticles = []
        counter = 0
        one20th = int(len(particles)/20)
        print("Splitting %s particle stacks into separate micrographs..." % str(len(particles)))

        for particle in particles:
            imageIndex, mrcsPath = particle.rlnImageName.split("@")
            mrcsFilename = mrcsPath.split("/")[-1]
            outMicName = outPrefix + "/" + mrcsFilename[:-5]+"_"+imageIndex+".mrc"
            self.splitMrcStack(particle.rlnImageName, outMicName)
            particle.rlnMicrographName = outMicName
            newParticles.append(particle)
            counter += 1
            # a simple progress bar
            sys.stdout.write('\r')
            progress = int(counter / one20th)
            sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
            sys.stdout.flush()
            # sleep(0.25)

        sys.stdout.write('\r\n')
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        md = MetaData(args.i)

        if md.version == "3.1":
            ilabels = md.getLabels("data_particles")
        else:
            ilabels = md.getLabels("data_")

        new_particles = []

        particles = self.get_particles(md)

        if not os.path.exists(args.o):
            os.makedirs(args.o)

        new_particles.extend(self.splitParticlesToMicrographs(particles, args.o))

        if md.version == "3.1":
            mdOut = md.clone()
            dataTableName = "data_particles"
            mdOut.removeDataTable(dataTableName)
        else:
            mdOut = MetaData()
            dataTableName = "data_"

        mdOut.addDataTable(dataTableName, md.isLoop(dataTableName))
        mdOut.addLabels(dataTableName, md.getLabels(dataTableName))
        mdOut.removeLabels(dataTableName, ['rlnImageName'])
        mdOut.addData(dataTableName, new_particles)
        mdOut.write(args.o+".star")

        print("New star file %s created. Have fun!" % args.o+".star")

if __name__ == "__main__":
    splitStacksToMics().main()

