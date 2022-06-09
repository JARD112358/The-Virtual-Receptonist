"""

 File        : inboxSortingMethods.py

 Date        : 03/03/2022

 Author      : Josh Dixon

 Description : Class to process the method of categorising the emails

 Copyright   : Roundhouse Limited

"""
import base64
import json
import pandas
import os
import ModelCategoriser as mc
import EmailDownloadServer
import pandas as pd
import re
import microsoftGraphConnector

import FileDownloaderAdande as fda
import FileDownloaderBakerPerkins as fdbp
import FileDownloaderBradmanLake as fdbl
import FileDownloaderFords as fdf
import FileDownloaderHarrod as fdh
import FileDownloaderHydra as fdHydra
import FileDownloaderPharos as fdPharos
import FileDownloaderTimberwolf as fdt

def emailCategoriser():
    # Download the starting data for the
    EmailDownloadServer.downloadStartingData()
    messages = EmailDownloadServer.download()
    print("Email Data is ready to be recognised ")

    # Load the data into the program
    df = pd.read_csv("main/Emails_to_Categorise.csv")
    body = df['Body'].replace('(\s+)', value=" ", regex=True)
    subject = df['Subject']

    # Create the machine Learning Models
    # mc.initialCategoriser(7, 25)
    # mc.ncrCategoriser(8, 12)
    # mc.experimentQuote(5, 4)
    # mc.experimentPO(4, 4)
    print("Models are completed")

    # Categorises the emails
    predictions = mc.finalDeciderCategoriser(body, subject)
    print("Predictions are completed")
    i = len(messages)
    # stores the flag data for the emails
    followUpFlags = []
    for message in messages:
        followUpFlags.append(message['flag'])

    # load the CustomerRegex.csv into a df
    df_Customer_Regex = pandas.read_csv("main/CustomerRegex.csv")
    # loop through the emails
    while i > 0:
        message = messages[(i - 1)]
        prediction = predictions[i - 1]
        followUpFlag = followUpFlags[i - 1]
        if prediction == 0 and followUpFlag['flagStatus'] == 'notFlagged':
            # Categorise the email as a NCR and flags it
            graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'
            df = pd.read_csv("main/authenticationDetails.csv", header=0)
            emailStringRequest = ""
            for j in range(len(df)):
                if df.loc[j, "Label"] == 'email':
                    chosen_email = df.loc[j, "Value"]
                    emailStringRequest = '/users/' + str(chosen_email) + '/messages/'
            request_url_string = emailStringRequest + message['id']
            request_url = graph_api_endpoint.format(request_url_string)
            followUpFlag.update({'flagStatus': 'flagged'})
            bodyData = {"categories": ["NCR / Complaint received"], "flag": followUpFlag}
            headers = {'User-Agent': 'python_tutorial/1.0',
                       'Accept': 'application/json',
                       'Content-Type': 'application/json'}

            # Only run this code to categorise all emails
            x = microsoftGraphConnector.patchRequest(request_url, headers, bodyData)
        elif (prediction == 1 and followUpFlag['flagStatus'] == 'notFlagged'):
            # Categorise the email as a Quote and flags it
            graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'
            df = pd.read_csv("main/authenticationDetails.csv", header=0)
            emailStringRequest = ""
            for j in range(len(df)):
                if df.loc[j, "Label"] == 'email':
                    chosen_email = df.loc[j, "Value"]
                    emailStringRequest = '/users/' + str(chosen_email) + '/messages/'
            request_url_string = emailStringRequest + message['id']
            request_url = graph_api_endpoint.format(request_url_string)
            followUpFlag.update({'flagStatus': 'flagged'})
            bodyData = {"categories": ["Quotation requested"], "flag": followUpFlag}
            headers = {'User-Agent': 'python_tutorial/1.0',
                       'Accept': 'application/json',
                       'Content-Type': 'application/json'}
            # Only run this code to categorise all emails
            x = microsoftGraphConnector.patchRequest(request_url, headers, bodyData)
            # check if the subject of the email stars with Fw:
            emailAddress = "No email address was found"
            if re.search(r"^Fw:", message['subject']):
                for ind in df_Customer_Regex.index:
                # if it does, loop through customer regex and compare to body preview
                    if  re.search(df_Customer_Regex['EmailRegex'][ind], message['bodyPreview']) != None:
                        #if a match is found set email to that email address
                        emailAddress = re.search(df_Customer_Regex['EmailRegex'][ind], message['bodyPreview']).group(0)
                        break
                    elif re.search(df_Customer_Regex['EmailRegex'][ind], message['body']['content']) != None:
                        #if a match is found set email to that email address
                        emailAddress = re.search(df_Customer_Regex['EmailRegex'][ind], message['body']['content']).group(0)
                        break
            else:
                #otherise set emailAddress to email address
                emailAddress = message['from']['emailAddress']['address']
            x = microsoftGraphConnector.patchRequest(request_url, headers, bodyData)
            for ind in df_Customer_Regex.index:
                if re.search(r'(.*)@adande\.com$', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "ADANDE":
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "adande")
                elif re.search(r'(.*)@bakerperkins\.com$', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "BAKER PERKINS":
                    # Processes the Purchase Order
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "bakerperkins")
                elif re.search(r'(.*)@bradmanlake.com$', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "BRADMAN-LAKE":
                    # Processes the Purchase Order
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "bradmanlake")
                elif re.search(r'(.*)@fordsps.com$', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "FORDS":
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "fords")
                elif re.search(r'(.*)@harrod\.uk\.com', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "HARROD":
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "harrod")
                elif re.search(r'(.*)@nov\.com', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "HYDRA RIG":
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "hydra")
                elif re.search(r'(.*)@pharosmarine\.com', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "PHAROS":
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "pharos")
                elif re.search(r'(.*)@timberwolf-uk\.com', emailAddress) != None and df_Customer_Regex['Customer'][ind] == "TIMBERWOLF":
                    attachmentQuoteSaver(message, df_Customer_Regex['DrawingFileLocation'][ind], "timberwolf")
        elif prediction == 2 and followUpFlag['flagStatus'] == 'notFlagged':

            # Categorise the email as a PO and flags it
            graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'
            df = pd.read_csv("main/authenticationDetails.csv", header=0)
            emailStringRequest = ""
            for j in range(len(df)):
                if df.loc[j, "Label"] == 'email':
                    chosen_email = df.loc[j, "Value"]
                    emailStringRequest = '/users/' + str(chosen_email) + '/messages/'
            request_url_string = emailStringRequest + message['id']
            request_url = graph_api_endpoint.format(request_url_string)
            followUpFlag.update({'flagStatus': 'flagged'})
            bodyData = {"categories": ["Purchase Order received"], "flag": followUpFlag}
            headers = {'User-Agent': 'python_tutorial/1.0',
                       'Accept': 'application/json',
                       'Content-Type': 'application/json'}

            # Only run this code to categorise all emails
            x = microsoftGraphConnector.patchRequest(request_url, headers, bodyData)

            # Checks to see if the customer is available for processing
            emailAddress = message['from']['emailAddress']['address']
            for ind in df_Customer_Regex.index:
                pattern = r"" + df_Customer_Regex['EmailRegex'][ind] + r""
                if re.search(pattern, emailAddress) != None:
                    # Processes the Purchase Order
                    x = microsoftGraphConnector.patchRequest(request_url, headers, bodyData)
                    # if message['attachments'] != None:
                    """attachmentPOSaver(message, df_Customer_Regex['PORegex'][ind],
                                          df_Customer_Regex['POFileLocationCustomer'][ind],
                                          df_Customer_Regex['POFileLocationReader'][ind])"""
        i = i - 1
    print("Emails have been sorted")

def attachmentQuoteSaver(message, quoteFileLocationCustomer, customer):
    graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'
    df = pd.read_csv("main/authenticationDetails.csv", header=0)
    df_Customer_Regex = pandas.read_csv("main/CustomerRegex.csv")
    emailStringRequest = ""
    chosen_email = ""
    #
    for i in range(len(df)):
        if df.loc[i, "Label"] == 'email':
            chosen_email = df.loc[i, "Value"]
            emailStringRequest = '/users/' + str(chosen_email) + '/messages/' + message['id']
    request_url = graph_api_endpoint.format(emailStringRequest)
    headers = {
        'User-Agent': 'python_tutorial/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        "Prefer": "outlook.body-content-type='text'"
    }
    response = microsoftGraphConnector.getRequest(request_url, headers)
    if response.ok:
        resposnseJson = response.json()
    #Check if the email has attachments aand retreieve them
    if resposnseJson["hasAttachments"] == True:
        emailStringRequest = '/users/' + str(chosen_email) + '/messages/' + message['id'] + '/attachments'
        request_url = graph_api_endpoint.format(emailStringRequest)
        response = microsoftGraphConnector.getRequest(request_url, headers)
    else:
        exit()
    jsonData = json.loads(response.content)

    #download the file
    if customer == "adande":
        # Save each attachment
        for attachment in jsonData['value']:
            # for testing only.
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            attachmentName = attachment['name']
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fda.adandeFileDownload(attachment, quoteFileLocationCustomer)
    elif customer == "bakerperkins":
        # Save each attachment
        for attachment in jsonData['value']:
            # for testing only.
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            attachmentName = attachment['name']
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fdbp.bakerPerkinsDownload(attachment, quoteFileLocationCustomer)
    elif customer == "bradmanlake":
        #Create a dataframe of the rev number of the part
        df = pd.DataFrame(columns=['Part_Number', 'Revision'])
        boolAttachedQuote = False
        for attachment in jsonData['value']:
            attachmentName = attachment['name']
            pattern = r'^1PU(.*)\.pdf$'
            if (re.search(pattern, attachmentName) is None):
                pass
            else:
                emailAddress = message['from']['emailAddress']['address']
                pattern = r"(.*)@bradmanlake\.com"
                if re.search(pattern, emailAddress) != None:
                    for index, row in df_Customer_Regex.iterrows():
                        if row['Customer'] == "BRADMAN-LAKE":
                            quoteFileLocation = row['QuoteFileLocation']
                            quoteFileLocation = "C:\\\\Users\josha\PycharmProjects\The Virtual Receptonist\Test Storage"
                            f = open(os.path.abspath(quoteFileLocation + attachmentName), 'w+b')
                            f.write(base64.b64decode(attachment['contentBytes']))
                            f.close()
                            df = fdbl.revTableCreator(quoteFileLocation + attachmentName)
        #Save each attachment
        for attachment in jsonData['value']:
            #for tetsing only
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fdbl.bradmanLakeFileDownload(attachment, quoteFileLocationCustomer, df)
    elif customer == "fords":
        attachmentDrawingList = fdf.partNumbersReturn(jsonData['value'])
        for attachment in jsonData['value']:
            # for testing only.
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            attachmentName = attachment['name']
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fdf.fordsDownload(attachment, quoteFileLocationCustomer, attachmentDrawingList)
    elif customer == "harrod":
        for attachment in jsonData['value']:
            # for testing only.
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            attachmentName = attachment['name']
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fdh.harrodDownload(attachment, quoteFileLocationCustomer)
    elif customer == "hydra":
        for attachment in jsonData['value']:
            # for testing only.
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            attachmentName = attachment['name']
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fdHydra.hydraDownload(attachment, quoteFileLocationCustomer)
    elif customer == "pharos":
        for attachment in jsonData['value']:
            # for testing only.
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            attachmentName = attachment['name']
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fdPharos.pharosDownload(attachment, quoteFileLocationCustomer)
    elif customer == "timberwolf":
        for attachment in jsonData['value']:
            print(attachment['name'])
            # for testing only.
            quoteFileLocationCustomer = "C:\\\\Users\\josha\\PycharmProjects\\The Virtual Receptonist\\Test Storage"
            attachmentName = attachment['name']
            f = open(os.path.abspath(quoteFileLocationCustomer + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            fdt.timberwolfDownload(attachment, quoteFileLocationCustomer)
def attachmentPOSaver(message, poRegex, poFileLocationCustomer, poFileLocationReader):
    graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'

    df = pd.read_csv("main/authenticationDetails.csv", header=0)
    emailStringRequest = ""
    for j in range(len(df)):
        if df.loc[j, "Label"] == 'email':
            chosen_email = df.loc[j, "Value"]
            emailStringRequest = '/users/' + str(chosen_email) + '/messages/' + message['id'] + "/attachments"
    request_url = graph_api_endpoint.format(emailStringRequest)
    headers = {
        'User-Agent': 'python_tutorial/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        "Prefer": "outlook.body-content-type='text'"
    }
    response = microsoftGraphConnector.getRequest(request_url, headers)
    # Download PO Twice (Once for the file reader and once for customer facing file location)
    jsonData = json.loads(response.content)
    for attachment in jsonData['value']:
        pattern = r"" + poRegex + r""
        attachmentName = attachment['name']
        if (re.search(pattern, attachmentName) is None):
            pass
        else:
            f = open(os.path.abspath(poFileLocationReader + attachmentName), 'w+b')
            f.write(base64.b64decode(attachment['contentBytes']))
            f.close()
            f2 = open(os.path.abspath(poFileLocationCustomer + attachmentName), 'w+b')
            f2.write(base64.b64decode(attachment['contentBytes']))
            f2.close()
            # input("prompt: ")
