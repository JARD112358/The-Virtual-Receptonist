"""

 File        : FileDownloaderTimberwolf.py

 Date        : 08/06/2022

 Author      : Josh Dixon

 Description : Class to download relative emails from Timberwolf

 Copyright   : Roundhouse Limited

"""
import base64
import os
import re

def timberwolfDownload(fileA, filePath):
    fileName = fileA['name']
    filenameNew = ""
    # Checks to see if file is a pdf or dxf or dwg
    if(re.search(r"iss", fileName)==None) or (re.search(r"Iss", fileName)==None):
        exit
    if (re.search(r'\.pdf$', fileName) != None) or (re.search(r'\.dxf$', fileName) != None) or (re.search(r'\.dwg$', fileName) != None) or (re.search(r'\.PDF$', fileName) != None) or (re.search(r'\.DXF$', fileName) != None) or (re.search(r'\.DWG$', fileName) != None):
        ofValue = re.search(r'(\d*)\sof\s(\d*)', fileName).group(1)

        f = open(os.path.join(filePath, fileName), 'w+b')
        f.write(base64.b64decode(fileA['contentBytes']))
        f.close()

        filenameSplit = fileName.split(" ")
        partNumber = filenameSplit[0]
        revision = filenameSplit[2]

        filenameSplit = fileName.split(".")
        if ofValue == None:
            filenameNew = str(partNumber) + " Rev " + str(revision) + "." + filenameSplit[1]
        else:
            filenameNew = str(partNumber) + " Rev " + str(revision) + " " + ofValue + "." + filenameSplit[1]
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