#  Copyright (c) 2019. This script has been written by Ch1r0n (Sergio Conti Rossini) All rights reserved.
#  All the rights for the libraries used in the script are reserved to their creators.

# libpff is needed, if you don't have it installed then you can install it by running "pip install libpff-python"

import sys
import pypff
import operator
import re


def openPST():
    pstfile = pypff.file()

    # Check that the pst file path was provided otherwise exit

    if len(sys.argv) != 2:
        print("101 Please enter the path of the file you want to analyze!")
        exit(1)
    else:
        try:
            pstfile.open(sys.argv[1])

        except OSError:
            print("102 An error has occurred while trying to open the file, exiting...")
            exit(1)

    return pstfile


def parseFolders(pstfile):
    root_folder = pstfile.get_root_folder()
    folders = []

    # @folder: is the array which will contain all 1st and 2nd level folders (more is not planned)

    for folder in range(0, root_folder.get_number_of_sub_folders()):
        folders.append(root_folder.get_sub_folder(folder))
        for subfolder in range(0, root_folder.get_sub_folder(folder).get_number_of_sub_folders()):
            folders.append(root_folder.get_sub_folder(folder).get_sub_folder(subfolder))

    return folders


def parseSentItems(folders):
    # Let's check if we're lucky, there should be a sent items folder to calculate statistics on the 'sent from' field
    for folder in range(0, len(folders)):
        # print('Parsing for Sent Items:' + folders[folder].get_name())
        if (folders[folder].get_name() == "Posta inviata") or (folders[folder].get_name() == "Posta Inviata") \
                or (folders[folder].get_name() == "Sent items") or (folders[folder].get_name() == "Sent Items") \
                or (folders[folder].get_name() == "Gesendete Elemente") or (
                folders[folder].get_name() == "Messages envoyés"):
            return folders[folder]


def parseReceivedItems(folders):
    # If we weren't lucky, well... let's try to do the inverse with the inbox and the 'recipient' field

    for folder in range(0, len(folders)):
        # print('Parsing for inbox:' + folders[folder].get_name())
        if (folders[folder].get_name() == "Posta in arrivo") or (folders[folder].get_name() == "Inbox") or \
                (folders[folder].get_name() == "Inbox") \
                or (folders[folder].get_name() == "Boîte de réception") or (
                folders[folder].get_name() == "Posteingang"):
            return folders[folder]


def lookForSender(sentItems):
    global processedSentItems
    for message in range(0, sentItems.get_number_of_sub_messages()):
        if sentItems.get_sub_message(message).get_sender_name() in senders:
            senders[sentItems.get_sub_message(message).get_sender_name()] = \
                senders[sentItems.get_sub_message(message).get_sender_name()] + 1
        else:
            senders[sentItems.get_sub_message(message).get_sender_name()] = 1

        processedSentItems = processedSentItems + 1
    for folder in range(0, sentItems.get_number_of_sub_folders()):
        lookForSender(sentItems.get_sub_folder(folder))


def getMaxSender(senders):
    # Old code debugging printing from where the data comes from
    # print('Data from sent Emails, User: ', max(senders.items(), key=operator.itemgetter(1))[0],\
    # 'Percentage: ' max(senders.items(), key=operator.itemgetter(1))[1]\
    # / sentItems.get_number_of_sub_messages() * 100, '%')
    if processedSentItems != 0:
        print(max(senders.items(), key=operator.itemgetter(1))[0], '-',
              max(senders.items(), key=operator.itemgetter(1))[1] / processedSentItems * 100, '%')
    else:
        print(max(senders.items(), key=operator.itemgetter(1))[0])


def lookForRecipient(receivedItems):
    global processedReceivedItems
    for message in range(0, receivedItems.get_number_of_sub_messages()):
        users = getRecipient(receivedItems.get_sub_message(message))
        for user in range(0, len(users)):
            actualUser = users[user]
            if actualUser in recipients:
                recipients[actualUser] = recipients[actualUser] + 1
            else:
                recipients[actualUser] = 1
        processedReceivedItems = processedReceivedItems + 1
    for folder in range(0, receivedItems.get_number_of_sub_folders()):
        lookForRecipient(receivedItems.get_sub_folder(folder))


def getRecipient(message):
    try:
        to = re.findall("^To: \S*.*\d*@\S+.+\S+", message.transport_headers, re.MULTILINE)
        for recipient in range(0, len(to)):
            to[recipient] = to[recipient].strip("To: ").strip("<").strip(">").strip(" ").strip("\"").strip(" <")
        return to
    except TypeError:
        return []


def getMaxRecipient(recipients):
    # Old code debugging printing from where the data comes from
    # print('Data from received Emails, User:', max(recipients.items(), key=operator.itemgetter(1))[0])\
    # , max(recipients.items(), key=operator.itemgetter(1))[0])
    if len(recipients) > 0:
        maxRecipient = (max(recipients.items(), key=operator.itemgetter(1))[0]).split("<")
        if processedReceivedItems > 0:
            print(maxRecipient[len(maxRecipient) - 1],
                  max(recipients.items(), key=operator.itemgetter(1))[1] / processedReceivedItems * 100, '%')
        else:
            print(maxRecipient[len(maxRecipient) - 1])
    else:
        print("104 Error analyzing Received Items")


# End of function definitions
# Script starts here! :-)

pstfile = openPST()
folders = parseFolders(pstfile)

# Normal run, try to work just with the sent Emails
try:
    processedSentItems = 0
    senders = dict()
    sentItems = parseSentItems(folders)
    lookForSender(sentItems)
    getMaxSender(senders)
except (AttributeError, ValueError):
    print("103 Error analyzing Sent Items")
# If it goes wrong then try with the inbox Items
try:
    processedReceivedItems = 0
    recipients = dict()
    receivedItems = parseReceivedItems(folders)
    lookForRecipient(receivedItems)
    getMaxRecipient(recipients)

    # If it happens again, then there were no folder we could analyze
except (AttributeError, ValueError):
    print("104 Error analyzing Received Items")
# !!! Very important never forget to close the file!
pstfile.close()
