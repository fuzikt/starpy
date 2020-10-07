#!/usr/bin/env python

import sys
import os
import numpy as np
import argparse
from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

parser = argparse.ArgumentParser(
    description="Clusters beam-shifts extracted from xml files into beam-tilt classes.")
add = parser.add_argument
add('--i', help="Input XML directory.")
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


xmlfiles = [f for f in listdir(args.i) if isfile(join(args.i, f))]

beamShifts = []
mrcFileNames = []
for xmlfile in xmlfiles:
    if ".xml" in xmlfile:
        mrcFileNames.append("%smrc" % xmlfile[0:-3])
        xmldoc = minidom.parse("%s/%s" % (args.i, xmlfile))
        beamshiftItems = xmldoc.getElementsByTagName("BeamShift")[0]
        shiftx = beamshiftItems.getElementsByTagName("a:_x")
        shifty = beamshiftItems.getElementsByTagName("a:_y")
        beamShifts.append([float(shiftx[0].childNodes[0].nodeValue), float(shifty[0].childNodes[0].nodeValue)])

beamShiftArray = np.array(beamShifts)

if elbow > 0:
    elbowMethod(elbow, beamShiftArray, max_iter, n_init)
else:
    pred_y = kmeansClustering(clusters, beamShiftArray, max_iter, n_init)

if (not args.o == "") and elbow == 0:
    saveStarFile(args.o, mrcFileNames, pred_y)

if (not args.o_shifts == "") and elbow == 0:
    saveClusteredShifts(args.o_shifts, beamShiftArray, pred_y)
