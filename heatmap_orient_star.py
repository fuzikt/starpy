#!/usr/bin/env python

import os
import sys
from metadata import MetaData
import argparse
import numpy as np
import matplotlib.pyplot as plt


class HeatmapStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Makes a heatmap of particle orientations.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename with particles and orientations.")
        add('--o', type=str, default="heatmap_orient", help="Output files prefix. Default: heatmap_orient")
        add('--show', action='store_true',
            help="Only shows the resulting heatmap. Does not store any output file.")
        add('--white_bg', action='store_true',
            help="Set background of the heatmap to white. (i.e. zero values represented by white)")
        add('--black_bg', action='store_true',
            help="Set background of the heatmap to black. (i.e. zero values represented by black)")

        add('--format', type=str, default="png",
            help="Output format. Available formats: png, svg, jpg, tif. Default: png")
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
            if particle.rlnAngleRot <= 0:
                angleRot = particle.rlnAngleRot + 360
            else:
                angleRot = particle.rlnAngleRot
            heatmap[int(particle.rlnAngleTilt)][int(angleRot)] += 1
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


        if args.vmin == -1:
            min = None
        else:
            min = args.vmin
        if args.vmax == -1:
            max = None
        else:
            max = args.vmax

        jetcmap = plt.cm.jet

        if args.white_bg or args.black_bg:
            heatmap = np.array(heatmap)
            heatmap = np.ma.masked_where(heatmap == 0, heatmap)
            if args.white_bg:
                jetcmap.set_bad(color='white')
            else:
                jetcmap.set_bad(color='black')

        fig_cart = plt.figure(figsize=(10, 8), dpi=80)
        ax_cart = fig_cart.add_subplot(111)
        plt.pcolormesh(heatmap, cmap=plt.cm.jet, vmin=min, vmax=max)
        cbar_cart = plt.colorbar(orientation='horizontal', label="# of particles")
        cbar_cart.ax.tick_params(labelsize=14)
        cbar_cart.set_label(label="# of particles", fontsize=14)
        plt.yticks(np.arange(0, 181, step=45))
        plt.xticks(np.arange(0, 361, step=45))
        plt.tick_params(axis="x", labelsize=14)
        plt.tick_params(axis="y", labelsize=14)
        ax_cart.set_ylim(180, 0)
        xlabels = ['$0^\circ$', '$45^\circ$', '$90^\circ$', '$135^\circ$', '$180^\circ$',
                   '$225^\circ$', '$270^\circ$', '$315^\circ$', '$360^\circ$']
        ylabels = ['$0^\circ$', '$45^\circ$', '$90^\circ$', '$135^\circ$',
                   '$180^\circ$']
        ax_cart.set_xticklabels(xlabels, fontsize=14)
        ax_cart.set_yticklabels(ylabels, fontsize=14)
        plt.tick_params(direction='out', bottom=True, top=False, left=True, right=False)
        plt.xlabel('phi (rot angle)', fontsize=14)
        plt.ylabel('theta (tilt angle)', fontsize=14)

        # make mollweide projection plot
        fig_moll = plt.figure(figsize=(10, 8), dpi=80, )
        ax_moll = fig_moll.add_subplot(111, projection='mollweide')
        lon = np.linspace(-np.pi, np.pi, 360)
        lat = np.linspace(-np.pi / 2., np.pi / 2., 180)
        xlabels = ['$30^\circ$', '$60^\circ$', '$90^\circ$', '$120^\circ$', '$150^\circ$',
                   '$180^\circ$', '$210^\circ$', '$240^\circ$', '$270^\circ$', '$300^\circ$', '$330^\circ$', ]
        ylabels = ['$165^\circ$', '$150^\circ$', '$135^\circ$', '$120^\circ$',
                   '$105^\circ$', '$90^\circ$', '$75^\circ$', '$60^\circ$',
                   '$45^\circ$', '$30^\circ$', '$15^\circ$']
        ax_moll.set_xticklabels(xlabels, fontsize=14, color="white")
        ax_moll.set_yticklabels(ylabels, fontsize=14)

        plt.xlabel('phi (rot angle)', fontsize=14)
        plt.ylabel('theta (tilt angle)', fontsize=14)
        Lon, Lat = np.meshgrid(lon, lat)

        im = ax_moll.pcolormesh(Lon, Lat, np.flip(heatmap, 0), cmap=plt.cm.jet, vmin=min, vmax=max)
        cbar = fig_moll.colorbar(im, orientation='horizontal', label="# of particles")
        cbar.ax.tick_params(labelsize=14)
        cbar.set_label(label="# of particles", fontsize=14)

        if args.show:
            plt.show()
        else:
            fig_cart.savefig(args.o + "." + args.format, format=args.format)
            fig_moll.savefig(args.o + "_mollweide." + args.format, format=args.format)
            np.savetxt(args.o + ".dat", heatmap, delimiter=' ', fmt='%1i')

            print("File %s.dat was created..." % args.o)
            print("File %s.%s was created..." % (args.o, args.format))
            print("File %s_mollweide.%s was created..." % (args.o, args.format))
        print("Finished. Have fun!")


if __name__ == "__main__":
    HeatmapStar().main()
