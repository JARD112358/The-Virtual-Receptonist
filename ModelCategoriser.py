"""

 File        : ModelCategoriser.py

 Date        : 03/03/2022

 Author      : Josh Dixon

 Description : Class for creating requests to the Microsoft Graph API

 Copyright   : Roundhouse Limited

"""

import _io
import json
import random
import Email
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras_preprocessing import text
from keras.utils.np_utils import to_categorical
from keras import models, layers
import numpy as np
from keras import backend as k


# A method to used to vectorise a string
def vectorize_sequences(sequences, dimension=10000):
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.
    return results


# A method to create a model that can give an intial clasification of the email
def initialCategoriser(epochA, epochB):
    # Clears any previous models
    k.clear_session()
    # uploads the email data
    df = pd.read_csv("main/Email_Machine_Learning_Model_Data.csv")
    # processes the email data
    df.dropna(subset=["Categories"], inplace=True)
    # renames all rows to "other" if the email is not one of the three core categories
    df.loc[(df.Categories != "NCR / Complaint received") &
           (df.Categories != "Quotation requested") &
           (df.Categories != "Purchase Order received"), "Categories"] = "Other"

    df = df.reset_index(drop=True)
    df['Body'] = df['Body'].replace('(\s+)', value=" ", regex=True)

    index = df.index
    iN1 = int(len(index) * 0.3)
    iN2 = int((len(index) * 0.3) + (len(index) * 0.5))

    # Loading the dataset
    body = df['Body']
    subject = df['Subject']
    labels = df['Categories']

    # Creating and storing emails
    emailList = []
    i = 0
    while i < len(body):
        emailList.append(Email.Email(body[i], labels[i], subject[i]))
        random.shuffle(emailList)
        i = i + 1

    # Assigning the emails into validation, training and test sets
    random.shuffle(emailList)
    i = 0
    labels_numberedNCR = []
    for email in emailList:
        email.id = i
        if i < iN1:
            email.email_assigned_type = "Validation"
        elif i < iN2:
            email.email_assigned_type = "Training"
        else:
            email.email_assigned_type = "Test"
        i = i + 1

    # Creating the models
    dataG = []
    dataH = []
    labels4 = []
    modelDefintionG = [layers.Dense(32, activation='relu', input_shape=(10000,)),
                       layers.Dense(32, activation='relu'),
                       layers.Dense(32, activation='relu'),
                       layers.Dense(4, activation='softmax')
                       ]
    modelDefintionH = [layers.Dense(32, activation='relu', input_shape=(10000,)),
                       layers.Dense(32, activation='relu'),
                       layers.Dense(4, activation='softmax')
                       ]
    # Convert email labels to numbered values
    labels_numbered4 = []

    for email in emailList:
        dataG.append(email.original_message)
        dataH.append(email.original_subject)
        labels4.append(email.original_label)
        labels_numbered4.append(email.numbered_label)
        labels_numberedNCR.append(email.nCR_label)

    i = 0
    while i < len(dataG):
        dataG[i] = str(dataG[i])
        body[i] = str(body[i])
        i = i + 1

    i = 0
    while i < len(dataH):
        dataH[i] = str(dataH[i])
        i = i + 1

    # tokenize
    tokenizerG = Tokenizer(num_words=10000)
    tokenizerG.fit_on_texts(dataG)
    dataG = tokenizerG.texts_to_sequences(dataG)
    tokenizerG_json = tokenizerG.to_json()
    with _io.open('main/tokenizerG.json', 'w', encoding='utf-8') as g:
        g.write(json.dumps(tokenizerG_json, ensure_ascii=False))

    tokenizerH = Tokenizer(num_words=10000)
    tokenizerH.fit_on_texts(dataH)
    dataH = tokenizerH.texts_to_sequences(dataH)
    tokenizerH_json = tokenizerH.to_json()
    with _io.open('main/tokenizerH.json', 'w', encoding='utf-8') as h:
        h.write(json.dumps(tokenizerH_json, ensure_ascii=False))
    # split data into a training and test set
    train_data7 = dataG[:iN2]
    test_data7 = dataG[iN2:]

    train_data8 = dataH[:iN2]
    test_data8 = dataH[iN2:]

    train_labels4 = labels_numbered4[:iN2]
    test_labels4 = labels_numbered4[iN2:]

    x_train7 = vectorize_sequences(train_data7)
    x_train8 = vectorize_sequences(train_data8)
    x_test7 = vectorize_sequences(test_data7)
    x_test8 = vectorize_sequences(test_data8)

    one_hot_train_labels4 = to_categorical(train_labels4)
    one_hot_test_labels4 = to_categorical(test_labels4)

    # setting aside a validation set
    x_val7 = x_train7[:iN1]
    partial_x_train7 = x_train7[iN1:]
    x_val8 = x_train8[:iN1]
    partial_x_train8 = x_train8[iN1:]

    y_val4 = one_hot_train_labels4[:iN1]
    partial_y_train4 = one_hot_train_labels4[iN1:]

    modelG = models.Sequential()
    for layer in modelDefintionG:
        modelG.add(layer)

    modelH = models.Sequential()
    for layer in modelDefintionH:
        modelH.add(layer)

    modelG.compile(optimizer='rmsprop',
                   loss='categorical_crossentropy',
                   metrics=['accuracy'])
    modelG.fit(partial_x_train7,
               partial_y_train4,
               epochs=epochA,
               batch_size=512,
               validation_data=(x_val7, y_val4))
    results = modelG.evaluate(x_test7, one_hot_test_labels4)

    modelH.compile(optimizer='rmsprop',
                   loss='categorical_crossentropy',
                   metrics=['accuracy'])
    modelH.fit(partial_x_train8,
               partial_y_train4,
               epochs=epochB,
               batch_size=512,
               validation_data=(x_val8, y_val4))
    results = modelH.evaluate(x_test8, one_hot_test_labels4)

    # Code to get a Confusion Matrix
    i = 0
    y_pred7 = modelG.predict(x_test7)
    y_pred8 = modelH.predict(x_test8)

    # Code to get a value depending if the model has predicted the email correctly
    correct_values7 = []
    correct_values8 = []
    y_pred_value7 = np.argmax(y_pred7, axis=1)
    y_pred_value8 = np.argmax(y_pred8, axis=1)
    i = 0
    while i < len(y_pred_value7):
        if y_pred_value7[i] == test_labels4[i]:
            correct_values7.append(1)
        else:
            correct_values7.append(0)
        i = i + 1

    i = 0
    while i < len(y_pred_value8):
        if y_pred_value8[i] == test_labels4[i]:
            correct_values8.append(1)
        else:
            correct_values8.append(0)
        i = i + 1

    # Code to get the difference between the largest and second largest values of certainty
    emailPredictedLabel7 = []
    emailPredictedLabel8 = []
    for email in y_pred7:
        emailPredictedLabel7.append(np.argmax(email))
    for email in y_pred8:
        emailPredictedLabel8.append(np.argmax(email))

    y_pred_sorted7 = y_pred7
    ppoint7 = []
    for values in y_pred_sorted7:
        values.sort()
        ppoint7.append(values[-1] - values[-2])

    y_pred_sorted8 = y_pred8
    ppoint8 = []
    for values in y_pred_sorted8:
        values.sort()
        ppoint8.append(values[-1] - values[-2])

    emailOriginalLabel = []
    emailBodyText = []
    emailSubjectText = []
    for email in emailList:
        if (email.email_assigned_type == "Test"):
            emailOriginalLabel.append(email.numbered_label)
            emailBodyText.append(email.original_message)
            emailSubjectText.append(email.original_subject)
    modelG.save("main/Model G")
    modelH.save("main/Model H")


# A method to create a model that can classify an email as either a ncr or not an ncr
def ncrCategoriser(epochA, epochB):
    df = pd.read_csv("main/Email_Machine_Learning_Model_Data.csv")
    df = df.reset_index(drop=True)
    df['Body'] = df['Body'].replace('<(.|\n)*>(.|\n)*', value="", regex=True)

    # Loading the dataset
    subject = df['Subject']
    body = df['Body']
    labels = df['Categories']

    # Creating and storing emails
    emailList = []
    i = 0
    while i < len(body):
        emailList.append(Email.Email(body[i], labels[i], subject[i]))
        random.shuffle(emailList)
        i = i + 1

    random.shuffle(emailList)
    i = 0
    for email in emailList:
        email.id = i
        if i < 1000:
            email.email_assigned_type = "Validation"
        elif i < 2709:
            email.email_assigned_type = "Training"
        else:
            email.email_assigned_type = "Test"
        i = i + 1

    # Model A
    # Converts email labels to numbered values
    body = []
    labels = []
    labels_numbered = []

    for email in emailList:
        body.append(str(email.original_message))
        labels.append(str(email.original_label))
        labels_numbered.append(email.nCR_label)
    # tokenize
    tokenizer = Tokenizer(num_words=10000)
    tokenizer.fit_on_texts(body)
    body = tokenizer.texts_to_sequences(body)
    tokenizerA_json = tokenizer.to_json()
    with _io.open('main/tokenizerA.json', 'w', encoding='utf-8') as e:
        e.write(json.dumps(tokenizerA_json, ensure_ascii=False))

    # split data into a training and test set
    train_body = body[:2709]
    train_labels = labels_numbered[:2709]

    test_body = body[2709:]
    test_labels = labels_numbered[2709:]

    x_train = vectorize_sequences(train_body)
    x_test = vectorize_sequences(test_body)

    y_train = np.asarray(train_labels).astype('float32')
    y_test = np.asarray(test_labels).astype('float32')

    # model definition
    modelA = models.Sequential()
    modelA.add(layers.Dense(512, activation='relu', input_shape=(10000,)))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(1, activation='sigmoid'))

    # setting aside a validation set
    x_val = x_train[:1000]
    partial_x_train = x_train[1000:]

    y_val = y_train[:1000]
    partial_y_train = y_train[1000:]

    # Training the model
    modelA.compile(optimizer='rmsprop',
                   loss='binary_crossentropy',
                   metrics=['accuracy'])

    modelA.fit(partial_x_train,
               partial_y_train,
               epochs=epochA,
               batch_size=512,
               validation_data=(x_val, y_val))
    results = modelA.evaluate(x_test, y_test)

    # Calculates the predicted value
    y_pred_value = []
    predictions = modelA.predict(x_test)
    for score in predictions:
        if score > 0.5:
            y_pred_value.append(1)
        else:
            y_pred_value.append(0)
    # calculates if the prediction is correct or not
    correct_values = []
    i = 0
    while i < len(y_pred_value):
        if y_pred_value[i] == test_labels[i]:
            correct_values.append(1)
        else:
            correct_values.append(0)
        i = i + 1
    # Model B
    # Store relevant data
    subject = []
    for email in emailList:
        subject.append(email.original_subject)

    # tokenize
    i = 0
    while i < len(subject):
        subject[i] = str(subject[i])
        i = i + 1
    tokenizer2 = Tokenizer(num_words=10000)
    tokenizer2.fit_on_texts(subject)
    subject = tokenizer2.texts_to_sequences(subject)
    tokenizerB_json = tokenizer2.to_json()
    with _io.open('main/tokenizerB.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(tokenizerB_json, ensure_ascii=False))

    # split data into a training and test set
    train_subject = subject[:2709]

    test_subject = subject[2709:]

    x2_train = vectorize_sequences(train_subject)
    x2_test = vectorize_sequences(test_subject)

    # Model Definition
    modelB = models.Sequential()
    modelB.add(layers.Dense(512, activation='relu', input_shape=(10000,)))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(1, activation='sigmoid'))

    # Defining a Validation set
    x2_val = x2_train[:1000]
    partial_x2_train = x2_train[1000:]

    # Training the Model
    modelB.compile(optimizer='rmsprop',
                   loss='binary_crossentropy',
                   metrics=['accuracy'])

    modelB.fit(partial_x2_train,
               partial_y_train,
               epochs=epochB,
               batch_size=512,
               validation_data=(x2_val, y_val))
    results = modelB.evaluate(x2_test, y_test)

    # Calculates the predicted value
    y_pred_value2 = []
    predictions2 = modelB.predict(x2_test)
    for score in predictions2:
        if score > 0.5:
            y_pred_value2.append(1)
        else:
            y_pred_value2.append(0)

    # calculates if the prediction is correct or not
    correct_values2 = []
    i = 0
    while i < len(y_pred_value2):
        if y_pred_value2[i] == test_labels[i]:
            correct_values2.append(1)
        else:
            correct_values2.append(0)
        i = i + 1

    modelA.save("main/Model A")
    modelB.save("main/Model B")

    k.clear_session()


# A method to create a model that can classify an email as either a PO or not a PO
def experimentPO(epochA, epochB):
    df = pd.read_csv("main/Email_Machine_Learning_Model_Data.csv")
    df = df.reset_index(drop=True)
    df['Body'] = df['Body'].replace('<(.|\n)*>(.|\n)*', value="", regex=True)

    # Loading the dataset
    subject = df['Subject']
    body = df['Body']
    labels = df['Categories']

    # Creating and storing emails
    emailList = []
    i = 0
    while i < len(body):
        emailList.append(Email.Email(body[i], labels[i], subject[i]))
        random.shuffle(emailList)
        i = i + 1

    random.shuffle(emailList)
    i = 0
    for email in emailList:
        email.id = i
        if i < 1000:
            email.email_assigned_type = "Validation"
        elif i < 2709:
            email.email_assigned_type = "Training"
        else:
            email.email_assigned_type = "Test"
        i = i + 1

    # Model A
    # Converts email labels to numbered values
    body = []
    labels = []
    labels_numbered = []

    for email in emailList:
        body.append(str(email.original_message))
        labels.append(str(email.original_label))
        labels_numbered.append(email.pO_label)
    # tokenize
    tokenizer = Tokenizer(num_words=10000)
    tokenizer.fit_on_texts(body)
    body = tokenizer.texts_to_sequences(body)
    tokenizerE_json = tokenizer.to_json()
    with _io.open('main/tokenizerE.json', 'w', encoding='utf-8') as e:
        e.write(json.dumps(tokenizerE_json, ensure_ascii=False))

    # split data into a training and test set
    train_body = body[:2709]
    train_labels = labels_numbered[:2709]

    test_body = body[2709:]
    test_labels = labels_numbered[2709:]

    x_train = vectorize_sequences(train_body)
    x_test = vectorize_sequences(test_body)

    y_train = np.asarray(train_labels).astype('float32')
    y_test = np.asarray(test_labels).astype('float32')

    # model definition
    modelA = models.Sequential()
    modelA.add(layers.Dense(512, activation='relu', input_shape=(10000,)))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(1, activation='sigmoid'))

    # setting aside a validation set
    x_val = x_train[:1000]
    partial_x_train = x_train[1000:]

    y_val = y_train[:1000]
    partial_y_train = y_train[1000:]

    # Training the model
    modelA.compile(optimizer='rmsprop',
                   loss='binary_crossentropy',
                   metrics=['accuracy'])

    modelA.fit(partial_x_train,
               partial_y_train,
               epochs=epochA,
               batch_size=512,
               validation_data=(x_val, y_val))
    results = modelA.evaluate(x_test, y_test)

    # Calculates the predicted value
    y_pred_value = []
    predictions = modelA.predict(x_test)
    for score in predictions:
        if score > 0.5:
            y_pred_value.append(1)
        else:
            y_pred_value.append(0)
    # calculates if the prediction is correct or not
    correct_values = []
    i = 0
    while i < len(y_pred_value):
        if y_pred_value[i] == test_labels[i]:
            correct_values.append(1)
        else:
            correct_values.append(0)
        i = i + 1
    # Model B
    # Store relevant data
    subject = []
    for email in emailList:
        subject.append(email.original_subject)

    # tokenize
    i = 0
    while i < len(subject):
        subject[i] = str(subject[i])
        i = i + 1
    tokenizer2 = Tokenizer(num_words=10000)
    tokenizer2.fit_on_texts(subject)
    subject = tokenizer2.texts_to_sequences(subject)
    tokenizerF_json = tokenizer2.to_json()
    with _io.open('main/tokenizerF.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(tokenizerF_json, ensure_ascii=False))

    # split data into a training and test set
    train_subject = subject[:2709]

    test_subject = subject[2709:]

    x2_train = vectorize_sequences(train_subject)
    x2_test = vectorize_sequences(test_subject)

    # Model Definition
    modelB = models.Sequential()
    modelB.add(layers.Dense(512, activation='relu', input_shape=(10000,)))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(1, activation='sigmoid'))

    # Defining a Validation set
    x2_val = x2_train[:1000]
    partial_x2_train = x2_train[1000:]

    # Training the Model
    modelB.compile(optimizer='rmsprop',
                   loss='binary_crossentropy',
                   metrics=['accuracy'])

    modelB.fit(partial_x2_train,
               partial_y_train,
               epochs=epochB,
               batch_size=512,
               validation_data=(x2_val, y_val))
    results = modelB.evaluate(x2_test, y_test)

    # Calculates the predicted value
    y_pred_value2 = []
    predictions2 = modelB.predict(x2_test)
    for score in predictions2:
        if score > 0.5:
            y_pred_value2.append(1)
        else:
            y_pred_value2.append(0)

    # calculates if the prediction is correct or not
    correct_values2 = []
    i = 0
    while i < len(y_pred_value2):
        if y_pred_value2[i] == test_labels[i]:
            correct_values2.append(1)
        else:
            correct_values2.append(0)
        i = i + 1

    modelA.save("main/Model E")
    modelB.save("main/Model F")

    k.clear_session()


# A method to create a model that can classify an email a Quote ot not a quote
def experimentQuote(epochA, epochB):
    df = pd.read_csv("main/Email_Machine_Learning_Model_Data.csv")
    df = df.reset_index(drop=True)
    df['Body'] = df['Body'].replace('<(.|\n)*>(.|\n)*', value="", regex=True)

    # Loading the dataset
    subject = df['Subject']
    body = df['Body']
    labels = df['Categories']

    # Creating and storing emails
    emailList = []
    i = 0
    while i < len(body):
        emailList.append(Email.Email(body[i], labels[i], subject[i]))
        random.shuffle(emailList)
        i = i + 1

    random.shuffle(emailList)
    i = 0
    for email in emailList:
        email.id = i
        if i < 1000:
            email.email_assigned_type = "Validation"
        elif i < 2709:
            email.email_assigned_type = "Training"
        else:
            email.email_assigned_type = "Test"
        i = i + 1

    # Model A
    # Converts email labels to numbered values
    body = []
    labels = []
    labels_numbered = []

    for email in emailList:
        body.append(str(email.original_message))
        labels.append(str(email.original_label))
        labels_numbered.append(email.quote_label)
    # tokenize
    tokenizer = Tokenizer(num_words=10000)
    tokenizer.fit_on_texts(body)
    body = tokenizer.texts_to_sequences(body)
    tokenizerC_json = tokenizer.to_json()
    with _io.open('main/tokenizerC.json', 'w', encoding='utf-8') as c:
        c.write(json.dumps(tokenizerC_json, ensure_ascii=False))

    # split data into a training and test set
    train_body = body[:2709]
    train_labels = labels_numbered[:2709]

    test_body = body[2709:]
    test_labels = labels_numbered[2709:]

    x_train = vectorize_sequences(train_body)
    x_test = vectorize_sequences(test_body)

    y_train = np.asarray(train_labels).astype('float32')
    y_test = np.asarray(test_labels).astype('float32')

    # model definition
    modelA = models.Sequential()
    modelA.add(layers.Dense(512, activation='relu', input_shape=(10000,)))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(512, activation='relu'))
    modelA.add(layers.Dense(1, activation='sigmoid'))

    # setting aside a validation set
    x_val = x_train[:1000]
    partial_x_train = x_train[1000:]

    y_val = y_train[:1000]
    partial_y_train = y_train[1000:]

    # Training the model
    modelA.compile(optimizer='rmsprop',
                   loss='binary_crossentropy',
                   metrics=['accuracy'])

    modelA.fit(partial_x_train,
               partial_y_train,
               epochs=epochA,
               batch_size=512,
               validation_data=(x_val, y_val))
    results = modelA.evaluate(x_test, y_test)

    # Calculates the predicted value
    y_pred_value = []
    predictions = modelA.predict(x_test)
    for score in predictions:
        if score > 0.5:
            y_pred_value.append(1)
        else:
            y_pred_value.append(0)
    # calculates if the prediction is correct or not
    correct_values = []
    i = 0
    while i < len(y_pred_value):
        if y_pred_value[i] == test_labels[i]:
            correct_values.append(1)
        else:
            correct_values.append(0)
        i = i + 1
    # Model B
    # Store relevant data
    subject = []
    for email in emailList:
        subject.append(email.original_subject)

    # tokenize
    i = 0
    while i < len(subject):
        subject[i] = str(subject[i])
        i = i + 1
    tokenizer2 = Tokenizer(num_words=10000)
    tokenizer2.fit_on_texts(subject)
    subject = tokenizer2.texts_to_sequences(subject)
    tokenizerD_json = tokenizer2.to_json()
    with _io.open('main/tokenizerD.json', 'w', encoding='utf-8') as d:
        d.write(json.dumps(tokenizerD_json, ensure_ascii=False))

    # split data into a training and test set
    train_subject = subject[:2709]

    test_subject = subject[2709:]

    x2_train = vectorize_sequences(train_subject)
    x2_test = vectorize_sequences(test_subject)

    # Model Definition
    modelB = models.Sequential()
    modelB.add(layers.Dense(512, activation='relu', input_shape=(10000,)))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(512, activation='relu'))
    modelB.add(layers.Dense(1, activation='sigmoid'))

    # Defining a Validation set
    x2_val = x2_train[:1000]
    partial_x2_train = x2_train[1000:]

    # Training the Model
    modelB.compile(optimizer='rmsprop',
                   loss='binary_crossentropy',
                   metrics=['accuracy'])

    modelB.fit(partial_x2_train,
               partial_y_train,
               epochs=epochB,
               batch_size=512,
               validation_data=(x2_val, y_val))
    results = modelB.evaluate(x2_test, y_test)

    # Calculates the predicted value
    y_pred_value2 = []
    predictions2 = modelB.predict(x2_test)
    for score in predictions2:
        if score > 0.5:
            y_pred_value2.append(1)
        else:
            y_pred_value2.append(0)

    # calculates if the prediction is correct or not
    correct_values2 = []
    i = 0
    while i < len(y_pred_value2):
        if y_pred_value2[i] == test_labels[i]:
            correct_values2.append(1)
        else:
            correct_values2.append(0)
        i = i + 1

    emailOriginalLabel = []
    emailBodyText = []
    emailSubjectText = []
    for email in emailList:
        if (email.email_assigned_type == "Test"):
            emailOriginalLabel.append(email.quote_label)
            emailBodyText.append(email.original_message)
            emailSubjectText.append(email.original_subject)

    modelA.save("main/Model C")
    modelB.save("main/Model D")


# A method that evaluates using all the models to give a final prection
def finalDeciderCategoriser(body, subject):
    modelA = models.load_model("main/Model A")
    modelB = models.load_model("main/Model B")
    modelC = models.load_model("main/Model C")
    modelD = models.load_model("main/Model D")
    modelE = models.load_model("main/Model E")
    modelF = models.load_model("main/Model F")
    modelG = models.load_model("main/Model G")
    modelH = models.load_model("main/Model H")

    bodyList = []
    for b in body:
        bodyList.append(str(b))

    subjectList = []
    for s in subject:
        subjectList.append(str(s))

    with open('main/tokenizerA.json') as a:
        dataA = json.load(a)
        tokenizerA = text.tokenizer_from_json(dataA)

    with open('main/tokenizerB.json') as b:
        dataB = json.load(b)
        tokenizerB = text.tokenizer_from_json(dataB)

    with open('main/tokenizerC.json') as c:
        dataC = json.load(c)
        tokenizerC = text.tokenizer_from_json(dataC)

    with open('main/tokenizerD.json') as d:
        dataD = json.load(d)
        tokenizerD = text.tokenizer_from_json(dataD)

    with open('main/tokenizerE.json') as e:
        dataE = json.load(e)
        tokenizerE = text.tokenizer_from_json(dataE)

    with open('main/tokenizerF.json') as f:
        dataF = json.load(f)
        tokenizerF = text.tokenizer_from_json(dataF)

    with open('main/tokenizerG.json') as g:
        dataG = json.load(g)
        tokenizerG = text.tokenizer_from_json(dataG)

    with open('main/tokenizerH.json') as h:
        dataH = json.load(h)
        tokenizerH = text.tokenizer_from_json(dataH)

    dataA = tokenizerA.texts_to_sequences(bodyList)
    dataB = tokenizerB.texts_to_sequences(subjectList)
    dataC = tokenizerC.texts_to_sequences(bodyList)
    dataD = tokenizerD.texts_to_sequences(subjectList)
    dataE = tokenizerE.texts_to_sequences(bodyList)
    dataF = tokenizerF.texts_to_sequences(subjectList)
    dataG = tokenizerG.texts_to_sequences(bodyList)
    dataH = tokenizerH.texts_to_sequences(subjectList)

    dataA = vectorize_sequences(dataA)
    dataB = vectorize_sequences(dataB)
    dataC = vectorize_sequences(dataC)
    dataD = vectorize_sequences(dataD)
    dataE = vectorize_sequences(dataE)
    dataF = vectorize_sequences(dataF)
    dataG = vectorize_sequences(dataG)
    dataH = vectorize_sequences(dataH)

    predA = modelA.predict(dataA)
    predB = modelB.predict(dataB)
    predC = modelC.predict(dataC)
    predD = modelD.predict(dataD)
    predE = modelE.predict(dataE)
    predF = modelF.predict(dataF)
    predG = modelG.predict(dataG)
    predH = modelH.predict(dataH)

    pred_valueA = []
    for score in predA:
        if score > 0.5:
            pred_valueA.append(1)
        else:
            pred_valueA.append(0)

    pred_valueB = []
    for score in predB:
        if score > 0.5:
            pred_valueB.append(1)
        else:
            pred_valueB.append(0)

    pred_valueC = []
    for score in predC:
        if score > 0.5:
            pred_valueC.append(1)
        else:
            pred_valueC.append(0)

    pred_valueD = []
    for score in predD:
        if score > 0.5:
            pred_valueD.append(1)
        else:
            pred_valueD.append(0)

    pred_valueE = []
    for score in predE:
        if score > 0.5:
            pred_valueE.append(1)
        else:
            pred_valueE.append(0)

    pred_valueF = []
    for score in predF:
        if score > 0.5:
            pred_valueF.append(1)
        else:
            pred_valueF.append(0)

    pred_valueG = []
    for email in predG:
        pred_valueG.append(np.argmax(email))

    pred_valueH = []
    for email in predH:
        pred_valueH.append(np.argmax(email))

    i = 0
    pred_value_Final = []
    while i < len(pred_valueG):
        if pred_valueG[i] == 0 and pred_valueH[i] == 0:
            if pred_valueB[i] == 1:
                pred_value_Final.append(0)
            else:
                pred_value_Final.append(3)
        elif pred_valueG[i] == 1 and pred_valueH[i] == 1:
            if pred_valueC[i] == 1 or pred_valueD[i] == 1:
                pred_value_Final.append(1)
            else:
                pred_value_Final.append(3)
        elif pred_valueG[i] == 2 and pred_valueH[i] == 2:
            if pred_valueE[i] == 1 or pred_valueF[i] == 1:
                pred_value_Final.append(2)
            else:
                pred_value_Final.append(3)
        else:
            if pred_valueA[i] == 1 and pred_valueB[i] == 1:
                pred_value_Final.append(0)
            elif pred_valueC[i] == 1 and pred_valueD[i] == 1:
                pred_value_Final.append(1)
            elif pred_valueE[i] == 1 and pred_valueF[i] == 1:
                pred_value_Final.append(2)
            else:
                pred_value_Final.append(3)
        i = i + 1

    return pred_value_Final
