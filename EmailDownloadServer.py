"""

 File        : EmailDownloadServer.py

 Date        : 03/03/2022

 Author      : Josh Dixon

 Description : Class to download emails from the Microsoft Server using the api

 Copyright   : Roundhouse Limited

"""

import csv
import re
import pandas as pd
import microsoftGraphConnector


def downloadStartingData():
    # data to create a microsoft GRAPH api GET request
    graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'

    df = pd.read_csv("main/authenticationDetails.csv", header=0)
    emailStringRequest = ""
    for i in range(len(df)):
        if df.loc[i, "Label"] == 'email':
            chosen_email = df.loc[i, "Value"]
            emailStringRequest = '/users/' + str(chosen_email) + '/messages?$top=1000&$select=categories,subject,body'
    request_url = graph_api_endpoint.format(emailStringRequest)
    headers = {
        'User-Agent': 'python_tutorial/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        "Prefer": "outlook.body-content-type='text'"
    }
    i = 0
    count = 3
    messageCategories = []
    messageBody = []
    messageSubject = []

    while i < count:
        response = microsoftGraphConnector.getRequest(request_url, headers)
        if response.ok:
            resposnseJson = response.json()
            request_url = resposnseJson['@odata.nextLink']
            for email in resposnseJson['value']:
                messageCategories.append(email['categories'])
                messageBody.append(email['body'])
                messageSubject.append(email['subject'])
        i = i + 1
    filename = "main/Email_Machine_Learning_Model_Data.csv"

    # Stores the email data into a csv
    i = 0
    count = len(messageBody)
    with open(filename, 'w', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Categories", "Subject", "Body"])
        while i < count:
            patterns = ["\\n", "\\r", '\s+', ]

            messageBodyEdited = messageBody[i]['content']
            for pattern in patterns:
                patternBody = re.sub(pattern, " ", messageBodyEdited)
                patternBody.strip()
                messageBodyEdited = patternBody
            messageCategoryChosen = "Other"
            if len(messageCategories[i]) == 1:
                messageCategoryChosen = messageCategories[i][0]
            writer.writerow([messageCategoryChosen, messageSubject[i], messageBodyEdited])
            i = i + 1


def download():
    # Creates a microsft graph api request
    graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'
    df = pd.read_csv("main/authenticationDetails.csv", header=0)
    emailStringRequest = ""
    for i in range(len(df)):
        if df.loc[i, "Label"] == 'email':
            chosen_email = df.loc[i, "Value"]
            emailStringRequest = '/users/' + str(
                chosen_email) + '/messages?$top=250&$select=id,categories,subject,body,flag,from,bodyPreview'
    request_url = graph_api_endpoint.format(emailStringRequest)
    headers = {
        'User-Agent': 'python_tutorial/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        "Prefer": "outlook.body-content-type='text'"
    }
    i = 0
    count = 1

    messageBody = []
    messageSubject = []
    messageId = []
    messageFlag = []
    messageCategory = []
    messages = []
    while i < count:
        response = microsoftGraphConnector.getRequest(request_url, headers)
        if response.ok:
            resposnseJson = response.json()
            request_url = resposnseJson['@odata.nextLink']
            for email in resposnseJson['value']:
                messages.append(email)
                messageBody.append(email['body']['content'])
                messageSubject.append(email['subject'])
                messageCategory.append(email['categories'])
                messageId.append(email['id'])
                messageFlag.append(email['flag'])
        i = i + 1
    # Use regex to remove useless characters
    patterns = ["\\n", "\\r", '\s+', ]
    # patterns = []
    messageBodyUpdated = []
    for body in messageBody:
        patternBody = body
        for pattern in patterns:
            patternBody = re.sub(pattern, " ", patternBody)
            patternBody.strip()
        messageBodyUpdated.append(patternBody)

    # Load data into a dataframe
    data = {"ID": messageId, "Category": messageCategory, "Subject": messageSubject, "Body": messageBodyUpdated,
            "Flag": messageFlag}
    df = pd.DataFrame(data)
    # Save the dataframe to an email
    df.to_csv('main/Emails_to_Categorise.csv', quoting=csv.QUOTE_NONNUMERIC)
    # outlook.Close()

    return messages
