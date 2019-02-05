#  Copyright (c) 2019. This script has been written by Ch1r0n (Sergio Conti Rossini) All rights reserved.
#  All the rights for the libraries used in the script are reserved to their creators.

# libpff is needed, if you don't have it installed then you can install it by running "pip install libpff-python"

import sys
import pypff
import operator
import re
from email.utils import parseaddr


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

    # @folder: is the array which will contain all 1st and 2nd level folders

    for folder in range(0, root_folder.get_number_of_sub_folders()):
        folders.append(root_folder.get_sub_folder(folder))
        for subfolder in range(0, root_folder.get_sub_folder(folder).get_number_of_sub_folders()):
            folders.append(root_folder.get_sub_folder(folder).get_sub_folder(subfolder))

    return folders


def parseSentItems(folders):
    for folder in range(0, len(folders)):
        if (folders[folder].get_name() == "Posta inviata") or (folders[folder].get_name() == "Posta Inviata") \
                or (folders[folder].get_name() == "Sent items") or (folders[folder].get_name() == "Sent Items") \
                or (folders[folder].get_name() == "Sent Messages") \
                or (folders[folder].get_name() == "Gesendete Elemente") or (
                folders[folder].get_name() == "Messages envoyés"):
            return folders[folder]


def parseReceivedItems(folders):
    foldersToAnalyze = []
    root_folder = pstfile.get_root_folder()
    isroot = bool
    for folder in range(0, len(folders)):
        for root_subfolder in range(0, root_folder.get_number_of_sub_folders()):
            if folders[folder].get_name() == root_folder.get_sub_folder(root_subfolder).get_name():
                isroot = 1
                break
            else:
                isroot = 0
        if not isroot \
                and not (folders[folder].get_name() == "Posta inviata") \
                and not (folders[folder].get_name() == "Posta Inviata") \
                and not (folders[folder].get_name() == "Sent items") \
                and not (folders[folder].get_name() == "Sent Items") \
                and not (folders[folder].get_name() == "Sent Messages") \
                and not (folders[folder].get_name() == "Drafts") \
                and not (folders[folder].get_name() == "Gesendete Elemente") \
                and not (folders[folder].get_name() == "Messages envoyés"):
            foldersToAnalyze.append(folders[folder])
    return foldersToAnalyze


def lookForSender(sentItems):
    global processedSentItems
    for message in range(0, sentItems.get_number_of_sub_messages()):
        if len(sentItems.get_sub_message(message).get_sender_name()) > 1:
            if sentItems.get_sub_message(message).get_sender_name() in senders:
                senders[sentItems.get_sub_message(message).get_sender_name()] = \
                    senders[sentItems.get_sub_message(message).get_sender_name()] + 1
            else:
                senders[sentItems.get_sub_message(message).get_sender_name()] = 1
            processedSentItems = processedSentItems + 1
    for folder in range(0, sentItems.get_number_of_sub_folders()):
        lookForSender(sentItems.get_sub_folder(folder))


def getMaxSender(senders):
    if processedSentItems != 0:
        print(max(senders.items(), key=operator.itemgetter(1))[0], '-',
              max(senders.items(), key=operator.itemgetter(1))[1] / processedSentItems * 100, '%')
    else:
        print(max(senders.items(), key=operator.itemgetter(1))[0])


def lookForRecipient(receivedItems):
    global processedReceivedItems
    for message in range(0, receivedItems.get_number_of_sub_messages()):
        users = getRecipient(receivedItems.get_sub_message(message))
        if len(users) >= 1:
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
        to = re.findall(r"^To: \S*.*\d*@\S+.+\S+", message.transport_headers, re.MULTILINE)
        for recipient in range(0, len(to)):
            to[recipient] = parseaddr(to[recipient])[1]
        return to
    except TypeError:
        return []


def getMaxRecipient(recipients):
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

# Normal run, try to work with the sent Emails
try:
    processedSentItems = 0
    senders = dict()
    sentItems = parseSentItems(folders)
    lookForSender(sentItems)
    getMaxSender(senders)
except (AttributeError, ValueError):
    print("103 Error analyzing Sent Items")

# try to analyse received Emails too
try:
    processedReceivedItems = 0
    recipients = dict()
    receivedItems = parseReceivedItems(folders)
    for receivedItem in receivedItems:
        lookForRecipient(receivedItem)
    getMaxRecipient(recipients)

except (AttributeError, ValueError):
    print("104 Error analyzing Received Items")

# !!! Very important never forget to close the file!
pstfile.close()
