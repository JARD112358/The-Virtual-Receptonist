"""

 File        : FileDownloaderBradmanLake.py

 Date        : 30/05/2022

 Author      : Josh Dixon

 Description : Class to download relative email attachments from Adande

 Copyright   : Roundhouse Limited

"""
import base64
import os
import re
from zipfile import ZipFile
import pandas as pd
import pdfplumber

def adandeFileDownload(fileA, filePath):
    fileName = fileA['name']
    # Checks to see if file is a zip
    if re.search(r'\.zip$', fileName) != None:
        # if it's a zip, save it
        f = open(os.path.join(filePath, fileName), 'w+b')
        f.write(base64.b64decode(fileA['contentBytes']))
        f.close()
        fileNameShort = fileName.replace('.zip', "ZIP")
        # unzip the folder
        temp = os.path.join(filePath, fileName)
        with ZipFile(temp, 'r') as zipObj:
            zipObj.extractall(os.path.join(filePath + "\\" + fileNameShort))
        # loop through files
        directory = os.path.join(filePath, fileNameShort)
        for filename in os.listdir(directory):
            filenameSplit = filename.split(".")
            filenameShort = re.search(r"(\d*)-(\d*)", filenameSplit[0])
            filenameExtension = filenameSplit[1]
            filenameSplit = filenameShort.group(0).split("-")
            rev = filenameSplit[1]

            filenameNew = filenameSplit[0] + " Rev " + str(rev) + "." + filenameExtension
            f = os.path.join(directory, filename)
            # checking if it is a file
            if os.path.isfile(f):
                # remove the extension to creat the folder name
                folderName = filenameSplit[0]
                # Save the file
                newpathFolder = filePath + "\\" + str(folderName)
                # Create the file path if it doesn't already exist
                if not os.path.exists(newpathFolder):
                    os.makedirs(newpathFolder)
                # Cut the file to the desired locations
                if not os.path.exists(newpathFolder + "\\" + filenameNew):
                    os.rename(os.path.join(directory, filename), newpathFolder + "\\" + filenameNew)
                else:
                    os.remove(os.path.join(directory, filename))
        # removed the save files that are no longer needed
        os.remove(os.path.join(filePath, fileName))
        os.rmdir(os.path.join(filePath, fileNameShort))
        print("All the Files have been saved for: " + str(fileName))
