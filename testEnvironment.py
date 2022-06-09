import re
import pdfplumber
import pandas as pd


def test(pdfSavedFiled):
    df = pd.DataFrame(columns=['Part_Number', 'Revision'])
    lineCounter = 1
    pdf = pdfplumber.open(pdfSavedFiled)
    for page in pdf.pages:
        for line in page.extract_text().split("\n"):
            partNumber = ""
            partRev = ""
            splitLine = line.split(" ")
            try:
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
                        #print("Line Counter: " + str(lineCounter) + ", Part Number : " + str(partNumber) +", Part Rev: " + str(partRev))
                        lineCounter = lineCounter + 1
                        df = df.append({'Part_Number':partNumber, 'Revision':partRev}, ignore_index=True)
            except:
                pass
    return df
