#!/usr/bin/env python

import os
import sys
# from time import sleep

from metadata import MetaData
import argparse
import math
from argparse import RawTextHelpFormatter


class RemovePrefOrientStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Remove particles with overrepresented orientations.\n Average count of particles at each orientation is calculated.\n Then the count of particles that are n-times SD over the average is modified\n by retaining the particles with the highest rlnMaxValueProbDistribution.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles and orientations.")
        add('--o', type=str, default="output.star", help="Output star file. Default: output.star")
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

    def removePrefOrient(self, particles,xSD):

        # generate array of 1 deg orientation step from rot and tilt angle
        heatmap = [[0 for col in range(360)] for row in range(180)]
        heatmappart = [[[] for col in range(360)] for row in range(180)]

        for partpos, particle in enumerate(particles, start=0):
            if particle.rlnAngleRot <= 0:
                angleRot = particle.rlnAngleRot + 360
            else:
                angleRot = particle.rlnAngleRot
            heatmap[int(particle.rlnAngleTilt)][int(angleRot)] += 1
            heatmappart[int(particle.rlnAngleTilt)][int(angleRot)].append(partpos)

        # calculate statistics (avg and SD)
        particleSum = 0
        n = 0
        maxCount = 0
        minCount = 1

        for i in range(180):
            for j in range(360):
                if heatmap[i][j] != 0:
                    particleSum += heatmap[i][j]
                    if maxCount < heatmap[i][j]: maxCount = heatmap[i][j]
                    if minCount > heatmap[i][j]: minCount = heatmap[i][j]
                    n += 1

        averageParticleCount = particleSum / n

        print("Max count of particles per orientation %s" % maxCount)

        print("Min count of particles per orientation %s" % minCount)

        print("Average count of particles per orientation %s" % averageParticleCount)

        sigmaSum = 0.0

        for i in range(180):
            for j in range(360):
                if heatmap[i][j] != 0:
                    sigmaSum += (heatmap[i][j] - averageParticleCount) ** 2
        particleSdev = math.sqrt(sigmaSum / (n - 1))

        print("SD of the average count %.03f" % particleSdev)

        orientationCountTreshold = averageParticleCount + xSD * particleSdev

        print("Including max %s particles per orientation in the final star file." % int(orientationCountTreshold))

        newParticleSet = []

        print("Removing overepresented orientations....")

        for i in range(180):
            for j in range(360):
                if heatmap[i][j] != 0:
                    if heatmap[i][j] <= int(orientationCountTreshold):
                        # add particles automatically
                        for particlepos in heatmappart[i][j]:
                            newParticleSet.append(particles[particlepos])
                    if heatmap[i][j] > int(orientationCountTreshold):
                        # add particles after reducing their count
                        particlesForReduction = []
                        for particlepos in heatmappart[i][j]:
                            particlesForReduction.append(particles[particlepos])
                        newParticleSet.extend(
                            self.reduceParticlesCount(particlesForReduction, int(orientationCountTreshold)))

            # a simple progress bar
            sys.stdout.write('\r')
            progress = int(i / 9) + 1
            sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
            sys.stdout.flush()
            # sleep(0.25)
        sys.stdout.write('\r\n')

        return newParticleSet

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print("Making orientation heatmap from star file...")

        md = MetaData(args.i)

        particles = self.get_particles(md)

        mdOut = MetaData()

        if md.version == "3.1":
            mdOut.version = "3.1"
            mdOut.addOpticsLabels(md.getOpticsLabels())
            mdOut.addOpticsData(md._data_optics)

        mdOut.addLabels(md.getLabels())

        new_particles = []

        new_particles.extend(self.removePrefOrient(particles, args.sd))

        mdOut.addData(new_particles)
        mdOut.write(args.o)

        print("File %s was created..." % args.o)

        print("Finished. Have fun!")


if __name__ == "__main__":
    RemovePrefOrientStar().main()
