#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
from metadata import LABELS
import argparse
from argparse import RawTextHelpFormatter
from matplotlib import pyplot as plt
import numpy


class PlotStar:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Plots values of defined label(s) from STAR file.",
            formatter_class=RawTextHelpFormatter)
        add = self.parser.add_argument
        add('--i', default="STDIN", help="Input STAR filename. Multiple files allowed separated by comma or by space (then all must be enclosed in double quotes) (Default: STDIN).")
        add('--data', type=str, default="data_particles",
            help="Data table from star file to be used (Default: data_particles).")
        add('--lbx', type=str, default="",
            help="Label used for X axis (Default: None). If not defined, X axis is per record in the data table (e.g. per particle)")
        add('--lby', type=str, default="",
            help="Labels used for plot (Y-axis values). Accepts multiple labels to plot (separated by comma, or by space (then all must be enclosed in double quotes)).")
        add('--hist_bins', type=int, default=0,
            help="Number of bins for plotting a histogram. If set to >0 then histogram is plotted.")
        add('--scatter', action='store_true',
            help="Sets scatter type of plot.")
        add('--threshold', type=str, default="",
            help="Draw a threshold line at the defined y value. Multiple values accepted, separated by comma (e.g. 0.5,0.143). (Default: none)"
            )
        add('--thresholdx', type=str, default="",
            help="Draw a threshold line at the defined x value. Multiple values accepted, separated by comma (e.g. 0.5,0.143). (Default: none)"
            )
        add('--multiplotY', type=str, default="1,1",
            help="Create separate plot for each --lby in a grid (Default: 1,1 = single plot). Define in parameter number of rows and columns  (e.g. --multiplotY \"2,3\")")
        add('--multiplotFile', type=str, default="1,1",
            help="Create separate plot for each file in --i in a grid (Default: 1,1 = single plot). Define in parameter number of rows and columns  (e.g. --multiplotFile \"2,3\")")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if " " in args.i:
            inputFiles = str(args.i).replace('\n', ' ').split(" ")
        elif "," in args.i:
            inputFiles = str(args.i).replace('\n', ' ').split(",")
        else:
            inputFiles = [str(args.i)]

        for inputFile in inputFiles:
            if not os.path.exists(inputFile) and not inputFile == "STDIN":
                self.error("Input file '%s' not found."
                           % inputFile)

        if args.multiplotFile != "1,1" and args.multiplotY != "1,1":
            self.error("You cannot use --multiplotFile and --multiplotY simultaneously!")

        if args.lby == "":
            self.error("At least one label has to be defined for plotting in --lby")
        else:
            for lb in args.lby.split(","):
                if not lb in LABELS:
                    self.error("Unknown Relion label %s" % lb)
                if not (LABELS[lb] == float or LABELS[lb] == int):
                    self.error("Label %s is non-numerical thus non-plottable" % lb)

        if args.scatter and args.hist_bins > 0:
            self.error("You cannot use --scatter and --hist_bins at the same time.")

    def get_particles(self, md, dataTable):
        particles = []
        if md.version != "3.1":
            dataTable="data_"
        for particle in getattr(md, dataTable):
            particles.append(particle)
        return particles

    def getLabelValues(self, particles, label):
        labelValues = []
        for particle in particles:
            labelValues.append(getattr(particle, label))
        return labelValues

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        if " " in args.i:
            inputFiles = str(args.i).replace('\n', ' ').split(" ")
        elif "," in args.i:
            inputFiles = str(args.i).replace('\n', ' ').split(",")
        else:
            inputFiles = [str(args.i)]

        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['ps.fonttype'] = 42
        plt.rcParams['svg.fonttype'] = 'none'  # Export text as editable text, not paths
        plt.rcParams['font.family'] = 'DejaVu Sans'  # Use a standard font

        multiplotY = [int(item) for item in args.multiplotY.split(",")]
        multiplotFile = [int(item) for item in args.multiplotFile.split(",")]

        maxTilesX, maxTilesY = max(multiplotY, multiplotFile)

        if multiplotY > multiplotFile:
            multiplotY = True
            multiplotFile = False
        else:
            multiplotFile = True
            multiplotY = False

        if maxTilesX > 1 or maxTilesY > 1:
            figure, axis = plt.subplots(maxTilesX, maxTilesY)
            figure.canvas.manager.set_window_title(", ".join([os.path.basename(i) for i in args.i.split(",")]))
        else:
            figure, axis = plt.subplots(1, 1)
            figure.canvas.manager.set_window_title(", ".join([os.path.basename(i) for i in args.i.split(",")]))

        tileX = tileY = 0

        def setSingleMultiRowColTileIndex(tileX, tileY, maxTilesX, maxTilesY):
            if maxTilesX == 1 or maxTilesY == 1:
                # this is a 1 row or column multiplot
                axisTile = max(tileX, tileY)
            else:
                axisTile = (tileX, tileY)
            return axisTile

        def alternateTiles(tileX, tileY, maxTilesX, maxTilesY):
            if tileY + 1 < maxTilesY:
                tileY += 1
            elif tileX + 1 < maxTilesX:
                tileY = 0
                tileX += 1
            else:
                tileX = tileY = 0
            return tileX, tileY

        axisTile = setSingleMultiRowColTileIndex(tileX, tileY, maxTilesX, maxTilesY)

        yTitle = plotTitle = ""

        for inputFile in inputFiles:
            md = MetaData(inputFile)

            dataTable = str(args.data)
            particles = self.get_particles(md, dataTable)

            plotTitle = inputFile
            xTitle = args.lbx

            if args.lbx == "" or args.hist_bins > 0:
                xValues = range(len(particles))
                xTitle = "record #"
            else:
                xValues = self.getLabelValues(particles, args.lbx)

            yLabels = str(args.lby).split(",")

            if (len(yLabels) > 1 or len(inputFiles) > 1) and args.hist_bins > 0:
                alphaVal = 0.5
            else:
                alphaVal = 1

            for yLabel in yLabels:
                yValues = self.getLabelValues(particles, yLabel)

                yTitle = yLabel
                if type(axis) == numpy.ndarray:  # multiplot
                    axis[axisTile].set_title(plotTitle)
                    if args.hist_bins > 0:
                        axis[axisTile].set_xlabel(yTitle)
                        axis[axisTile].set_ylabel("count")
                        axis[axisTile].hist(yValues, args.hist_bins, alpha=alphaVal, label=yLabel)
                    else:
                        axis[axisTile].set_xlabel(xTitle)
                        axis[axisTile].set_ylabel(yTitle)
                        if args.scatter:
                            axis[axisTile].scatter(xValues, yValues, label=yLabel)
                        else:
                            axis[axisTile].plot(xValues, yValues, label=yLabel)
                else:  # single plot
                    if args.hist_bins > 0:  # histogram
                        axis.set_xlabel(yTitle)
                        axis.set_ylabel("count")
                        axis.hist(yValues, args.hist_bins, alpha=alphaVal, label=yLabel)
                    else:
                        axis.set_xlabel(xTitle)
                        axis.set_ylabel(yTitle)
                        if args.scatter:  # scatter
                            axis.scatter(xValues, yValues, label=yLabel)
                        else:  # line plot
                            axis.plot(xValues, yValues, label=yLabel)

                if multiplotY:
                    tileX, tileY = alternateTiles(tileX, tileY, maxTilesX, maxTilesY)
                    axisTile = setSingleMultiRowColTileIndex(tileX, tileY, maxTilesX, maxTilesY)

            if multiplotY:
                tileX = tileY = 0
                axisTile = setSingleMultiRowColTileIndex(tileX, tileY, maxTilesX, maxTilesY)

            if multiplotFile:
                tileX, tileY = alternateTiles(tileX, tileY, maxTilesX, maxTilesY)
                axisTile = setSingleMultiRowColTileIndex(tileX, tileY, maxTilesX, maxTilesY)

        if args.threshold != "":
            for thresholdValue in args.threshold.split(","):
                plt.axhline(y=float(thresholdValue), linestyle=':')

        if args.thresholdx != "":
            for thresholdValue in args.thresholdx.split(","):
                plt.axvline(x=float(thresholdValue), linestyle=':')

        if maxTilesX > 1 or maxTilesY > 1:
            # a bit of plot formatting for multiplot
            manager = plt.get_current_fig_manager()
            screen_height = manager.window.winfo_screenheight()
            # Make window square based on screen height
            window_size = screen_height - 100
            x = (manager.window.winfo_screenwidth() - window_size) // 2
            y = 50  # Leave some space at the top
            manager.window.geometry(f'{window_size}x{window_size}+{x}+{y}')
            # Add some space between subplots
            figure.subplots_adjust(hspace=0.35)  # Increase vertical space between plots (to make plot title not overlapping with x axis label)
            figure.subplots_adjust(wspace=0.2) # Increase horizontal space between plots (to make y axis label not overlapping with y axis)
            figure.subplots_adjust(left = 0.1, right = 0.95, top = 0.95, bottom = 0.05)

        plt.legend()
        plt.show()


if __name__ == "__main__":
    PlotStar().main()
