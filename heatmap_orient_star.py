#!/usr/bin/env python

import os
import sys
import copy
from math import *
from metadata import MetaData
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import OrderedDict


class HeatmapStar():
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Makes a heatmap of particle orientations.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles and orientations.")
        add('--o', type=str, default="heatmap_orient", help="Output files prefix. Default: heatmap_orient")
        add('--format', type=str, default="png",
              help="Output format. Available formats: png, svg, jpg, tif. Dafault: png")
        add('--vmin', type=float, default=-1,
              help="Min values represented on color bar. Default: -1 (auto)")
        add('--vmax', type=float, default=-1,
              help="Max values represented on color bar. Default: -1 (auto)")

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

    def makeHeatMap(self, particles, heatmap):
        for particle in particles:
            if particle.rlnAngleRot<=0:
                angleRot=particle.rlnAngleRot+360
            else:
                angleRot=particle.rlnAngleRot
            heatmap[int(particle.rlnAngleTilt)][int(angleRot)]+=1
        return heatmap

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        print("Making orientation heatmap from star file...")

        md = MetaData(args.i)
        
        heatmap = [[0 for col in range(360)] for row in range(180)]


        particles = self.get_particles(md)

        heatmap = self.makeHeatMap(particles, heatmap)


        plt.imshow(heatmap)

        if args.vmin==-1:
            min=None
        else:
            min=args.vmin
        if args.vmax==-1:
            max=None
        else:
            max=args.vmax

        plt.pcolor(heatmap, cmap=plt.cm.jet,vmin=min, vmax=max)
        plt.colorbar(orientation='horizontal', label="# of particles")

        plt.yticks(np.arange(0, 181, step=45))
        plt.xticks(np.arange(0, 361, step=45))
        plt.tick_params(direction='out',bottom='on', top='off', left='on', right='off')
        plt.xlabel('phi (rot angle)')
        plt.ylabel('theta (tilt angle)')

        plt.savefig(args.o+"."+args.format, format=args.format)

        np.savetxt(args.o+".dat", heatmap, delimiter=' ', fmt='%1i')

        print("File "+args.o+".dat was created...")
        print("File "+ args.o+"."+args.format+" was created...")
        print("Finished. Have fun!")


if __name__ == "__main__":

    HeatmapStar().main()
