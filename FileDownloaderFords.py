"""

 File        : FileDownloaderFords.py

 Date        : 06/06/2022

 Author      : Josh Dixon

 Description : Class to download relative emails from Fords

 Copyright   : Roundhouse Limited

"""
import base64
import os
import re

def fordsDownload(fileA, filePath, drawingList):
    fileName = fileA['name']
    # Checks to see if file is a pdf or dxf or swg
    if (re.search(r'\.pdf$', fileName) != None) or (re.search(r'\.dxf$', fileName) != None) or (re.search(r'\.dwg$', fileName) != None):
        f = open(os.path.join(filePath, fileName), 'w+b')
        f.write(base64.b64decode(fileA['contentBytes']))
        f.close()

        for name in drawingList:
            if re.search(name , fileName) != None:
                fileNameSplit = ""
                partNumber = name
                revision = "Unknown"
                # Locate the partnumber and revision
                if re.search(r"-", fileName) != None:
                    # if it does set partNumber and revision
                    fileNameSplit = fileName.split("-")
                    partNumber = fileNameSplit[0]
                    revision = fileNameSplit[1]
                    # else set revision to unknown
                # Create a new name for the file including it's rev
                filenameSplit = fileName.split(".")
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

def partNumbersReturn(attachments):
    returnList = []
    for attachment in attachments:
        attachmentName = attachment['name']
        if re.search ("DRAWING", attachmentName, ) != None:
            attachmentNameSplit = attachmentName.split("-")
            returnList.append(attachmentNameSplit[0])
    return returnList
