"""

 File        : microsoftGraphConnector.py

 Date        : 03/03/2022

 Author      : Josh Dixon

 Description : Class for creating requests to the Microsoft Graph API

 Copyright   : Roundhouse Limited

"""
import json
import adal
import requests
import pandas as pd


# Method to send a GET request to the microsoft GRAPH api
def getRequest(request_url, headersToAdd):
    # store this information on a csv so it can be updated
    df = pd.read_csv("main/authenticationDetails.csv", header=0)
    for i in range(len(df)):
        if df.loc[i, "Label"] == 'tenant':
            tenant = df.loc[i, "Value"]
        elif df.loc[i, "Label"] == 'client_id':
            client_id = df.loc[i, "Value"]
        elif df.loc[i, "Label"] == 'client_secret':
            client_secret = df.loc[i, "Value"]
    # tenant = "3d4hy4.onmicrosoft.com"
    # tenant = "3d4hy4.onmicrosoft.com"
    # client_id = "81c248d9-655d-4916-8441-92a13fd47d5e"
    # client_secret = "JG57Q~cbRNNj1Wu3JCIM7OMOIHB_ghWyX3fCT"

    authority = "https://login.microsoftonline.com/" + tenant
    RESOURCE = "https://graph.microsoft.com"

    context = adal.AuthenticationContext(authority)

    token = context.acquire_token_with_client_credentials(
        RESOURCE,
        client_id,
        client_secret
    )
    headers = {
        'Authorization': 'Bearer {0}'.format(token["accessToken"]),
    }
    for key, value in headersToAdd.items():
        headers[key] = value

    response = requests.get(url=request_url, headers=headers)
    return response


# Method to send a PATCH request to the microsoft GRAPH api
def patchRequest(request_url, headersToAdd, body):
    df = pd.read_csv("main/authenticationDetails.csv", header=0)
    for i in range(len(df)):
        if df.loc[i, "Label"] == 'tenant':
            tenant = df.loc[i, "Value"]
        elif df.loc[i, "Label"] == 'client_id':
            client_id = df.loc[i, "Value"]
        elif df.loc[i, "Label"] == 'client_secret':
            client_secret = df.loc[i, "Value"]

    authority = "https://login.microsoftonline.com/" + tenant
    RESOURCE = "https://graph.microsoft.com"

    context = adal.AuthenticationContext(authority)

    token = context.acquire_token_with_client_credentials(
        RESOURCE,
        client_id,
        client_secret
    )
    headers = {
        'Authorization': 'Bearer {0}'.format(token["accessToken"]),
    }
    for key, value in headersToAdd.items():
        headers[key] = value

    response = requests.patch(url=request_url, headers=headers, data=json.dumps(body))
    return response
