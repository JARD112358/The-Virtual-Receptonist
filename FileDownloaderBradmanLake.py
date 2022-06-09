"""

 File        : FileDownloaderBradmanLake.py

 Date        : 09/05/2022

 Author      : Josh Dixon

 Description : Class to download relative emails from BradmanLake

 Copyright   : Roundhouse Limited

"""
import base64
import os
import re
from zipfile import ZipFile
import pandas as pd
import pdfplumber

def bradmanLakeFileDownload(fileA, filePath, dfRev):
    if dfRev.empty:
        dfRev.append({'Part_Number':"Unknown", 'Revision':"Unknown"}, ignore_index=True)
    fileName = fileA['name']
    # Checks to see if file is a zip
    if re.search(r'\.zip$', fileName) != None:
        # if it's a zip, save it
        f = open(os.path.join(filePath, fileName), 'w+b')
        f.write(base64.b64decode(fileA['contentBytes']))
        f.close()
        fileNameShort = fileName.replace('.zip', "")
        # unzip the folder
        temp = os.path.join(filePath, fileName)
        with ZipFile(temp, 'r') as zipObj:
            zipObj.extractall(os.path.join(filePath + "\\" + fileNameShort))
        # loop through files

        directory = os.path.join(filePath, fileNameShort)
        for filename in os.listdir(directory):
            filenameSplit = filename.split(".")

            rev = "unknown"
            for index, row in dfRev.iterrows():
                if row['Part_Number'] == filenameSplit[0]:
                    rev = row['Revision']

            filenameNew = filenameSplit[0] + " Rev " + str(rev) + "." + filenameSplit[1]
            f = os.path.join(directory, filename)
            # checking if it is a file
            if os.path.isfile(f):
                # remove the extension to creat the folder name
                folderName = f.replace(directory + "\\", "").split(".")
                folderName = folderName[0]
                folderName = folderName.replace(directory + "\\", "").split("_")
                folderName = folderName[0]
                # Save the file
                #for ind in df_Customer_Regex.index:
                    #if df_Customer_Regex['Customer'][ind] == "BRADMAN-LAKE":
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
    elif ((re.search(r'\.pdf$', fileName) != None) or (re.search(r'\.dxf$', fileName) != None)) and (re.search(r'^1PU', fileName) == None):
        fileName = fileA['name']
        f = open(os.path.join(filePath, fileName), 'w+b')
        f.write(base64.b64decode(fileA['contentBytes']))
        f.close()
        fileNameShort = fileName.replace('.dxf', "")
        fileNameShort = fileNameShort.replace('.pdf', "")
        folderName = fileNameShort.split("_")
        folderName = folderName[0]

        # Create a new ame for the file including it's rev
        filenameSplit = fileName.split(".")

        rev = "unknown"
        for index, row in dfRev.iterrows():
            if row['Part_Number'] == filenameSplit[0]:
                rev = row['Revision']

        filenameNew = filenameSplit[0] + " Rev " + str(rev) + "." + filenameSplit[1]


        # Save the file
        newpathFolder = filePath + "\\" + str(folderName)
        # Create the file path if it doesn't already exist
        if not os.path.exists(newpathFolder):
            os.makedirs(newpathFolder)
        # Cut the file to the desired locations
        if not os.path.exists(newpathFolder + "\\" + filenameNew):
            os.rename(os.path.join(filePath, fileName), (newpathFolder + "\\" + filenameNew))
        else:
            os.remove(os.path.join(filePath, fileName))
        # removed the save files that are no longer needed
        #os.remove(os.path.join(filePath, fileName))
        #os.rmdir(os.path.join(filePath, fileNameShort))
        print("File:" + filenameNew + " has been saved")

def revTableCreator(pdfSavedFiled):
    df = pd.DataFrame(columns=['Part_Number', 'Revision'])
    lineCounter = 1
    pdf = pdfplumber.open(pdfSavedFiled)
    for page in pdf.pages:
        for line in page.extract_text().split("\n"):
            partNumber = ""
            partRev = ""
            splitLine = line.split(" ")
            if splitLine[0].isdigit():
                if int(splitLine[0]) == lineCounter:
                    pattern = r"^SC\-\d*"
                    if (re.search(pattern, splitLine[1]) is None):
                        pass
                    else:
                        splitLine[1] = splitLine[1].replace("SC-", "")
                    partNumber = splitLine[1]
                    pattern = r"^(\d*)$|^F(\d*)|(\d*)-(\d*)\w$"
                    if (re.search(pattern, splitLine[1]) is None):
                        pass
                    else:
                        partRev = splitLine[2]
                        lineCounter = lineCounter + 1
                        df = df.append({'Part_Number':partNumber, 'Revision':partRev}, ignore_index=True)
    return df
