"""

 File        : Email.py

 Date        : e03/03/2022

 Author      : Josh Dixon

 Description : Class for creating email objects

 Copyright   : Roundhouse Limited

"""


class Email:
    def __init__(self, original_message, original_label, original_subject):
        self.original_message = original_message
        self.original_label = original_label
        self.original_subject = original_subject
        # For numbered label: 0 = NCR, 1 = Quote, 2 = PO, 3 = Other
        # For the remaining labels 0 = False, 1 = True
        if original_label == "NCR / Complaint received":
            self.numbered_label = 0
            self.nCR_label = 1
            self.quote_label = 0
            self.pO_label = 0
        elif original_label == "Quotation requested":
            self.numbered_label = 1
            self.nCR_label = 0
            self.quote_label = 1
            self.pO_label = 0
        elif original_label == "Purchase Order received":
            self.numbered_label = 2
            self.nCR_label = 0
            self.quote_label = 0
            self.pO_label = 1
        else:
            self.numbered_label = 3
            self.nCR_label = 0
            self.quote_label = 0
            self.pO_label = 0
        self.id = None
        self.email_assigned_type = None

    def __str__(self):
        output = str(self.id) + ', ' + self.original_label
        return output
