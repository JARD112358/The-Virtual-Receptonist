"""

 File        : Email.py

 Date        : 28/04/2022

 Author      : Josh Dixon

 Description : Class to write out a csv for you

 Copyright   : Roundhouse Limited

"""

import csv
import pandas as pd

with open('FileReaderList', 'w', encoding='UTF-8') as f:
    data = [["Timberwolf", r'(.*)@timberwolf-uk.com']]
    df = pd.DataFrame(data, columns=['Company', 'Regex'])
    df.to_csv('main/EmailRegex.csv', quoting=csv.QUOTE_NONNUMERIC)
