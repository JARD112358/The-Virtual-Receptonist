import inboxSortingMethods as ism
import FileDownloaderBradmanLake as FLBL
import base64
import json
import os
import pandas as pd
import re
import microsoftGraphConnector
import testEnvironment as TE


"""FLBL.revTableCreator('C:\\Users\josha\PycharmProjects\The Virtual Receptonist\\1PU221654.pdf')
FLBL.revTableCreator('C:\\Users\josha\PycharmProjects\The Virtual Receptonist\\1PU221655.pdf')
FLBL.revTableCreator('C:\\Users\josha\PycharmProjects\The Virtual Receptonist\\1PU221685.pdf')
FLBL.revTableCreator('C:\\Users\josha\PycharmProjects\The Virtual Receptonist\\1PU221710.pdf')
FLBL.revTableCreator('C:\\Users\josha\PycharmProjects\The Virtual Receptonist\\1PU221727.pdf')
FLBL.revTableCreator('C:\\Users\josha\PycharmProjects\The Virtual Receptonist\\1PU221764.pdf')
FLBL.revTableCreator('C:\\Users\josha\PycharmProjects\The Virtual Receptonist\\1PU221764.pdf')"""
ism.emailCategoriser()

"""
graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'
df = pd.read_csv("main/authenticationDetails.csv", header=0)
emailStringRequest = ""
for i in range(len(df)):
    if df.loc[i, "Label"] == 'email':
        chosen_email = df.loc[i, "Value"]
        #emailStringRequest = '/users/josh.dixon@roundhouselimited.co.uk/messages/AAMkAGZiYTViZjliLWQ3YjYtNDAxNi04NWY2LWFhNzE0NDViN2U1NwBGAAAAAACKX78gyIsiRo54bOADxY5tBwCqI-Hv0hi4Q7QivypfGGiwAAAAAAEMAACqI-Hv0hi4Q7QivypfGGiwAADRbtg2AAA=/attachments'
        #"AAMkAGZiYTViZjliLWQ3YjYtNDAxNi04NWY2LWFhNzE0NDViN2U1NwBGAAAAAACKX78gyIsiRo54bOADxY5tBwCqI-Hv0hi4Q7QivypfGGiwAAAAAAEMAACqI-Hv0hi4Q7QivypfGGiwAADWOG52AAA="
        #emailStringRequest = '/users/josh.dixon@roundhouselimited.co.uk/messages/AAMkAGZiYTViZjliLWQ3YjYtNDAxNi04NWY2LWFhNzE0NDViN2U1NwBGAAAAAACKX78gyIsiRo54bOADxY5tBwCqI-Hv0hi4Q7QivypfGGiwAAAAAAEMAACqI-Hv0hi4Q7QivypfGGiwAADWOG52AAA=/attachments'

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
    FLBL.bradmanLakeFileDownload(attachment, "K:\\Customer Drawings\\BRADMAN LAKE")
"""