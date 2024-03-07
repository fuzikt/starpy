#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
import math
from argparse import RawTextHelpFormatter
import healpy as hp


class RemovePrefOrientStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Remove particles with overrepresented orientations by sorting them into HealPix based orientation bins.\n Average count of particles per orientation bin is calculated.\n Then the count of particles that are n-times SD over the average is modified\n by retaining the particles with the highest rlnMaxValueProbDistribution.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles and orientations.")
        add('--o', type=str, default="output.star", help="Output star file. Default: output.star")
        add('--hlpx_order', type=int, default=4,
            help="HealPix sampling order used for sorting particles into orientation bins (2->15deg,3->7.5deg, 4->3.75). Default: 4 (3.75deg)")
        add('--sd', type=float, default=3,
            help="This many times SD above the average count will be representations kept. Default: 3")

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

    def reduceParticlesCount(self, particles, maxCount):

        sortedParticles = []
        particlesToSort = []

        def sortSecond(val):
            return val[1]

        for partPos, particle in enumerate(particles, start=0):
            particlesToSort.append([partPos, particle.rlnMaxValueProbDistribution])

        particlesToSort.sort(key=sortSecond, reverse=True)

        for i in range(maxCount):
            selectedParticle = particlesToSort.pop(0)
            sortedParticles.append(particles[selectedParticle[0]])

        return sortedParticles

    def removePrefOrient(self, particles, xSD, hlpxOrder):

        NSIDE = hlpxOrder ** 2

        hlpx_orient_bins = [[] for _ in range(hp.nside2npix(NSIDE))]
        print("Sorting particles into %s HealPix bins at uniform angular sampling of %.2f." % (
        len(hlpx_orient_bins), math.degrees(hp.max_pixrad(NSIDE))))

        for particle in particles:
            hppix = hp.ang2pix(NSIDE, math.radians(particle.rlnAngleTilt), math.radians(particle.rlnAngleRot))
            hlpx_orient_bins[hppix].append(particle)

        # calculate statistics (avg and SD)
        particleSum = 0
        n = 0
        maxCount = 0
        minCount = 1

        for hlpx_bin in hlpx_orient_bins:
            if len(hlpx_bin) != 0:
                particleSum += len(hlpx_bin)
                maxCount = max(maxCount, len(hlpx_bin))
                minCount = min(minCount, len(hlpx_bin))
                n += 1

        averageParticleCount = particleSum / n

        print("Max count of particles per orientation bin: %s" % maxCount)
        print("Min count of particles per orientation bin: %s" % minCount)
        print("Average count of particles per orientation bin %0.2f" % averageParticleCount)

        sigmaSum = 0.0

        for hlpx_bin in hlpx_orient_bins:
            if len(hlpx_bin) != 0:
                sigmaSum += (len(hlpx_bin) - averageParticleCount) ** 2

        particleSdev = math.sqrt(sigmaSum / (n - 1))

        print("SD of the average count per bin: %.02f" % particleSdev)

        orientationCountTreshold = averageParticleCount + xSD * particleSdev

        print("Including max %s particles per orientation bin in the final star file." % int(orientationCountTreshold))

        newParticleSet = []

        print("Removing overrepresented orientations.... Preserving those by highest rlnMaxValueProbDistribution...")

        progress_step = int(len(hlpx_orient_bins) / 20)
        i = 0
        for hlpx_bin in hlpx_orient_bins:
            if len(hlpx_bin) != 0:
                if len(hlpx_bin) <= int(orientationCountTreshold):
                    # add all particles of this hlpx bin
                    for particle in hlpx_bin:
                        newParticleSet.append(particle)
                if len(hlpx_bin) > int(orientationCountTreshold):
                    newParticleSet.extend(
                        self.reduceParticlesCount(hlpx_bin, int(orientationCountTreshold)))

            # a simple progress bar
            sys.stdout.write('\r')
            progress = int(i / progress_step)
            sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
            sys.stdout.flush()
            i += 1

        sys.stdout.write('\r\n')

        return newParticleSet

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)

        particles = self.get_particles(md)
        print("%s particles found in star file." % len(particles))

        new_particles = []

        new_particles.extend(self.removePrefOrient(particles, args.sd, args.hlpx_order))

        if md.version == "3.1":
            mdOut = md.clone()
            dataTableName = "data_particles"
            mdOut.removeDataTable(dataTableName)
        else:
            mdOut = MetaData()
            dataTableName = "data_"

        mdOut.addDataTable(dataTableName, md.isLoop(dataTableName))
        mdOut.addLabels(dataTableName, md.getLabels(dataTableName))
        mdOut.addData(dataTableName, new_particles)
        mdOut.write(args.o)

        print("%s particles written." % len(new_particles))
        print("File %s was created..." % args.o)

        print("Finished. Have fun!")


if __name__ == "__main__":
    RemovePrefOrientStar().main()
