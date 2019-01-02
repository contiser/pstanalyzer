#  Copyright (c) 2019. This script has been written by Ch1r0n (Sergio Conti Rossini) All rights reserved.
#  All the rights for the libraries used in the script are reserved to their creators.

# libpff is needed, if you don't have it installed then you can install it by running "pip install libpff-python"

import sys
import pypff
import operator


def openPST():
    pstfile = pypff.file()

    # Check that the pst file path was provided otherwise exiting

    if len(sys.argv) != 2:
        print("Please enter the path of the file you want to analyze!")
        exit(1)
    else:
        try:
            pstfile.open(sys.argv[1])

        except OSError:
            print("An error has occurred while trying to open the file, exiting...")
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
        print('Parsing for Sent Items:' + folders[folder].get_name())
        if (folders[folder].get_name() == "Posta inviata") or (folders[folder].get_name() == "Posta Inviata") \
                or (folders[folder].get_name() == "Sent items") or (folders[folder].get_name() == "Sent Items"):
            return folders[folder]


def parseReceivedItems(folders):
    # If we weren't lucky, well... let's try to do the inverse with the inbox and the 'recipient' field

    for folder in range(0, len(folders)):
        print('Parsing for inbox:' + folders[folder].get_name())
        if (folders[folder].get_name() == "Posta in arrivo") or (folders[folder].get_name() == "Inbox"):
            return folders[folder]


def lookForSender(sentItems):
    senders = dict()
    for message in range(0, sentItems.get_number_of_sub_messages()):
        if sentItems.get_sub_message(message).get_sender_name() in senders:
            senders[sentItems.get_sub_message(message).get_sender_name()] = \
                senders[sentItems.get_sub_message(message).get_sender_name()] + 1
        else:
            senders[sentItems.get_sub_message(message).get_sender_name()] = 1
    return senders


def getMaxSender(senders):
    print('Utente', max(senders.items(), key=operator.itemgetter(1))[0], 'percentuale: ' \
          , max(senders.items(), key=operator.itemgetter(1))[1] / sentItems.get_number_of_sub_messages() * 100, '%')


def lookForRecipient(receivedItems):
    recipients = dict()
    for message in range(0, sentItems.get_number_of_sub_messages()):
        recipients[receivedItems.get_sub_message(message).get_sender_name()] = \
            recipients[receivedItems.get_sub_message(message).get_sender_name()] + 1

    return recipients


# End of function definitions
# Script starts here! :-)

pstfile = openPST()
folders = parseFolders(pstfile)
sentItems = parseSentItems(folders)
receivedItems = parseReceivedItems(folders)
senders = lookForSender(sentItems)
getMaxSender(senders)

# !!! Very important never forget to close the file!
pstfile.close()
