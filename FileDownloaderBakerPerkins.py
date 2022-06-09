"""

 File        : FileDownloaderBakerPerkins.py

 Date        : 09/05/2022

 Author      : Josh Dixon

 Description : Class to download relative emails from Baker Perkins

 Copyright   : Roundhouse Limited

"""
import base64
import os
import re

def bakerPerkinsDownload(fileA, filePath):
    fileName = fileA['name']
    moreThenOneSheet = False
    # Checks to see if file is a pdf or dxf
    if (re.search(r'\.pdf$', fileName) != None) or (re.search(r'\.dxf$', fileName) != None):
        f = open(os.path.join(filePath, fileName), 'w+b')
        f.write(base64.b64decode(fileA['contentBytes']))
        f.close()
        # check to see if it should be more then one sheet
        sheetNumber = re.search(r"SH(\d*)", fileName)
        if sheetNumber != None:
            # if more then one sheet set moreThenOnSheet true and extract the sheet number
            moreThenOneSheet = True
            sheetNumber = sheetNumber.group(0)
            sheetNumber = sheetNumber[2:]
            if sheetNumber.isdigit():
                sheetNumber = int(sheetNumber)
        # Check to see if it contains an underscore
        fileNameSplit = ""
        partNumber = ""
        revision = "Unknown"
        # Locate the partnumber and revision
        if re.search(r"_", fileName) != None:
            # if it does set partNumber and revision
            fileNameSplit = fileName.split("_")
            partNumber = fileNameSplit[0]
            revision = fileNameSplit[1]
        else:
            fileNameSplit = fileName.split(".")
            fileNameSplit = fileNameSplit[0].split(" ")
            partNumber = fileNameSplit[0]
            # else set revision to unknown
        # Create a new ame for the file including it's rev
        filenameSplit = fileName.split(".")

        # Assigning filenameNew, value depending on moreThenOneSheet
        if moreThenOneSheet == False:
            filenameNew = partNumber + " Rev " + str(revision) + "." + filenameSplit[1]
        else:
            filenameNew = str(partNumber) + " Rev " + str(revision) + " Sheet " + str(sheetNumber) + "." + filenameSplit[1]

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
