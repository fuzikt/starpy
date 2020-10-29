#!/usr/bin/env python

import sys
import os
import numpy as np
import argparse
from copy import deepcopy
from os import listdir
from metadata import MetaData
from os.path import isfile, join
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

parser = argparse.ArgumentParser(
    description="Clusters beam-shifts extracted from mdoc files into opticgroups.")
add = parser.add_argument
add('--i', help="Input mdoc directory.")
add('--istar', default="", help="Input particles star file.")
add('--o', default="", help="Output star file. If empty no file generated generated.")
add('--o_shifts', default="",
    help="Output file with extracted beam-shifts and cluster numbers. If empty no file generated generated.")
add('--clusters', type=str, default="1",
    help="Number of clusters the beam-shifts should be divided in. (default: 1)")
add('--elbow', type=str, default="0",
    help="Number of max clusters used in Elbow method optimal cluster number determination. (default: 0)")
add('--max_iter', type=str, default="300",
    help="Expert option: Maximum number of iterations of the k-means algorithm for a single run. (default: 300)")
add('--n_init', type=str, default="10",
    help="Expert option: Number of time the k-means algorithm will be run with different centroid seeds. (default: 10)")

args = parser.parse_args()

try:
    clusters = int(args.clusters)
    elbow = int(args.elbow)
    max_iter = int(args.max_iter)
    n_init = int(args.n_init)
except ValueError:
    print("--clusters, --elbow, --max_iter and --n_init require integer values for comparison.")
    sys.exit(2)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(2)

if not args.i:
    print("No input file given.")
    parser.print_help()
    sys.exit(2)

if not args.o:
    print("No output file given. No star file will be saved.")

if not os.path.exists(args.i):
    print("Input directory '%s' not found."
          % args.i)
    sys.exit(2)


def elbowMethod(maxClusters, inputArray, maxIter, nInit):
    wcss = []
    for i in range(1, maxClusters):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=maxIter, n_init=nInit, random_state=0)
        kmeans.fit(inputArray)
        wcss.append(kmeans.inertia_)
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.plot(range(1, maxClusters), wcss)
    plt.show()


def kmeansClustering(nClusters, inputArray, maxIter, nInit):
    kmeans = KMeans(n_clusters=nClusters, init='k-means++', max_iter=maxIter, n_init=nInit, random_state=0)
    pred_y = kmeans.fit_predict(inputArray)
    # make cluster numbering start form 1 not 0
    pred_y_1 = [x + 1 for x in pred_y]
    # plot the clustering
    plt.title('Beam-shifts distribution clustering')
    plt.xlabel('Beam-shift X')
    plt.ylabel('Beam-shift Y')
    plt.scatter(inputArray[:, 0], inputArray[:, 1])
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red')
    plt.show()
    return pred_y_1


def saveClusteredShifts(fileName, inputArray, clusterIDs):
    clustered_array = np.append(inputArray, np.reshape(np.array(clusterIDs), (-1, 1)), axis=1)
    np.savetxt(fileName, clustered_array, delimiter=',', header="beamShiftX, beamShiftY, clusterNr")


def saveStarFile(starFileName, mrcFileNames, pred_y):
    with open(starFileName, 'w') as starFile:
        starFile.write("data_\n\nloop_\n_rlnMicrographName #1\n_rlnBeamTiltClass #2\n")
        for mrcFileName, pred_y_val in zip(mrcFileNames, pred_y):
            starFile.write("%s %d\n" % (mrcFileName, pred_y_val))


mdocFiles = [f for f in listdir(args.i) if isfile(join(args.i, f))]

beamShifts = []
mrcFileNames = []
for mdocFileName in mdocFiles:
    if ".mdoc" in mdocFileName and "mic" in mdocFileName:
        mrcFileNames.append("%smrc" % mdocFileName[0:-8])

        mdocFile = open(args.i + "/" + mdocFileName, 'r')
        for line in mdocFile:
            if "ImageShift" in line:
                shiftx = line.split(" ")[2]
                shifty = line.split(" ")[3]
        mdocFile.close()

        beamShifts.append([float(shiftx), float(shifty)])

beamShiftArray = np.array(beamShifts)

if elbow > 0:
    elbowMethod(elbow, beamShiftArray, max_iter, n_init)
else:
    pred_y = kmeansClustering(clusters, beamShiftArray, max_iter, n_init)

micDic = dict(zip(mrcFileNames, pred_y))

if (not args.o == "") and elbow == 0:
    if not args.istar:
        print("No particle star input file given. Please, define one by --istar")
        sys.exit(2)

    # read in particle star file
    md = MetaData(args.istar)

    particles = []

    for particle in md:
        particles.append(particle)

    # create output star file
    mdOut = MetaData()
    mdOut.version = "3.1"
    mdOut.addDataTable("data_optics")
    mdOut.addLabels("data_optics", md.getLabels("data_optics"))
    mdOut.addDataTable("data_particles")
    mdOut.addLabels("data_particles", md.getLabels("data_particles"))

    # create optics groups
    opticGroup = md.data_optics[0]
    opticsGroups = []

    for opticGroupNr in range(max(pred_y)):
        newOpticGroup = deepcopy(opticGroup)
        newOpticGroup.rlnOpticsGroup = opticGroupNr+1
        newOpticGroup.rlnOpticsGroupName = "opticsGroup"+str(opticGroupNr+1)
        opticsGroups.append(newOpticGroup)

    mdOut.addData("data_optics", opticsGroups)

    # create particles table
    new_particles = []

    for particle in particles:
        try:
            particle.rlnOpticsGroup = micDic[particle.rlnMicrographName.split("/")[-1]]
        except:
            print("Warning: No mdoc file found for micrograph: %s. Removing particle from the output star." % particle.rlnMicrographName.split("/")[-1])
        else:
            new_particles.append(particle)

    mdOut.addData("data_particles", new_particles)

    mdOut.write(args.o)

if (not args.o_shifts == "") and elbow == 0:
    saveClusteredShifts(args.o_shifts, beamShiftArray, pred_y)
