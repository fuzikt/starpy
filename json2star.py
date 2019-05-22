#!/scratch/work/user/fuzikt/soft/EMAN2/extlib/bin/python2.7

# don't forget to source the EMAN2 !!!!

# python script to correct the box positions in EMAN2 json files
# for boxing done on binned images

import os
from EMAN2 import *

#---------------------------------------------------------------------
# setup part
#---------------------------------------------------------------------

binningFactor = 1 #use 1 if the particles were picked on non-binned micrographs
workingDir = "/scratch/work/user/fuzikt/EV70_win_carbon"
infoDir = "info"
starDir = "box_star"
suffix = "_aibox"

boxsize = 512 # this parameter is only used to exclude boxes from micrograph edges
maxX = 4096 # max size of the micrograph in pixels in X direction (used to exclude boxes from micrograph edges)
maxY = 4096 # max size of the micrograph in pixels in X direction (used to exclude boxes from micrograph edges)


#---------------------------------------------------------------------
# end of setup part
#---------------------------------------------------------------------

if os.path.isdir(workingDir+"/"+starDir) == False:
	os.makedirs(workingDir+"/"+starDir)

totalBoxesExported = 0
totalOutsideBoxes = 0
for fileName in os.listdir(workingDir+"/"+infoDir):
		if fileName.endswith(".json"):
			boxarray=[]
			inputFile=js_open_dict(workingDir+"/"+infoDir+"/"+fileName)
			if "boxes" in inputFile.keys():
				for box in inputFile["boxes"]:
					if ((box[0]*binningFactor+boxsize/2) < maxX) and ((box[1]*binningFactor+boxsize/2) < maxY) and ((box[0]*binningFactor-boxsize/2) >-1) and ((box[1]*binningFactor-boxsize/2) > -1):
						boxarray.append(str(int(box[0]*binningFactor))+" "+str(int(box[1]*binningFactor)))
						totalBoxesExported+=1
					else:
						print "Box x:"+str(int(box[0]*binningFactor))+", y:"+str(int(box[1]*binningFactor))+" found to be outside the micrograph boundaries."
						totalOutsideBoxes+=1
			else:
				print "No boxes were found in "+fileName+"."
			outFileBaseName = os.path.splitext(fileName)[0]
			outFileBaseName = outFileBaseName.replace("_info","")
			outputFile = open(workingDir+"/"+starDir+"/"+outFileBaseName+suffix+".star", "w")
			outputFile.write("\n")
			outputFile.write("data_\n\n")
			outputFile.write("loop_\n")
			outputFile.write("_rlnCoordinateX #1\n")
			outputFile.write("_rlnCoordinateY #2\n")
			outputFile.write("\n".join(boxarray))
			outputFile.close()
			print "Star file "+outFileBaseName+suffix+".star"+" written succesfully."
print "--------------------------------------------------------------------"
print "Total "+str(totalBoxesExported)+" boxes were exported to star files."
print str(totalOutsideBoxes)+" boxes were found outside the micrograph boundaries and were not exported."
print "You can find the generated star files in "+workingDir+"/"+starDir+".\n Move them to the micrograph directory for particle extraction by RELION.\n Have fun... See you next time..."
