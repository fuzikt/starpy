#!/usr/bin/env python3

import os
import sys
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
        add('--i', default="STDIN", help="Input STAR filename (Default: STDIN).")
        add('--o', default="STDOUT", help="Output STAR filename (Default: STDOUT).")
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
        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Input file '%s' not found." % args.i)

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)

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

    def removePrefOrient(self, particles, xSD):

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

        self.mprint("Max count of particles per orientation %s" % maxCount)

        self.mprint("Min count of particles per orientation %s" % minCount)

        self.mprint("Average count of particles per orientation %s" % averageParticleCount)

        sigmaSum = 0.0

        for i in range(180):
            for j in range(360):
                if heatmap[i][j] != 0:
                    sigmaSum += (heatmap[i][j] - averageParticleCount) ** 2
        particleSdev = math.sqrt(sigmaSum / (n - 1))

        self.mprint("SD of the average count %.03f" % particleSdev)

        orientationCountTreshold = averageParticleCount + xSD * particleSdev

        self.mprint(
            "Including max %s particles per orientation in the final star file." % int(orientationCountTreshold))

        newParticleSet = []

        self.mprint("Removing overepresented orientations....")

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
            if self.args.o != "STDOUT":
                sys.stdout.write('\r')
                progress = int(i / 9) + 1
                sys.stdout.write("[%-20s] %d%%" % ('=' * progress, 5 * progress))
                sys.stdout.flush()
                # sleep(0.25)
        if self.args.o != "STDOUT":
            sys.stdout.write('\r\n')

        return newParticleSet

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        self.mprint("Making orientation heatmap from star file...")

        md = MetaData(args.i)

        particles = self.get_particles(md)

        new_particles = []

        new_particles.extend(self.removePrefOrient(particles, args.sd))

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

        self.mprint("File %s was created..." % args.o)

        self.mprint("Finished. Have fun!")


if __name__ == "__main__":
    RemovePrefOrientStar().main()
