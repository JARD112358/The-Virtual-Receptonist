"""

 File        : FileDownloaderHydra.py

 Date        : 06/06/2022

 Author      : Josh Dixon

 Description : Class to download relative emails from Hydra

 Copyright   : Roundhouse Limited

"""
import base64
import os
import re

def hydraDownload(fileA, filePath):
    fileName = fileA['name']
    # Checks to see if file is a pdf or dxf or swg
    if (re.search(r'\.pdf$', fileName) != None) or (re.search(r'\.dxf$', fileName) != None) or (re.search(r'\.dwg$', fileName) != None) or (re.search(r'\.PDF$', fileName) != None) or (re.search(r'\.DXF$', fileName) != None) or (re.search(r'\.DWG$', fileName) != None):
        f = open(os.path.join(filePath, fileName), 'w+b')
        f.write(base64.b64decode(fileA['contentBytes']))
        f.close()

        revision = "Unknown"
        filenameSplit = fileName.split(".")
        partNumber = filenameSplit[0]
        # Assigning filenameNew, value depending on moreThenOneSheet
        filenameNew = str(partNumber) + " Rev " + str(revision) + "." + filenameSplit[1]

        # Save the file
        newpathFolder = filePath + "\\" + str(partNumber)
        # Create a folder for the part if that folder does not exist
        if not os.path.exists(newpathFolder):
            os.makedirs(newpathFolder)
        # Cut the file to the folder
        if not os.path.exists(newpathFolder + "\\" + filenameNew):
            os.rename(os.path.join(filePath, fileName), (newpathFolder + "\\" + filenameNew))
        else:
            os.remove(os.path.join(filePath, fileName))
        print("File:" + filenameNew + " has been saved")
