#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse
import numpy as np
import matplotlib.pyplot as plt
import healpy as hp
from healpy.newvisufunc import projview


class HeatmapStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Makes a heatmap of particle orientations.")
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename with particles and orientations (Default: STDIN).")
        add('--o', type=str, default="heatmap_orient", help="Output files prefix. Default: heatmap_orient")
        add('--show', action='store_true',
            help="Only shows the resulting heatmap. Does not store any output file.")
        add('--format', type=str, default="png",
            help="Output format. Available formats: png, svg, jpg, tif. Default: png")
        add('--cmap', type=str, default="turbo",
            help="Color map used for the heatmap. Matplotlib colormap names accepted. Recommended: jet, inferno, viridis, turbo. (Default: turbo)")
        add('--mask_zero', action='store_true',
            help="Mask zero values not to be represented by color. (i.e. zero values represented by white)")
        add('--grid_size', type=int, default=50,
            help="Grid size of the hexbin grid. The higher number the finer sampling. Default: 50")
        add('--hlpx', action='store_true',
            help="Create HealPix style maps")
        add('--hlpx_order', type=int, default=4,
            help="HealPix sampling order used for plotting (2->15deg,3->7.5deg, 4->3.75). Default: 4 (3.75deg)")
        add('--no_graticule', action='store_true',
            help="Do not plot graticule on HealPix maps.")
        add('--vmin', type=float, default=-1,
            help="Min values represented on color bar. Default: -1 (auto)")
        add('--vmax', type=float, default=-1,
            help="Max values represented on color bar. Default: -1 (auto)")
        add('--legacy', action='store_true',
            help="Creates old (original) style heatmaps")

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

        if not os.path.exists(args.i) and not args.i == "STDIN":
            self.error("Input file '%s' not found."
                       % args.i)

        if args.cmap not in list(plt.colormaps):
            self.error("Colormap '%s' is not a valid matplotlib colormap. \nPlease choose one of: %s"
                       % (args.cmap, ",".join(list(plt.colormaps))))

        if args.hlpx_order < 1 or args.hlpx_order > 16:
            self.error("Keep the hlpx_order between reasonable limits (0-16) not %s."
                       % args.hlpx_order)

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

        particles = self.get_particles(md)

        if args.vmin == -1:
            minVal = None
        else:
            minVal = args.vmin
        if args.vmax == -1:
            maxVal = None
        else:
            maxVal = args.vmax

        colorMap = plt.colormaps[args.cmap]

        if not args.hlpx:
            tilt = np.zeros(len(particles))
            rot = np.zeros(len(particles))

            for index, particle in enumerate(particles):
                rot[index] = particle.rlnAngleRot
                tilt[index] = particle.rlnAngleTilt - 90

            if args.mask_zero:
                minCount = 1
            else:
                minCount = 0

            fig_hexbin = plt.figure(figsize=(10, 8), dpi=80, )
            ax_hexbin = fig_hexbin.add_subplot(111)
            hb = ax_hexbin.hexbin(rot, tilt, gridsize=args.grid_size, cmap=colorMap, mincnt=minCount, vmin=minVal,
                                  vmax=maxVal)
            ax_hexbin = plt.gca()
            ax_hexbin.set(xlim=(-180, 180), ylim=(-90, 90))
            # ax_hexbin.set_title("Hexagon binning")
            cbar_hexbin = fig_hexbin.colorbar(hb, orientation='horizontal', label="# of particles")
            cbar_hexbin.ax.tick_params(labelsize=14)
            cbar_hexbin.set_label(label="# of particles", fontsize=14)
            xlabels = ['$-180^\circ$', '$-135^\circ$', '$90^\circ$', '$45^\circ$', '$0^\circ$',
                       '$45^\circ$', '$90^\circ$', '$135^\circ$', '$180^\circ$']
            ylabels = ['$-90^\circ$', '$-45^\circ$', '$0^\circ$', '$45^\circ$',
                       '$90^\circ$']
            plt.yticks(np.arange(-90, 90.1, step=45))
            plt.xticks(np.arange(-180, 180.1, step=45))
            fig_hexbin.canvas.manager.set_window_title(os.path.basename(args.i))

            plt.tick_params(axis="x", labelsize=14)
            plt.tick_params(axis="y", labelsize=14)
            ax_hexbin.set_xticklabels(xlabels, fontsize=14)
            ax_hexbin.set_yticklabels(ylabels, fontsize=14)
            plt.tick_params(direction='out', bottom=True, top=False, left=True, right=False)
            plt.xlabel('phi (rot angle)', fontsize=14)
            plt.ylabel('theta (tilt angle)', fontsize=14)
        else:

            hlpOrder = args.hlpx_order
            NSIDE = hlpOrder ** 2

            print("HealPix order %s represents uniform angular sampling of %0.3f degrees." % (hlpOrder, np.degrees(hp.max_pixrad(NSIDE))))

            heatmap_hp = np.zeros(hp.nside2npix(NSIDE))
            for particle in particles:
                if particle.rlnAngleRot <= 0:
                    angleRot = particle.rlnAngleRot + 360
                else:
                    angleRot = particle.rlnAngleRot
                hppix = hp.ang2pix(NSIDE, np.radians(particle.rlnAngleTilt), np.radians(angleRot))
                heatmap_hp[hppix] += 1

            if args.mask_zero:
                heatmap_hp = hp.pixelfunc.ma(heatmap_hp, badval=0, rtol=1e-05, atol=1e-08, copy=True)

            if args.no_graticule:
                gratColor = None
            else:
                gratColor = "white"

            def plotHealpixHeatmap(mapStyle):
                _ = projview(
                    heatmap_hp,
                    fig=0,
                    coord=["G"],
                    min=minVal,
                    max=maxVal,
                    graticule=not (args.no_graticule),
                    graticule_labels=True,
                    # title="Binning with healpix",
                    xlabel="phi (rot angle)",
                    ylabel="theta (tilt angle)",
                    latitude_grid_spacing=15,
                    longitude_grid_spacing=45,
                    xtick_label_color="w",
                    ytick_label_color="black",
                    title = os.path.basename(args.i),
                    fontsize={
                        "xlabel": 14,
                        "ylabel": 14,
                        "xtick_label": 14,
                        "ytick_label": 14,
                        "title": 14,
                        "cbar_label": 14,
                        "cbar_tick_label": 14,
                    },
                    cb_orientation="horizontal",
                    unit="# of particles",
                    flip="astro",
                    projection_type=mapStyle,
                    phi_convention="clockwise",
                    graticule_color=gratColor,
                    cmap=colorMap
                )
                fig = plt.gcf()
                fig.canvas.manager.set_window_title(os.path.basename(args.i))
                return fig


            plotHealpixHeatmap("mollweide")
            plotHealpixHeatmap("cart")

        if args.legacy:
            heatmap = [[0 for col in range(360)] for row in range(180)]
            heatmap = self.makeHeatMap(particles, heatmap)

            if args.mask_zero:
                heatmap = np.array(heatmap)
                heatmap = np.ma.masked_where(heatmap == 0, heatmap)
                colorMap.set_bad(color='white')

            fig_cart = plt.figure(figsize=(10, 8), dpi=80)
            ax_cart = fig_cart.add_subplot(111)
            plt.pcolormesh(heatmap, cmap=colorMap, vmin=minVal, vmax=maxVal)
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

            im = ax_moll.pcolormesh(Lon, Lat, np.flip(heatmap, 0), cmap=colorMap, vmin=minVal, vmax=maxVal)
            cbar = fig_moll.colorbar(im, orientation='horizontal', label="# of particles")
            cbar.ax.tick_params(labelsize=14)
            cbar.set_label(label="# of particles", fontsize=14)

        if args.show:
            plt.show()
        else:
            if args.legacy:
                fig_cart.savefig(args.o + "." + args.format, format=args.format)
                fig_moll.savefig(args.o + "_mollweide." + args.format, format=args.format)
                np.savetxt(args.o + ".dat", heatmap, delimiter=' ', fmt='%1i')
                print("File %s.dat was created..." % args.o)
                print("File %s.%s was created..." % (args.o, args.format))
                print("File %s_mollweide.%s was created..." % (args.o, args.format))
            if not args.hlpx:
                fig_hexbin.savefig(args.o + "_hexbin." + args.format, format=args.format)
                print("File %s_hexbin.%s was created..." % (args.o, args.format))
            else:
                plt.figure(1)
                plt.savefig(args.o + "_hlpx_mollweide." + args.format, format=args.format)
                plt.figure(2)
                plt.savefig(args.o + "_hlpx_cart." + args.format, format=args.format)
                print("File %s_hlpx_mollweide.%s was created..." % (args.o, args.format))
                print("File %s_hlpx_cart.%s was created..." % (args.o, args.format))

        print("Finished. Have fun!")


if __name__ == "__main__":
    HeatmapStar().main()
